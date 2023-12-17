import aiohttp
import json
import time
import datetime
from sqlalchemy import select
from aiogram import Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.filters import Command
from aiogram.types import Message, ContentType, InlineKeyboardButton, CallbackQuery, Message
from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart
from ..create_bot import bot


from db.data_base import lesson, lesson_info, message_index


from db.base import database
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from ..state.state import LessonState, LessonInfoState


class InleneKeyboardControl:
    def __init__(self, info = None, callback_data:str = None, index:str = None, keyb=None, chat_id: int=None) -> None:
        self.key_datas = ''
        self.messages_id = ''
        self.keyb =keyb
        
        if index is not None:
            self.index = index
        
        if info is not None:
            print('info is not', info)

            if isinstance(info, CallbackQuery):
                print("<--------CallbackQuery")
                self.key_datas = info.data.split('_')
                self.chat_id = info.from_user.id
                self._flag_key = True
            if isinstance(info, Message):
                print('Message')
                self.chat_id = info.from_user.id
                self._flag_key = False
            self._set_key_datas()
        else:
            print('info is', info)
            self.chat_id=chat_id
            if callback_data is not None and  callback_data != '':
                self.key_datas = callback_data.split('_')
                self._set_key_datas()
        

            
    def _set_key_datas(self):
        if len(self.key_datas) != 0:
            self.prefix = self.key_datas[0]
            self.index = self.key_datas[-1]
        if len(self.key_datas) > 1:
            data = self.key_datas[1:]
            for i, dt in enumerate(data):
                setattr(self, f'value{i+1}', dt)
        

    @property
    def ids_message(self):
        return self.messages_id
    @ids_message.setter
    def ids_message(self, ids):
        if self.messages_id != '':
            self.messages_id += '_'
        self.messages_id += str(ids)
    
    @property
    def idk_message(self):
        return self.messages_id
    
    @idk_message.setter
    def idk_message(self, idk):
        if self.messages_id != '':
            self.messages_id += '_'

        if self.keyb is not None:
            self.messages_id += f'k-{idk}'
        else:
            self.messages_id += str(idk)


    def summ_ids_message(self, data):
        if self.messages_id != '':
            self.messages_id += '_'
        self.messages_id += data.messages_id

    async def set_ids_message(self):
        value = {
            'index': self.index,
            'ids_message': self.messages_id,
            'tg_chat_id': str(self.chat_id),
            'created_at': datetime.datetime.utcnow()
        }
        query = message_index.insert().values(**value)
        await database.execute(query)
        self.messages_id = ''
    
    async def delete_all_message(self):
        query = message_index.select().where(
            message_index.c.index == self.index,
            message_index.c.tg_chat_id == str(self.chat_id)
        )
        data = await database.fetch_one(query)
        if data is not None:
            message_ids = data.ids_message.split('_')
            for id in message_ids:
                print("message_ids", id)
                if id != '':
                    message_id = id.split('-')[-1]
                    #await bot.edit_message_reply_markup(chat_id=self.chat_id,  message_id=int(message_id))
                    await bot.delete_message(chat_id=self.chat_id,  message_id=int(message_id))
                query = message_index.delete().where(
                    message_index.c.id == data.id,
                )
                await database.execute(query)
        self.messages_id = ''

    async def delete_all_inline_keyboard(self):
        query = message_index.select().where(
            message_index.c.tg_chat_id == str(self.chat_id)
        )
        result = await database.fetch_all(query)
        for data in  result:
            message_ids = data.ids_message.split('_')
            for id in message_ids:
                if 'k-' in id:
                    message_id = id.split('-')[-1]
                    try:
                        await bot.edit_message_reply_markup(chat_id=self.chat_id,  message_id=int(message_id))
                    except:
                        pass
                query = message_index.delete().where(
                    message_index.c.id == data.id,
                )
                await database.execute(query)
        self.messages_id = ''


def check_description(text):
    if text is not None and len(text) < 1000:
        return True
    return False


