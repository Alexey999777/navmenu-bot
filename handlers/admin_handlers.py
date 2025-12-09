# handlers/admin_handlers.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    add_channel,
    get_channel_title,
    add_admin,
    add_section,
    get_sections_by_channel,
    add_subsection,
    get_subsections_by_section,
    get_posts_by_section,
    get_posts_by_subsection,
    delete_post,
    post_exists,
    add_post,
    get_user_channels,
    get_channels_count,
    get_all_channels,
    is_user_channel_admin,
    get_channel_by_id
)
from config import MAX_CHANNELS, OWNER_ID, DATABASE_URL
from utils.check_admin import require_channel_admin
import asyncpg
from handlers.user_handlers import show_main_menu  # ← для автоматического меню

router = Router()


# === FSM: Создание ===
class CreateSection(StatesGroup):
    waiting_for_channel = State()
    waiting_for_title = State()


class CreateSubsection(StatesGroup):
    choosing_channel = State()
    choosing_section = State()
    waiting_for_title = State()


class AddPost(StatesGroup):
    choosing_channel = State()
    choosing_section = State()
    choosing_subsection = State()
    waiting_for_forward = State()
    waiting_for_title = State()


# === FSM: Удаление ===
class DeletePost(StatesGroup):
    choosing_channel = State()
    choosing_section = State()
    choosing_post = State()
    confirm = State()


class DeleteSubsection(StatesGroup):
    choosing_channel = State()
    choosing_section = State()
    choosing_subsection = State()
    confirm = State()


class DeleteSectionState(StatesGroup):
    choosing_channel = State()
    choosing_section = State()
    confirm = State()


class DeleteChannelState(StatesGroup):
    choosing_channel = State()
    confirm = State()


# === FSM: Управление админами ===
class AddAdminState(StatesGroup):
    choosing_channel = State()
    entering_user_id = State()
    entering_role = State()


class DeleteAdminState(StatesGroup):
    choosing_channel = State()
    choosing_admin = State()
    confirm = State()


# === FSM: Редактирование ===
class EditItem(StatesGroup):
    choosing_channel = State()
    choosing_type = State()
    choosing_item = State()
    entering_new_title = State()


