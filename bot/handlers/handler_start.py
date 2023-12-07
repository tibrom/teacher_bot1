import aiohttp
import json

#
from aiogram import Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart

from ..create_bot import bot


from db.data_base import chats


from db.base import database

#photo=message.photo[0].file_id



async def user_control(message: types.Message):
    print(message.photo)
    kb = [
        [types.KeyboardButton(text="Создать ноывй урок")],
        [types.KeyboardButton(text="Посмотреть уроки")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(
        message.from_user.id,
        text='Бот работает',
        reply_markup=keyboard
    )


async def create_lesson_1(message: types.Message):
    pass


 
async def on_new_chat_member(event: ChatMemberUpdated):
    
    chat_id = event.chat.id
    chat_title = event.chat.title
    
    search_query =  chats.select().where(
        chats.c.tg_chat_id == str(chat_id)
    )
    ansewr = await database.fetch_one(search_query)
    if ansewr is None:
        value = {
            'tg_chat_id': str(chat_id),
            'name': str(chat_title)
        }
        query = chats.insert().values(**value)
        await database.execute(query)


async def on_left_chat_member(event: ChatMemberUpdated):
    chat_id = event.chat.id

    
    search_query =  chats.select().where(
        chats.c.tg_chat_id == str(chat_id)
    )
    ansewr = await database.fetch_all(search_query)
    for chat in ansewr:
        query = chats.delete().where(
            chats.c.id==chat.id
        )
        await database.execute(query)
   

        
        
            
            
    


def register_handler(dp: Dispatcher):
    dp.message.register(user_control, CommandStart())
    dp.message.register(user_control)
    dp.my_chat_member.register(on_new_chat_member, ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    ))
    dp.my_chat_member.register(on_left_chat_member, ChatMemberUpdatedFilter(
        member_status_changed=MEMBER >> IS_NOT_MEMBER
    ))
    #dp.message.register(on_left_chat_member, F.LEFT_CHAT_MEMBER())