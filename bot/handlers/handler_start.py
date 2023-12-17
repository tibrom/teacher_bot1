import aiohttp
import json
import time

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


from db.data_base import chats,lesson, lesson_info
from .handler_new_lesson import parse_lesson, InleneKeyboardControl

from db.base import database

#photo=message.photo[0].file_id



async def user_control(message: types.Message):
    key_data = InleneKeyboardControl(info=message,)
    await key_data.delete_all_inline_keyboard()
    
    print(message)
    kb = [
        [types.KeyboardButton(text="Посмотреть мои уроки")],
        [types.KeyboardButton(text="Настройки")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(
        message.from_user.id,
        text='Бот работает',
        reply_markup=keyboard
    )



async def act_lesson(message: types.Message):
    index = str(time.time())
    key_data = InleneKeyboardControl(info=message,)
    await key_data.delete_all_inline_keyboard()
    key_data.index = index
    query = lesson.select().where(
        lesson.c.is_activ == True
    )
    data = await database.fetch_all(query)
    for dt in data:
        but = []
        query = lesson_info.select().where(
            lesson_info.c.lesson_id== int(dt.id)
        )
        data = await database.fetch_all(query)
        for key in data:
            but.append([types.InlineKeyboardButton(text=key.name, callback_data=f"Mes_{key.id}_{key.lesson_id}_{index}"),])
        print(but)
        keyb = types.InlineKeyboardMarkup(inline_keyboard=but)
    
        
        result = await parse_lesson(
            caht_id=message.from_user.id,
            audio_id=dt.audio_id,
            photo=[dt.photo_id] if dt.photo_id is not None else [],
            description=f"{dt.name}\n {dt.description}",
            keyboard=keyb
        )
        key_data.ids_message = result.messages_id
    await key_data.set_ids_message()



async def show_my_lesson_info(callback: types.CallbackQuery):
    index = str(time.time())
    inline = InleneKeyboardControl(info=callback)
    await inline.delete_all_message()
    inline.index=index
    lesson_id = callback.data.split('_')[2]
    print(callback.data)
    query = lesson.select().where(
        lesson.c.id ==  int(lesson_id)
    )
    lesson_data = await database.fetch_one(query)
    parse_id = await parse_lesson(
        caht_id=callback.from_user.id,
        audio_id=lesson_data.audio_id,
        photo=[lesson_data.photo_id] if lesson_data.photo_id is not None else [],
        description=lesson_data.description,
    )
    
    inline.summ_ids_message(parse_id)
    query = lesson_info.select().where(
        lesson_info.c.id==int(inline.value1)
    )
    les_info = await database.fetch_one(query)
    print(dict(les_info))
    if les_info is not None:
        ikc = await parse_lesson(
            caht_id=callback.from_user.id,
            audio_id=les_info.audio_id,
            photo=[les_info.photo_id] if les_info.photo_id is not None else [],
            description=les_info.description
        )



async def user_settings(message: types.Message):
    print(message)
    kb = [
        [types.KeyboardButton(text="Создать ноывй урок")],
        [types.KeyboardButton(text="Редактировать уроки")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(
        message.from_user.id,
        text='Бот работает',
        reply_markup=keyboard
    )





 
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
    dp.message.register(act_lesson,  F.text == "Посмотреть мои уроки")
    dp.message.register(user_settings,  F.text == "Настройки")
    dp.message.register(user_control, CommandStart())
    dp.message.register(user_control)
    dp.my_chat_member.register(on_new_chat_member, ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    ))
    dp.my_chat_member.register(on_left_chat_member, ChatMemberUpdatedFilter(
        member_status_changed=MEMBER >> IS_NOT_MEMBER
    ))
    #dp.message.register(on_left_chat_member, F.LEFT_CHAT_MEMBER())


    dp.callback_query.register(show_my_lesson_info, F.data.startswith('Mes'))