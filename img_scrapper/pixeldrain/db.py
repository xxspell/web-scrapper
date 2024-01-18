import aiosqlite
import asyncio



async def create_table(conn):
    query = '''
    CREATE TABLE IF NOT EXISTS pixeldrain_img (id TEXT PRIMARY KEY, path TEXT, date_parsed TEXT, valid INTEGER);
    '''
    await conn.execute(query)
    await conn.commit()

async def insert_into_database(conn, id, path, date_parsed, valid):
    try:


        await conn.execute('INSERT INTO pixeldrain_img VALUES (?, ?, ?, ?)', (id, path, date_parsed, valid))
        await conn.commit()

    except Exception as error:
        print(error)


async def check_id(db):
    try:

        async with db.execute('SELECT id FROM pixeldrain_img') as cursor:
            return await cursor.fetchall()

    except Exception as error:
        print(error)