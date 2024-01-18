import asyncio
import os
import string
import traceback
import datetime
import random

import aiosqlite
import httpx
import logging
from config import settings
import ua_generator
from img_scrapper.pixeldrain.db import check_id, insert_into_database, create_table

logger = logging.getLogger('img-scraper')

NUM_THREADS = settings.PIXELDRAIN_MAX_THREADS  # Замените на желаемое количество потоков


async def create_session():
    try:
        useragent = ua_generator.generate(device='desktop', browser='chrome')
        headers = {
            'accept': 'application/json',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'host': f'{settings.PIXELDRAIN_DOMAIN}',
            'user-agent': f'{useragent}'
        }

        # Создание сессии с возможностью подделки TLS
        session = httpx.AsyncClient(
            headers=headers, verify=settings.PROXY_VERIFY, proxies=settings.PROXY_ROTATE
        )
        logger.info(f"Session created successfully \n{str(headers)}\n{settings.PROXY_ROTATE}")

        return session
    except Exception as error:
        logger.error(f"Error creating session \n{str(error)}")
        raise


async def parse_and_save_images(session, unique_id):
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            url = f"{settings.PIXELDRAIN_URL_TYPE}{settings.PIXELDRAIN_DOMAIN}/api/file/{unique_id}"
            response = await session.get(url, timeout=15.0)

            if response.status_code == 200:
                logger.info(f"Successful response received")
                file_path = os.path.join(settings.IMG_PATH, 'pixeldrain', unique_id)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                    return file_path, True, False
            elif response.status_code == 404:
                return None, False, False
            elif response.status_code == 403:
                return None, False, True
            elif "Cannot find any proxy" in response.text:
                message = "Cannot find any proxy : {response.text}"
                print(message)
                return None, False, True

            else:
                raise Exception(f"Unexpected status code: {response.status_code}\n{response.text}")


        except Exception as error:
            logger.error(f"Unexpected error in get_session_token \n{str(error)}")
            logger.error(traceback.format_exc())

    logger.error(f"Max retries exceeded, failed to parse")
    return None, False, True


async def generate_unique_id():
    result = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    print(result)
    return result



async def main():
    while True:
        try:
            print("DB Path: {}".format(settings.DB_PATH))
            async with aiosqlite.connect(settings.DB_PATH) as db:
                # Создание таблицы
                await create_table(db)

                # Создаем список задач, каждая из которых выполняет одну итерацию
                tasks = []
                for _ in range(NUM_THREADS):  # Замените NUM_THREADS на желаемое количество потоков
                    new_id = await generate_unique_id()
                    existing_data = await check_id(db)
                    if existing_data is not None:
                        while new_id in existing_data:
                            new_id = generate_unique_id()

                    session = await create_session()
                    task = parse_and_save_images(session, new_id)
                    tasks.append(task)

                # Запускаем задачи параллельно
                results = await asyncio.gather(*tasks)

                for result in results:
                    image_path, is_valid, is_captcha = result
                    if is_valid:
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        await insert_into_database(db, new_id, image_path, current_date, 1)
                        print("Data successfully parsed and saved.")
                    else:
                        if is_captcha:
                            print("403 Error: file_rate_limited_captcha_required")
                        else:
                            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            print("404 Error: Image not found.")
                            await insert_into_database(db, new_id, '', current_date, 0)

        except Exception as error:
            print(f"Unexpected error: {str(error)}")
            print(traceback.format_exc())

        # Пауза между итерациями цикла (например, 10 секунд)
        await asyncio.sleep(settings.PIXELDRAIN_DELAY_SECONDS)


async def start_pixeldrain():
    print(f"go")

    task = asyncio.create_task(main())
    await task
