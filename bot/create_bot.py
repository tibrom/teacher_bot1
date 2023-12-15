from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage



BOT_TOKEN = "5676281811:AAGj_O56Y_NCUc0_ws5-P-h96hw4VkX6OKE"



bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


from .handlers.handler_start import register_handler
from .handlers.handler_new_lesson import register_handler_lesson

register_handler_lesson(dp)
register_handler(dp)