async def parse_lesson(caht_id, audio_id, photo: list, description, keyboard = None,)  -> InleneKeyboardControl:
    result = InleneKeyboardControl(keyb=keyboard)
    
    if len(photo) == 1 and audio_id is None and check_description(description):
        ids = await bot.send_photo(chat_id=caht_id, photo=photo[0], caption=description, reply_markup=keyboard)
        if keyboard is not None:
            result.idk_message = ids.message_id
        else:
            result.ids_message = ids.message_id
    elif audio_id is not None and photo == [] and check_description(description):
        ids = await bot.send_audio(chat_id=caht_id, audio=audio_id, caption=description, reply_markup=keyboard)
        if keyboard is not None:
            
            result.idk_message = ids.message_id
        else:
            result.ids_message = ids.message_id
    else:
        for photo_id in photo:
            ids = await bot.send_photo(chat_id=caht_id, photo=photo_id)
            result.ids_message = ids.message_id
        if audio_id is not None:
            ids = await bot.send_audio(chat_id=caht_id, audio=audio_id)
            result.ids_message = ids.message_id
        if description is not None:
            ids = await bot.send_message(chat_id=caht_id, text=description, reply_markup=keyboard)
            result.idk_message = ids.message_id
    return result





async def write_lesson(lesson_data):
    value = {}
    if lesson_data.get('audio_id') is not None:
        value['audio_id'] = lesson_data.get('audio_id')
    if lesson_data.get('photo_id') is not None:
        value['photo_id'] = lesson_data.get('photo_id')
    if lesson_data.get('description') is not None:
        value['description'] = lesson_data.get('description')
    if lesson_data.get('name') is not None:
        value['name'] = lesson_data.get('name')
    value['created_at'] =  datetime.datetime.utcnow()
    value['is_activ'] = True
    query = lesson.insert().values(**value)
    try:
        await database.execute(query)
        return True
    except:
        return False




async def write_lesson_info(lesson_info_data):
    value = {'lesson_id': lesson_info_data['lesson_id']}
    if lesson_info_data.get('audio_id') is not None:
        value['audio_id'] = lesson_info_data.get('audio_id')
    if lesson_info_data.get('photo_id') is not None:
        value['photo_id'] = lesson_info_data.get('photo_id')
    if lesson_info_data.get('description') is not None:
        value['description'] = lesson_info_data.get('description')
    if lesson_info_data.get('name') is not None:
        value['name'] = lesson_info_data.get('name')
    value['created_at'] =  datetime.datetime.utcnow()
    value['is_activ'] = True
    query = lesson_info.insert().values(**value)
    try:
        await database.execute(query)
        return True
    except:
        return False


