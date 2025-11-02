import asyncpg, asyncio
import os, logging
from dotenv import load_dotenv

load_dotenv()
pool = None

async def init_db():
    global pool

    try:
        # Подключение с параметрами
        pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

        #Создание таблицы если ее нет:
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    user_message_id BIGINT NOT NULL,
                    photo_id TEXT,
                    caption TEXT,
                    status VARCHAR(20) DEFAULT 'pending'            
                )
            ''')
        logging.info("Создание БД успешно ✅")
    except:
        logging.exception("Инициализация БД ошибка ⛔️")


async def save_post(user_id: str, photo_id: str, caption: str = None, user_message_id: str = None):
    try:
        async with pool.acquire() as conn:
            post_id = await conn.fetchval(
                "INSERT INTO posts (user_id, caption, photo_id, user_message_id) VALUES ($1, $2, $3, $4) RETURNING id",
                user_id, caption, photo_id, user_message_id
            )
        logging.info("Сохранение сообщения в БД успешно ✅")
        return post_id
    except:
        logging.exception("Сохранение сообщения в БД ошибка ⛔️")



async def approvedPost(post_id):
    try:
        async with pool.acquire() as conn:
            post = await conn.fetchrow("SELECT * FROM posts WHERE id = $1", post_id)
            if post and post["status"] == "pending":
                await conn.execute(f"UPDATE posts SET status = 'approved' WHERE id = $1", post_id)
        logging.info("Обновление статуса сообщения в БД успешно ✅")
        return post
    except:
        logging.exception("Обновление статуса сообщения в БД ошибка ⛔️")


async def rejectedPost(post_id):
    try:
        async with pool.acquire() as conn:
            post = await conn.fetchrow("SELECT * FROM posts WHERE id = $1", post_id)
            if post and post["status"] == "pending":
                await conn.execute(f"UPDATE posts SET status = 'rejected' WHERE id = $1", post_id)
        logging.info("Обновление статуса сообщения в БД успешно ✅")
        return post
    except:
        logging.exception("Обновление статуса сообщения в БД ошибка ⛔️")