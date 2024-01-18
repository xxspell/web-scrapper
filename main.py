import configparser
import asyncio
from img_scrapper.pixeldrain.run import start_pixeldrain
import time
import logging
logger = logging.getLogger(__name__)

async def pixeldrain():
    print("Running Function 1")
    await start_pixeldrain()



async def function2():
    print("Running Function 2")

async def function3():

    print("Running Function 3")

async def main():
    # Чтение конфигурационного файла
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    # Перечень функций для проверки
    functions_to_check = ['pixeldrain', 'function2', 'function3']

    # Проверка наличия секции и опций в INI-файле
    tasks = []
    for func in functions_to_check:
        if 'Functions' in config and func in config['Functions']:
            if config['Functions'].getboolean(func):
                task = asyncio.create_task(globals()[func]())
                tasks.append(task)

    # Запуск всех функций асинхронно
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())