# === /add_channel ===
@router.message(Command("add_channel"))
async def cmd_add_channel(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Только владелец может добавлять каналы.")
        return

    try:
        count = await get_channels_count()
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        return

    if count >= MAX_CHANNELS:
        await message.answer(f"❌ Достигнут лимит ({MAX_CHANNELS}) каналов.")
        return

    await message.answer("Введите ID канала (в формате -100...):")
    await state.set_state(CreateSection.waiting_for_channel)


@router.message(CreateSection.waiting_for_channel, F.text)
async def process_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Неверный ID канала. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    try:
        chat = await message.bot.get_chat(channel_id)
    except Exception:
        await message.answer("❌ Канал не найден или бот не является его администратором. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    if await get_channel_title(channel_id):
        title = await get_channel_title(channel_id)
        await message.answer(f"❌ Канал «{title}» уже добавлен. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    try:
        await add_channel(channel_id, chat.title)
        await add_admin(OWNER_ID, channel_id, "owner")
        await message.answer(f"✅ Канал «{chat.title}» добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await state.clear()
        await show_main_menu(message)


# === /add_admin ===
@router.message(Command("add_admin"))
async def cmd_add_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Только владелец может добавлять админов.")
        return
    await message.answer("Введите ID канала:")
    await state.set_state(AddAdminState.choosing_channel)


@router.message(AddAdminState.choosing_channel, F.text)
async def add_admin_ask_user(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Неверный ID канала. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    if not await get_channel_title(channel_id):
        await message.answer("❌ Канал не найден в базе. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    await state.update_data(channel_id=channel_id)
    await message.answer("Введите ID пользователя:")
    await state.set_state(AddAdminState.entering_user_id)


@router.message(AddAdminState.entering_user_id, F.text)
async def add_admin_ask_role(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Неверный ID пользователя. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    await state.update_data(user_id=user_id)
    await message.answer("Введите роль (moderator, owner):")
    await state.set_state(AddAdminState.entering_role)


@router.message(AddAdminState.entering_role, F.text)
async def add_admin_final(message: types.Message, state: FSMContext):
    role = message.text.strip()
    if role not in ["moderator", "owner"]:
        await message.answer("❌ Роль должна быть 'moderator' или 'owner'. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    data = await state.get_data()
    if await is_user_channel_admin(data["user_id"], data["channel_id"]):
        await message.answer("❌ Этот пользователь уже является админом канала. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    await add_admin(data["user_id"], data["channel_id"], role)
    await message.answer(f"✅ Пользователь {data['user_id']} добавлен как {role}.")
    await state.clear()
    await show_main_menu(message)


# === /delete_admin ===
@router.message(Command("delete_admin"))
async def cmd_delete_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Только владелец может удалять админов.")
        return

    channel_ids = await get_all_channels()
    if not channel_ids:
        await message.answer("📭 Нет каналов.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"deladmin_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeleteAdminState.choosing_channel)


@router.callback_query(DeleteAdminState.choosing_channel, F.data.startswith("deladmin_channel_"))
async def choose_admin_to_delete(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    await state.update_data(channel_id=channel_id)

    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT user_id, role FROM admins WHERE channel_id = $1", channel_id)
    await conn.close()

    if not rows:
        await callback.answer("📭 В этом канале нет админов.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for row in rows:
        user_id = row["user_id"]
        role = row["role"]
        builder.button(text=f"👤 {user_id} ({role})", callback_data=f"deladmin_user_{user_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите админа для удаления:", reply_markup=builder.as_markup())
    await state.set_state(DeleteAdminState.choosing_admin)


@router.callback_query(DeleteAdminState.choosing_admin, F.data.startswith("deladmin_user_"))
async def confirm_delete_admin(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[2])
    await state.update_data(target_user_id=user_id)
    await callback.message.edit_text("Вы уверены? Напишите «да» для подтверждения.")
    await state.set_state(DeleteAdminState.confirm)


@router.message(DeleteAdminState.confirm, F.text)
async def execute_delete_admin(message: types.Message, state: FSMContext):
    if message.text.lower().strip() in ("да", "yes", "удалить"):
        data = await state.get_data()
        channel_id = data["channel_id"]
        user_id = data["target_user_id"]

        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(
            "DELETE FROM admins WHERE channel_id = $1 AND user_id = $2",
            channel_id, user_id
        )
        await conn.close()
        await message.answer("✅ Админ удалён.")
    else:
        await message.answer("❌ Отменено.")
    await state.clear()
    await show_main_menu(message)


# === /add_section ===
@router.message(Command("add_section"))
async def cmd_add_section(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"section_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(CreateSection.waiting_for_channel)


@router.callback_query(F.data.startswith("section_channel_"))
async def choose_channel_for_section(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    await callback.message.edit_text("Введите название раздела:")
    await state.set_state(CreateSection.waiting_for_title)


@router.message(CreateSection.waiting_for_title, F.text)
async def process_new_section(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_id = data.get("channel_id")
    if channel_id is None:
        await message.answer("❌ Ошибка: канал не выбран. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    title = message.text.strip()
    if not title or len(title) > 50:
        await message.answer("❌ Название должно быть от 1 до 50 символов. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    if await add_section(channel_id, title):
        await message.answer(f"✅ Раздел «{title}» создан!")
    else:
        await message.answer("❌ Ошибка при создании раздела.")
    await state.clear()
    await show_main_menu(message)


# === /add_subsection ===
@router.message(Command("add_subsection"))
async def cmd_add_subsection(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"sub_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(CreateSubsection.choosing_channel)


@router.callback_query(F.data.startswith("sub_channel_"))
async def choose_channel_for_subsection(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    sections = await get_sections_by_channel(channel_id)
    if not sections:
        await callback.answer("❌ Нет разделов.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(text=f"📁 {title}", callback_data=f"sub_section_{sec_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите раздел:", reply_markup=builder.as_markup())
    await state.set_state(CreateSubsection.choosing_section)


@router.callback_query(F.data.startswith("sub_section_"))
async def enter_subsection_title(callback: types.CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[2])
    await state.update_data(section_id=section_id)
    await callback.message.edit_text("Введите название подраздела:")
    await state.set_state(CreateSubsection.waiting_for_title)


@router.message(CreateSubsection.waiting_for_title, F.text)
async def create_subsection_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    section_id = data.get("section_id")
    if section_id is None:
        await message.answer("❌ Ошибка: раздел не выбран. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    title = message.text.strip()
    if not title or len(title) > 50:
        await message.answer("❌ Название должно быть от 1 до 50 символов. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    if await add_subsection(section_id, title):
        await message.answer(f"✅ Подраздел «{title}» добавлен!")
    else:
        await message.answer("❌ Ошибка при создании подраздела.")
    await state.clear()
    await show_main_menu(message)


# === /add_post ===
@router.message(Command("add_post"))
async def cmd_add_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"addpost_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(AddPost.choosing_channel)


@router.callback_query(F.data.startswith("addpost_channel_"))
async def choose_channel_for_post(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    sections = await get_sections_by_channel(channel_id)
    if not sections:
        await callback.answer("❌ Нет разделов.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(text=f"📁 {title}", callback_data=f"addpost_section_{sec_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите раздел:", reply_markup=builder.as_markup())
    await state.set_state(AddPost.choosing_section)


@router.callback_query(AddPost.choosing_section, F.data.startswith("addpost_section_"))
async def choose_subsection_or_skip(callback: types.CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[2])
    await state.update_data(section_id=section_id)

    subsections = await get_subsections_by_section(section_id)
    if subsections:
        builder = InlineKeyboardBuilder()
        for sub_id, title in subsections:
            builder.button(text=f"🔹 {title}", callback_data=f"addpost_subsection_{sub_id}")
        builder.button(text="📥 Без подраздела", callback_data="addpost_subsection_0")
        builder.adjust(1)
        await callback.message.edit_text("Выберите подраздел:", reply_markup=builder.as_markup())
        await state.set_state(AddPost.choosing_subsection)
    else:
        await callback.message.edit_text("Перешлите пост из канала:")
        await state.set_state(AddPost.waiting_for_forward)


@router.callback_query(AddPost.choosing_subsection, F.data.startswith("addpost_subsection_"))
async def choose_subsection_final(callback: types.CallbackQuery, state: FSMContext):
    sub_id_str = callback.data.split("_")[2]
    subsection_id = int(sub_id_str) if sub_id_str != "0" else None
    await state.update_data(subsection_id=subsection_id)
    await callback.message.edit_text("Перешлите пост из канала:")
    await state.set_state(AddPost.waiting_for_forward)


@router.message(AddPost.waiting_for_forward, F.forward_from_chat)
async def process_forwarded_post(message: types.Message, state: FSMContext):
    if not message.forward_from_chat or not hasattr(message, 'forward_from_message_id'):
        await message.answer("❌ Перешлите пост из канала. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    chat_id = message.forward_from_chat.id
    message_id = message.forward_from_message_id

    if not str(chat_id).startswith("-100"):
        await message.answer("❌ Это не пост из канала. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    if await post_exists(chat_id, message_id):
        await message.answer("❌ Этот пост уже добавлен. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    data = await state.get_data()
    channel_id = data.get("channel_id")
    section_id = data.get("section_id")
    subsection_id = data.get("subsection_id")

    if channel_id is None or section_id is None:
        await message.answer("❌ Ошибка: данные не сохранены. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    # Генерация URL
    if str(chat_id).startswith("-100"):
        real_id = str(chat_id)[4:]
        url = f"https://t.me/c/{real_id}/{message_id}"
    else:
        username = "public_channel"
        url = f"https://t.me/{username}/{message_id}"

    await state.update_data(
        chat_id=chat_id,
        message_id=message_id,
        url=url
    )
    await message.answer("Введите название поста:")
    await state.set_state(AddPost.waiting_for_title)


@router.message(AddPost.waiting_for_title, F.text)
async def save_post_with_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = message.text.strip()

    if not title:
        await message.answer("❌ Название не может быть пустым. Попробуйте снова:")
        return

    await add_post(
        channel_id=data["channel_id"],
        section_id=data["section_id"],
        subsection_id=data.get("subsection_id"),
        chat_id=data["chat_id"],
        message_id=data["message_id"],
        url=data["url"],
        title=title
    )
    await message.answer("✅ Пост добавлен!")
    await state.clear()
    await show_main_menu(message)


# === Вспомогательная функция для получения всех постов в разделе (включая подразделы) ===
async def get_posts_by_subsection_from_section(section_id: int):
    subsections = await get_subsections_by_section(section_id)
    all_posts = []
    for sub_id, _ in subsections:
        posts = await get_posts_by_subsection(sub_id)
        all_posts.extend(posts)
    return all_posts


# === /delete_post ===
@router.message(Command("delete_post"))
async def cmd_delete_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"delpost_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeletePost.choosing_channel)


@router.callback_query(F.data.startswith("delpost_channel_"))
async def choose_channel_for_delete_post(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    sections = await get_sections_by_channel(channel_id)
    if not sections:
        await callback.answer("❌ Нет разделов.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(text=f"📁 {title}", callback_data=f"delpost_section_{sec_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите раздел:", reply_markup=builder.as_markup())
    await state.set_state(DeletePost.choosing_section)


@router.callback_query(DeletePost.choosing_section, F.data.startswith("delpost_section_"))
async def choose_post_to_delete(callback: types.CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[2])
    await state.update_data(section_id=section_id)

    posts = await get_posts_by_section(section_id)
    posts.extend(await get_posts_by_subsection_from_section(section_id))

    if not posts:
        await callback.answer("📭 Постов нет.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for post in posts:
        post_id, _, _, _, url, title, _ = post
        btn_text = (title or "Пост")[:20]
        builder.button(text=btn_text, callback_data=f"delpost_post_{post_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите пост для удаления:", reply_markup=builder.as_markup())
    await state.set_state(DeletePost.choosing_post)


@router.callback_query(DeletePost.choosing_post, F.data.startswith("delpost_post_"))
async def confirm_delete_post(callback: types.CallbackQuery, state: FSMContext):
    post_id = int(callback.data.split("_")[2])
    await state.update_data(post_id=post_id)
    await callback.message.edit_text("Вы уверены? Напишите «да» для подтверждения.")
    await state.set_state(DeletePost.confirm)


@router.message(DeletePost.confirm, F.text)
async def execute_delete_post(message: types.Message, state: FSMContext):
    if message.text.lower() in ("да", "yes", "удалить"):
        data = await state.get_data()
        await delete_post(data["post_id"])
        await message.answer("✅ Пост удалён.")
    else:
        await message.answer("❌ Отменено.")
    await state.clear()
    await show_main_menu(message)


# === /delete_subsection ===
@router.message(Command("delete_subsection"))
async def cmd_delete_subsection(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"delsub_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSubsection.choosing_channel)


@router.callback_query(F.data.startswith("delsub_channel_"))
async def choose_channel_for_del_sub(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    sections = await get_sections_by_channel(channel_id)
    if not sections:
        await callback.answer("❌ Нет разделов.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(text=f"📁 {title}", callback_data=f"delsub_section_{sec_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите раздел:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSubsection.choosing_section)


@router.callback_query(DeleteSubsection.choosing_section, F.data.startswith("delsub_section_"))
async def choose_subsection_to_delete(callback: types.CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[2])
    await state.update_data(section_id=section_id)
    subsections = await get_subsections_by_section(section_id)
    if not subsections:
        await callback.answer("📭 Подразделов нет.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for sub_id, title in subsections:
        builder.button(text=f"🔹 {title}", callback_data=f"delsub_sub_{sub_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите подраздел:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSubsection.choosing_subsection)


@router.callback_query(DeleteSubsection.choosing_subsection, F.data.startswith("delsub_sub_"))
async def confirm_delete_subsection(callback: types.CallbackQuery, state: FSMContext):
    sub_id = int(callback.data.split("_")[2])
    await state.update_data(sub_id=sub_id)
    await callback.message.edit_text("Вы уверены? Напишите «да» для подтверждения.")
    await state.set_state(DeleteSubsection.confirm)


@router.message(DeleteSubsection.confirm, F.text)
async def execute_delete_subsection(message: types.Message, state: FSMContext):
    if message.text.lower() in ("да", "yes", "удалить"):
        data = await state.get_data()
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("DELETE FROM subsections WHERE id = $1", data["sub_id"])
        await conn.close()
        await message.answer("✅ Подраздел удалён.")
    else:
        await message.answer("❌ Отменено.")
    await state.clear()
    await show_main_menu(message)


# === /delete_section ===
@router.message(Command("delete_section"))
async def cmd_delete_section(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"delsec_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSectionState.choosing_channel)


@router.callback_query(F.data.startswith("delsec_channel_"))
async def choose_channel_for_del_sec(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    sections = await get_sections_by_channel(channel_id)
    if not sections:
        await callback.answer("❌ Нет разделов.", show_alert=True)
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(text=f"📁 {title}", callback_data=f"delsec_section_{sec_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите раздел:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSectionState.choosing_section)


@router.callback_query(DeleteSectionState.choosing_section, F.data.startswith("delsec_section_"))
async def confirm_delete_section(callback: types.CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[2])
    await state.update_data(section_id=section_id)
    await callback.message.edit_text("Вы уверены? Напишите «да» для подтверждения.")
    await state.set_state(DeleteSectionState.confirm)


@router.message(DeleteSectionState.confirm, F.text)
async def execute_delete_section(message: types.Message, state: FSMContext):
    if message.text.lower() in ("да", "yes", "удалить"):
        data = await state.get_data()
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("DELETE FROM sections WHERE id = $1", data["section_id"])
        await conn.close()
        await message.answer("✅ Раздел удалён.")
    else:
        await message.answer("❌ Отменено.")
    await state.clear()
    await show_main_menu(message)


# === /delete_channel ===
@router.message(Command("delete_channel"))
async def cmd_delete_channel(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Только владелец может удалять каналы.")
        return

    channel_ids = await get_all_channels()
    if not channel_ids:
        await message.answer("📭 Нет каналов.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"del_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал для удаления:", reply_markup=builder.as_markup())
    await state.set_state(DeleteChannelState.choosing_channel)


@router.callback_query(DeleteChannelState.choosing_channel, F.data.startswith("del_channel_"))
async def confirm_delete_channel(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    await state.update_data(channel_id=channel_id)
    await callback.message.edit_text(
        "Вы уверены? Напишите «да» для подтверждения."
    )
    await state.set_state(DeleteChannelState.confirm)
    await callback.answer()


@router.message(DeleteChannelState.confirm, F.text)
async def execute_delete_channel(message: types.Message, state: FSMContext):
    if message.text.lower().strip() in ("да", "yes", "удалить"):
        data = await state.get_data()
        channel_id = data["channel_id"]

        conn = await asyncpg.connect(DATABASE_URL)
        try:
            await conn.execute("DELETE FROM channels WHERE channel_id = $1", channel_id)
            await message.answer("✅ Канал удалён.")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
        finally:
            await conn.close()
    else:
        await message.answer("❌ Отменено.")

    await state.clear()
    await show_main_menu(message)


# === /edit ===
@router.message(Command("edit"))
async def cmd_edit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await message.answer("❌ У вас нет доступа к каналам.")
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"edit_channel_{channel_id}")
    builder.adjust(1)

    await message.answer("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(EditItem.choosing_channel)


@router.callback_query(EditItem.choosing_channel, F.data.startswith("edit_channel_"))
async def edit_choose_channel(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    if not await require_channel_admin(callback.from_user.id, channel_id):
        await callback.answer("❌ Нет прав.", show_alert=True)
        return

    await state.update_data(channel_id=channel_id)
    builder = InlineKeyboardBuilder()
    builder.button(text="📁 Раздел", callback_data="edit_type:section")
    builder.button(text="🔹 Подраздел", callback_data="edit_type:subsection")
    builder.button(text="📄 Пост", callback_data="edit_type:post")
    builder.adjust(1)

    await callback.message.edit_text("Что отредактировать?", reply_markup=builder.as_markup())
    await state.set_state(EditItem.choosing_type)


@router.callback_query(EditItem.choosing_type, F.data.startswith("edit_type:"))
async def edit_choose_item(callback: types.CallbackQuery, state: FSMContext):
    item_type = callback.data.split(":")[1]
    await state.update_data(item_type=item_type)

    data = await state.get_data()
    channel_id = data["channel_id"]

    builder = InlineKeyboardBuilder()
    if item_type == "section":
        items = await get_sections_by_channel(channel_id)
        for sec_id, title in items:
            builder.button(text=f"📁 {title}", callback_data=f"edit_item_{sec_id}")
    elif item_type == "subsection":
        sections = await get_sections_by_channel(channel_id)
        for sec_id, _ in sections:
            subs = await get_subsections_by_section(sec_id)
            for sub_id, title in subs:
                builder.button(text=f"🔹 {title}", callback_data=f"edit_item_{sub_id}")
    elif item_type == "post":
        sections = await get_sections_by_channel(channel_id)
        for sec_id, _ in sections:
            posts = await get_posts_by_section(sec_id)
            posts.extend(await get_posts_by_subsection_from_section(sec_id))
            for post in posts:
                post_id, _, _, _, _, title, _ = post
                btn_text = (title or "Пост")[:20]
                builder.button(text=btn_text, callback_data=f"edit_item_{post_id}")

    if not builder.buttons:
        await callback.answer("📭 Нет элементов.", show_alert=True)
        await state.clear()
        return

    builder.adjust(1)
    await callback.message.edit_text("Выберите элемент:", reply_markup=builder.as_markup())
    await state.set_state(EditItem.choosing_item)


@router.callback_query(EditItem.choosing_item, F.data.startswith("edit_item_"))
async def edit_enter_new_title(callback: types.CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[2])
    await state.update_data(item_id=item_id)
    await callback.message.edit_text("Введите новый заголовок:")
    await state.set_state(EditItem.entering_new_title)


@router.message(EditItem.entering_new_title, F.text)
async def execute_edit_title(message: types.Message, state: FSMContext):
    new_title = message.text.strip()
    if len(new_title) > 100:
        await message.answer("❌ Слишком длинный заголовок (макс. 100). Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    data = await state.get_data()
    item_type = data.get("item_type")
    item_id = data.get("item_id")
    if not item_type or not item_id:
        await message.answer("❌ Ошибка данных. Операция отменена.")
        await state.clear()
        await show_main_menu(message)
        return

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        if item_type == "section":
            await conn.execute("UPDATE sections SET title = $1 WHERE id = $2", new_title, item_id)
        elif item_type == "subsection":
            await conn.execute("UPDATE subsections SET title = $1 WHERE id = $2", new_title, item_id)
        elif item_type == "post":
            await conn.execute("UPDATE posts SET title = $1 WHERE id = $2", new_title, item_id)
        await message.answer("✅ Заголовок обновлён.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await conn.close()
        await state.clear()
        await show_main_menu(message)


# === Обработка админ-кнопок меню (callback) ===

@router.callback_query(F.data == "cmd_add_channel")
async def menu_add_channel(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Только владелец.", show_alert=True)
        return

    try:
        count = await get_channels_count()
        if count >= MAX_CHANNELS:
            await callback.answer(f"❌ Лимит ({MAX_CHANNELS}) каналов достигнут.", show_alert=True)
            return
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
        return

    await callback.message.edit_text("Введите ID канала (в формате -100...):")
    await state.set_state(CreateSection.waiting_for_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_add_admin")
async def menu_add_admin(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Только владелец.", show_alert=True)
        return

    channel_ids = await get_all_channels()
    if not channel_ids:
        await callback.answer("📭 Нет каналов.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"addadmin_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(AddAdminState.choosing_channel)
    await callback.answer()


@router.callback_query(AddAdminState.choosing_channel, F.data.startswith("addadmin_channel_"))
async def menu_add_admin_step2(callback: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])
    await state.update_data(channel_id=channel_id)
    await callback.message.edit_text("Введите ID пользователя:")
    await state.set_state(AddAdminState.entering_user_id)
    await callback.answer()


@router.callback_query(F.data == "cmd_delete_admin")
async def menu_delete_admin(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Только владелец.", show_alert=True)
        return

    channel_ids = await get_all_channels()
    if not channel_ids:
        await callback.answer("📭 Нет каналов.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"deladmin_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeleteAdminState.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_add_section")
async def admin_add_section(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"section_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(CreateSection.waiting_for_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_add_subsection")
async def admin_add_subsection(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"sub_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(CreateSubsection.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_add_post")
async def admin_add_post(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"addpost_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(AddPost.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_delete_post")
async def admin_delete_post(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"delpost_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeletePost.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_delete_subsection")
async def admin_delete_subsection(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"delsub_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSubsection.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_delete_section")
async def admin_delete_section(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"delsec_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(DeleteSectionState.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_edit")
async def admin_edit(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channels = await get_user_channels(user_id)
    if not channels:
        await callback.answer("❌ У вас нет доступа к каналам.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channels:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"edit_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал:", reply_markup=builder.as_markup())
    await state.set_state(EditItem.choosing_channel)
    await callback.answer()


@router.callback_query(F.data == "cmd_delete_channel")
async def admin_delete_channel(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("❌ Только владелец.", show_alert=True)
        return

    channel_ids = await get_all_channels()
    if not channel_ids:
        await callback.answer("📭 Нет каналов.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for channel_id in channel_ids:
        title = await get_channel_title(channel_id)
        builder.button(text=f"📺 {title}", callback_data=f"del_channel_{channel_id}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите канал для удаления:", reply_markup=builder.as_markup())
    await state.set_state(DeleteChannelState.choosing_channel)
    await callback.answer()