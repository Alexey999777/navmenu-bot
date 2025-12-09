from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"))
    builder.adjust(1)  # одна большая кнопка
    return builder.as_markup()


def section_list_keyboard(sections: list):
    """
    Кнопки разделов — по одной в ряду
    """
    builder = InlineKeyboardBuilder()
    for sec_id, title in sections:
        builder.button(
            text=f"📁 {title}",
            callback_data=f"section_{sec_id}"
        )
    builder.adjust(1)  # ← Одна кнопка в ряду
    return builder.as_markup()