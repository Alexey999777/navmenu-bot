# handlers/user_handlers.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    get_sections_by_channel,
    get_posts_by_section,
    get_posts_by_subsection,
    get_subsections_by_section,
    get_channel_title,
    get_user_channels,
    asyncpg, DATABASE_URL
)
from config import OWNER_ID

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.text and len(message.text.split()) > 1:
        arg = message.text.split()[1]
        if arg.startswith("channel_"):
            try:
                channel_id = int(arg.split("_")[1])
                user_id = message.from_user.id
                # Проверяем доступ
                if channel_id not in await get_user_channels(user_id):
                    await message.answer("❌ У вас нет доступа к этому каналу.")
                    return

                sections = await get_sections_by_channel(channel_id)
                if not sections:
                    await message.answer("📭 В этом канале пока нет разделов.")
                    return

                builder = InlineKeyboardBuilder()
                for sec_id, title in sections:
                    builder.button(text=f"📁 {title}", callback_data=f"section_{sec_id}")
                builder.adjust(1)

                channel_title = await get_channel_title(channel_id) or "Канал"
                await message.answer(
                    f"<b>📂 {channel_title}</b>\n\nВыберите раздел:",
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
                return
            except (ValueError, IndexError):
                pass

    await show_main_menu(message)


@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)

    builder = InlineKeyboardBuilder()

    if channels:
        builder.button(text="➕ Добавить раздел", callback_data="cmd_add_section")
        builder.button(text="📎 Добавить пост", callback_data="cmd_add_post")
        builder.button(text="🔽 Добавить подраздел", callback_data="cmd_add_subsection")
        builder.button(text="🗑 Удалить пост", callback_data="cmd_delete_post")
        builder.button(text="🗑 Удалить подраздел", callback_data="cmd_delete_subsection")
        builder.button(text="🗑 Удалить раздел", callback_data="cmd_delete_section")
        builder.button(text="✏️ Редактировать", callback_data="cmd_edit")

    if user_id == OWNER_ID:
        builder.button(text="➕ Добавить канал", callback_data="cmd_add_channel")
        builder.button(text="➕ Добавить админа", callback_data="cmd_add_admin")
        builder.button(text="🗑 Удалить канал", callback_data="cmd_delete_channel")
        builder.button(text="🗑 Удалить админа", callback_data="cmd_delete_admin")

    builder.button(text="📚 Показать меню каналов", callback_data="show_channels")
    builder.adjust(2, repeat=True)

    if channels or user_id == OWNER_ID:
        await message.answer(
            "<b>⚙️ Админ-панель</b>\n\nВыберите действие:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    else:
        await message.answer("📭 Используйте меню из канала.")


# 🔥 ИСПРАВЛЕНО: вызывается только из message-обработчиков
async def show_channels_menu(message: types.Message):
    user_id = message.from_user.id
    channel_ids = await get_user_channels(user_id)

    if not channel_ids:
        await message.answer("📭 У вас нет доступа ни к одному каналу.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        if title:
            builder.button(text=f"📺 {title}", callback_data=f"show_menu_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())


# 🔥 НОВАЯ ФУНКЦИЯ: показать разделы конкретного канала (БЕЗ кнопки назад)
async def show_sections_menu(message: types.Message, channel_id: int):
    sections = await get_sections_by_channel(channel_id)
    if not sections:
        await message.answer("📭 В этом канале пока нет разделов.")
        return

    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(text=f"📁 {title}", callback_data=f"section_{sec_id}")
    builder.adjust(1)

    channel_title = await get_channel_title(channel_id) or "Канал"
    await message.answer(
        f"<b>📂 {channel_title}</b>\n\nВыберите раздел:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "show_channels")
async def callback_show_channels_menu(callback: types.CallbackQuery):
    # 🔥 ИСПРАВЛЕНО: используем callback.from_user.id
    user_id = callback.from_user.id
    channel_ids = await get_user_channels(user_id)

    if not channel_ids:
        await callback.answer("📭 У вас нет доступа ни к одному каналу.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        if title:
            builder.button(text=f"📺 {title}", callback_data=f"show_menu_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("show_menu_"))
async def show_channel_menu(callback: types.CallbackQuery):
    channel_id = int(callback.data.split("_")[2])
    await show_sections_menu(callback.message, channel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("section_"))
async def show_posts_in_section(callback: types.CallbackQuery):
    section_id = int(callback.data.split("_")[1])

    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT channel_id FROM sections WHERE id = $1", section_id)
    channel_id = row["channel_id"] if row else None
    await conn.close()

    if channel_id is None:
        await callback.answer("❌ Раздел не найден.", show_alert=True)
        return

    subsections = await get_subsections_by_section(section_id)
    direct_posts = await get_posts_by_section(section_id)

    builder = InlineKeyboardBuilder()
    for sub_id, title in subsections:
        builder.button(text=f"🔹 {title}", callback_data=f"subsection:{sub_id}:{section_id}")
    for post in direct_posts:
        _, _, _, _, url, custom_title, _ = post
        btn_text = custom_title or "📄 Пост"
        if url:
            builder.button(text=btn_text, url=url)

    builder.button(text="← Назад к разделам", callback_data=f"back_to_sections_{channel_id}")
    builder.adjust(1)
    await callback.message.edit_text("Выберите:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("subsection:"))
async def show_posts_in_subsection(callback: types.CallbackQuery):
    _, sub_id_str, section_id_str = callback.data.split(":")
    sub_id = int(sub_id_str)
    section_id = int(section_id_str)

    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT channel_id FROM sections WHERE id = $1", section_id)
    channel_id = row["channel_id"] if row else None
    await conn.close()

    posts = await get_posts_by_subsection(sub_id)
    if not posts:
        await callback.answer("📭 Постов нет.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for post in posts:
        _, _, _, _, url, custom_title, _ = post
        btn_text = custom_title or "📄 Пост"
        if url:
            builder.button(text=btn_text, url=url)

    builder.button(text="← Назад к разделу", callback_data=f"section_{section_id}")
    builder.button(text="↑ Наверх", callback_data=f"back_to_sections_{channel_id}")
    builder.adjust(1)
    await callback.message.edit_text("Посты:", reply_markup=builder.as_markup())


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    user_id = callback.from_user.id  # 🔥 Исправлено
    channels = await get_user_channels(user_id)

    if channels:
        # Показываем меню каналов
        builder = InlineKeyboardBuilder()
        for channel_id in channels:
            title = await get_channel_title(channel_id)
            if title:
                builder.button(text=f"📺 {title}", callback_data=f"show_menu_{channel_id}")
        builder.adjust(1)
        await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text("📭 Используйте меню из канала.")
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_sections_"))
async def back_to_sections(callback: types.CallbackQuery):
    channel_id = int(callback.data.split("_")[3])
    await show_sections_menu(callback.message, channel_id)
    await callback.answer()