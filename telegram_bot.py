import asyncio
from db.base import database
from bot.create_bot import dp, bot




async def on_startup():
    print('Бот онлайн start')
    await database.connect()
    

async def main() -> None:
    await on_startup()
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())