async def create_lesson_1(message: types.Message,  state: FSMContext):
    key_data = InleneKeyboardControl(info=message,)
    await key_data.delete_all_inline_keyboard()
    await message.answer(text="Введите название урока", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(LessonState.lesson_name)

async def create_lesson_2(message: types.Message,  state: FSMContext):
    await state.update_data(name=message.text)
    kb = [
        [types.KeyboardButton(text="Завершить редактирование урока")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    text="Отправьте содержание урока. Вы можете использовать текст и медиа, такие как видео, аудио или фото. В ответ бот будет высылать вам как выглядит ваш урок  сейчас для замершение редактирования отправьте 'Завершить редактирование урока'"
    await message.answer(text=text, reply_markup=keyboard)
    await state.set_state(LessonState.lesson_message)

async def create_lesson_3(message: types.Message,  state: FSMContext):
    if message.text == "Завершить редактирование урока":
        lesson_data = await state.get_data()
        if await write_lesson(lesson_data):
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Урок создан',
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.clear()

            return
        await bot.send_message(
            chat_id=message.from_user.id,
            text='Возникла ошибка урок не создан',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()
        return

    if message.content_type == ContentType.VOICE:

        await state.update_data(audio_id=message.voice.file_id)
    elif  message.content_type == ContentType.PHOTO:
        await state.update_data(photo_id=message.photo[-1].file_id)
        
    elif message.content_type == ContentType.TEXT:
        
        await state.update_data(description=message.text)
    elif message.content_type == ContentType.STICKER:
        await state.update_data(sticker_id=message.sticker.file_id)


    lesson_data = await state.get_data()
    
    await parse_lesson(
        caht_id=message.from_user.id,
        audio_id=lesson_data.get('audio_id'),
        photo=[lesson_data.get('photo_id')] if lesson_data.get('photo_id') is not None else [],
        description=lesson_data.get('description')
    )

async def show_my_lesson(message: types.Message,):
    index = str(time.time())
    keyb_data = InleneKeyboardControl(info=message, index=index)
    
    
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
            but.append([types.InlineKeyboardButton(text=key.name, callback_data=f"mes_{key.id}_{index}"),])
        print(but)
        keyb = types.InlineKeyboardMarkup(inline_keyboard=but)
        buttons = [
            [types.InlineKeyboardButton(text="Редактировать урок", callback_data=f"l-key_{dt.id}_{index}"),]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        
        result = await parse_lesson(
            caht_id=message.from_user.id,
            audio_id=dt.audio_id,
            photo=[dt.photo_id] if dt.photo_id is not None else [],
            description=dt.description,
            keyboard=keyb
        )
        ids2 = await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Урок: {dt.name}',
            reply_markup=keyboard
        )
        result.idk_message = ids2.message_id
        keyb_data.summ_ids_message(result)

    await keyb_data.set_ids_message()




async def change_lesson(callback: types.CallbackQuery):
    ids_message = InleneKeyboardControl(info=callback)
    await ids_message.delete_all_message()
    ids_message.index = str(time.time())
    data = callback.data.split('_')
    #await delete_message(index = data[-1], tg_chat_id = callback.from_user.id)
    query = lesson.select().where(
        lesson.c.id ==  int(data[1])
    )
    lesson_data = await database.fetch_one(query)
    
    await bot.send_message(chat_id=callback.from_user.id, text='Редактирование урока')
    parse_id = await parse_lesson(
        caht_id=callback.from_user.id,
        audio_id=lesson_data.audio_id,
        photo=[lesson_data.photo_id] if lesson_data.photo_id is not None else [],
        description=lesson_data.description,
    )
    buttons = [
        [
            types.InlineKeyboardButton(text="Добавить раздел", callback_data=f"C-new_{data[1]}_{ids_message.index}"),
            types.InlineKeyboardButton(text="Удалить урок", callback_data=f"C-del_{data[1]}_{ids_message.index}"),
        ],[types.InlineKeyboardButton(text="Закрыть", callback_data=f"C-cl_{data[1]}_{ids_message.index}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    id2 =await bot.send_message(
        chat_id=callback.from_user.id,
        text='Редактирование урока',
        reply_markup=keyboard
    )
    
    ids_message.summ_ids_message(parse_id)
    ids_message.idk_message = id2.message_id
    await ids_message.set_ids_message()


async def calb_change(callback: types.CallbackQuery,  state: FSMContext):
    inline = InleneKeyboardControl(info=callback)
    await inline.delete_all_message()
    print("inline.prefix", inline.prefix)
    print("inline.value1", inline.value1)
    if inline.prefix == 'C-del':
        query = lesson.delete().where(
            lesson.c.id==int(inline.value1)
        )
        await database.execute(query)
    if inline.prefix == 'C-new':
        await state.set_state(LessonInfoState.key_name)
        await state.update_data(lesson_id=int(inline.value1))
        await bot.send_message(chat_id=callback.from_user.id, text='Ведите текст кнопки' )
    


async def create_lesson_info_name(message: types.Message,  state: FSMContext):
    await state.update_data(name=message.text)
    kb = [
        [types.KeyboardButton(text="Завершить редактирование раздела")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    text="Отправьте содержание раздела. Вы можете использовать текст и медиа, такие как видео, аудио или фото. Описание к медиа отправлять не надо весть текс отправляйте текстовым собщением"
    await message.answer(text=text, reply_markup=keyboard)
    await state.set_state(LessonInfoState.infodata)



async def create_lesson_info(message: types.Message,  state: FSMContext):
    print('data')
    if message.text == "Завершить редактирование раздела":
        lesson_info_data = await state.get_data()
        await write_lesson_info(lesson_info_data)
        print("create lesson info")
        await state.clear()
        return
    if message.content_type == ContentType.VOICE:
        await state.update_data(audio_id=message.voice.file_id)
    elif  message.content_type == ContentType.PHOTO:
        await state.update_data(photo_id=message.photo[-1].file_id)
    elif message.content_type == ContentType.TEXT:
        await state.update_data(description=message.text)
    elif message.content_type == ContentType.STICKER:
        await state.update_data(sticker_id=message.sticker.file_id)


    lesson_data = await state.get_data()
    print(lesson_data)
    await parse_lesson(
        caht_id=message.from_user.id,
        audio_id=lesson_data.get('audio_id'),
        photo=[lesson_data.get('photo_id')] if lesson_data.get('photo_id') is not None else [],
        description=lesson_data.get('description')
    )


async def show_lesson_info(callback: types.CallbackQuery):
    index = str(time.time())
    inline = InleneKeyboardControl(info=callback)
    inline.index=index
    await inline.delete_all_message()
    
    query = lesson_info.select().where(
        lesson_info.c.id==int(inline.value1)
    )
    les_info = await database.fetch_one(query)
    print(dict(les_info))
    if les_info is not None:
        buttons = [
            [
                types.InlineKeyboardButton(text="Удалить раздел", callback_data=f"li-del_{les_info.id}_{index}"),
            ], [types.InlineKeyboardButton(text="Закрыть", callback_data=f"li-cl_{les_info.id}_{index}"),]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        
        ikc = await parse_lesson(
            caht_id=callback.from_user.id,
            audio_id=les_info.audio_id,
            photo=[les_info.photo_id] if les_info.photo_id is not None else [],
            description=les_info.description
        )
        id2 = await bot.send_message(
            chat_id=callback.from_user.id,
            text=f'Редактирование разделa: {les_info.name}',
            reply_markup=keyboard
        )
        inline.summ_ids_message(ikc)
        inline.idk_message = id2.message_id
    await inline.set_ids_message()


async def info_change(callback: types.CallbackQuery,  state: FSMContext):
    
    print(callback.data)
    inline = InleneKeyboardControl(info=callback)
    print("++++++++++",inline.chat_id)
    print("++++++++++",inline.messages_id)
    await inline.delete_all_message()
    if inline.prefix == 'li-del':
        query_select = lesson_info.select().where(
            lesson_info.c.id==int(inline.value1)
        )
        dt = await database.fetch_one(query_select)
        query = lesson_info.delete().where(
            lesson_info.c.id==int(inline.value1)
        )
        await database.execute(query)
        
        await parse_lesson(
            caht_id=callback.from_user.id,
            audio_id=dt.audio_id,
            photo=[dt.photo_id] if dt.photo_id is not None else [],
            description=dt.description
        )
        await bot.send_message(chat_id=callback.from_user.id, text=f'Раззел {dt.name} удален' )

    if inline.prefix == 'li-change':
        pass
    

def register_handler_lesson(dp: Dispatcher):
    dp.message.register(create_lesson_1,  F.text == "Создать ноывй урок")
    dp.message.register(show_my_lesson,  F.text == "Редактировать уроки")
    dp.message.register(create_lesson_2, LessonState.lesson_name)
    dp.message.register(create_lesson_3, LessonState.lesson_message)
    dp.message.register(create_lesson_info_name, LessonInfoState.key_name)
    dp.message.register(create_lesson_info, LessonInfoState.infodata)


    dp.callback_query.register(info_change, F.data.startswith('li'))
    dp.callback_query.register(change_lesson, F.data.startswith('l-key'))
    dp.callback_query.register(calb_change, F.data.startswith('C'))
    dp.callback_query.register(show_lesson_info, F.data.startswith('mes'))
    
