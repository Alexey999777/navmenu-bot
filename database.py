# database.py
import asyncpg
from config import DATABASE_URL

# SQL для создания таблиц с исправленными связями и ограничениями
CREATE_TABLES_QUERY = """
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL UNIQUE,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    role TEXT DEFAULT 'moderator',
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE,
    UNIQUE (user_id, channel_id)
);

CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subsections (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    section_id INTEGER NOT NULL,
    subsection_id INTEGER,
    chat_id BIGINT NOT NULL,
    message_id INTEGER NOT NULL,
    url TEXT,
    title TEXT,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
    FOREIGN KEY (subsection_id) REFERENCES subsections(id) ON DELETE SET NULL
);
"""


async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(CREATE_TABLES_QUERY)
    await conn.close()
    print("✅ База данных PostgreSQL инициализирована")


# === Каналы ===
async def add_channel(channel_id: int, title: str):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO channels (channel_id, title) VALUES ($1, $2)",
            channel_id, title
        )
        return True
    except asyncpg.UniqueViolationError:
        return False
    finally:
        await conn.close()


async def get_channel_title(channel_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT title FROM channels WHERE channel_id = $1", channel_id)
    await conn.close()
    return row["title"] if row else None


async def get_channel_by_id(channel_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM channels WHERE channel_id = $1", channel_id)
    await conn.close()
    return row


async def get_channels_count():
    conn = await asyncpg.connect(DATABASE_URL)
    count = await conn.fetchval("SELECT COUNT(*) FROM channels")
    await conn.close()
    return count


async def get_all_channels():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT channel_id FROM channels")
    await conn.close()
    return [row["channel_id"] for row in rows]


# === Администраторы ===
async def add_admin(user_id: int, channel_id: int, role: str = "moderator"):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO admins (user_id, channel_id, role) VALUES ($1, $2, $3)",
            user_id, channel_id, role
        )
        return True
    except Exception:
        return False
    finally:
        await conn.close()


async def is_user_channel_admin(user_id: int, channel_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow(
        "SELECT role FROM admins WHERE user_id = $1 AND channel_id = $2",
        user_id, channel_id
    )
    await conn.close()
    return row is not None


# 🔥 ИСПРАВЛЕНО: теперь возвращает ТОЛЬКО существующие каналы
async def get_user_channels(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("""
        SELECT a.channel_id 
        FROM admins a
        JOIN channels c ON a.channel_id = c.channel_id
        WHERE a.user_id = $1
    """, user_id)
    await conn.close()
    return [row["channel_id"] for row in rows]


# === Разделы ===
async def add_section(channel_id: int, title: str):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO sections (channel_id, title) VALUES ($1, $2)",
            channel_id, title
        )
        return True
    except Exception:
        return False
    finally:
        await conn.close()


async def get_sections_by_channel(channel_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(
        "SELECT id, title FROM sections WHERE channel_id = $1",
        channel_id
    )
    await conn.close()
    return [(row["id"], row["title"]) for row in rows]


# === Подразделы ===
async def add_subsection(section_id: int, title: str):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO subsections (section_id, title) VALUES ($1, $2)",
            section_id, title
        )
        return True
    except Exception:
        return False
    finally:
        await conn.close()


async def get_subsections_by_section(section_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(
        "SELECT id, title FROM subsections WHERE section_id = $1",
        section_id
    )
    await conn.close()
    return [(row["id"], row["title"]) for row in rows]


# === Посты ===
async def add_post(channel_id: int, section_id: int, subsection_id: int, chat_id: int, message_id: int, url: str, title: str = None):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        """INSERT INTO posts (channel_id, section_id, subsection_id, chat_id, message_id, url, title)
           VALUES ($1, $2, $3, $4, $5, $6, $7)""",
        channel_id, section_id, subsection_id, chat_id, message_id, url, title
    )
    await conn.close()


async def get_posts_by_section(section_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(
        """SELECT id, section_id, chat_id, message_id, url, title, deleted
           FROM posts
           WHERE section_id = $1 AND subsection_id IS NULL AND deleted = FALSE""",
        section_id
    )
    await conn.close()
    return [(r["id"], r["section_id"], r["chat_id"], r["message_id"], r["url"], r["title"], r["deleted"]) for r in rows]


async def get_posts_by_subsection(subsection_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(
        """SELECT id, section_id, chat_id, message_id, url, title, deleted
           FROM posts
           WHERE subsection_id = $1 AND deleted = FALSE""",
        subsection_id
    )
    await conn.close()
    return [(r["id"], r["section_id"], r["chat_id"], r["message_id"], r["url"], r["title"], r["deleted"]) for r in rows]


async def delete_post(post_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("UPDATE posts SET deleted = TRUE WHERE id = $1", post_id)
    await conn.close()


# === Проверка дубликата ===
async def post_exists(chat_id: int, message_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow(
        "SELECT 1 FROM posts WHERE chat_id = $1 AND message_id = $2 AND deleted = FALSE",
        chat_id, message_id
    )
    await conn.close()
    return row is not None