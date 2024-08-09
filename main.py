import asyncio
from PIL import Image
import config
from modules.lang import get_translation

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from modules import database
from modules.states import GenAIState, IllusionAIState, EditState, SpamState, AddUpText, AddDownText, CutAIState
from modules.keyboards import ban_kb, link_kb, func_kb, ai_kb, edit_kb, ai_continue, admin_kb, font_kb
from modules.callback_data import Ban, AddText
from modules.middleware import ExistsUserMiddleware
from func.ai import upload_image_to_imgbb, gen_photo, gen_illusion, cut_photo
from func.editor import liquid_rescale, bad_quality, make_sketch, make_moire, add_text_to_photo, \
    make_noise, make_bright, make_sat


# start
async def welcome(message: Message):
    start_msg = get_translation("start_msg", message.from_user.id)
    await message.answer_photo("https://i.imgur.com/KVk8Pzq.jpeg", start_msg, reply_markup=func_kb(message.from_user.id))

# editor
async def edit(message: Message, state: FSMContext):
    msg = get_translation("send_to_edit", message.from_user.id)
    await message.answer(msg)
    await state.set_state(EditState.get_photo)

async def edit_call(call: CallbackQuery, state: FSMContext):
    await call.answer()
    msg = get_translation("send_to_edit", call.from_user.id)
    await call.message.answer(msg)
    await state.set_state(EditState.get_photo)

async def photo(message: Message, state: FSMContext):
    await state.clear()
    photo_link = f"photos/{message.from_user.id}.jpg"
    if message.photo:
        file_id = await download_photo(message, message.from_user.id)
        await message.bot.send_photo(chat_id=config.LOG_CHAT, photo=file_id, caption=f"<code>{message.from_user.id}</code> <a href='{message.from_user.url}'>{message.from_user.first_name}</a> sended", parse_mode="html", reply_markup=ban_kb(message.from_user.id))
        im = Image.open(photo_link)
        width, height = im.size
        while width > 800:
            width = (width//4)*3
            height = (height//4)*3
        while height > 800:
            width = (width//4)*3
            height = (height//4)*3
        im = im.resize((width, height))
        im.save(photo_link)
        msg = get_translation("menu", message.from_user.id)
        await message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(message.from_user.id))

async def jm(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await liquid_rescale(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def call_bad_quality(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await bad_quality(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def sketch(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await make_sketch(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def moire(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await make_moire(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def noise(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await make_noise(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def bright(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await make_bright(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def sat(call: CallbackQuery):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    photo_link = f"photos/{call.from_user.id}.jpg"
    await make_sat(photo_link)
    msg = get_translation("result", call.from_user.id)
    await call.message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(call.from_user.id))

async def choose_font(call: CallbackQuery):
    await call.answer()
    msg = get_translation("choose_font", call.from_user.id)
    file_id = await download_photo(call.message, call.from_user.id)
    await call.message.answer_photo(photo=file_id, caption=msg, reply_markup=font_kb())

async def add_text(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await download_photo(call.message, call.from_user.id)
    await state.update_data(font=callback_data.font)
    msg = get_translation("add_up_text", call.from_user.id)
    await call.message.answer(msg)
    await state.set_state(AddUpText.text)

async def add_up_text(message: Message, state: FSMContext):
    if message.text == "/skip":
        up_text = ""
    else:
        up_text = message.text
    await state.update_data(up_text=up_text)
    msg = get_translation("add_down_text", message.from_user.id)
    await message.answer(msg)
    await state.set_state(AddDownText.text)

async def add_down_text(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    font = data["font"]
    up_text = data["up_text"]
    if message.text == "/skip":
        down_text = ""
    else:
        down_text = message.text
    photo_link = f"photos/{message.from_user.id}.jpg"
    await add_text_to_photo(font, up_text, down_text, photo_link)
    msg = get_translation("result", message.from_user.id)
    await message.answer_photo(FSInputFile(photo_link), msg, reply_markup=edit_kb(message.from_user.id))

# ai
async def ai_start(message: Message):
    msg = get_translation("choose_ai", message.from_user.id)
    await message.answer(msg, reply_markup=ai_kb(message.from_user.id))

async def ai_start_call(call: CallbackQuery):
    await call.answer()
    msg = get_translation("choose_ai", call.from_user.id)
    await call.message.answer(msg, reply_markup=ai_kb(call.from_user.id))

async def illusion_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    msg = get_translation("send_illusion", call.from_user.id)
    await call.message.answer(msg)
    await state.set_state(IllusionAIState.image)

async def illuson_photo(message: Message, state: FSMContext):
    file_id = await download_photo(message, message.from_user.id)
    await message.bot.send_photo(chat_id=config.LOG_CHAT, photo=file_id, caption=f"<code>{message.from_user.id}</code> <a href='{message.from_user.url}'>{message.from_user.first_name}</a> sended", parse_mode="html", reply_markup=ban_kb(message.from_user.id))
    msg = get_translation("gen_text", message.from_user.id)
    await message.answer(msg, parse_mode="html")
    await state.set_state(IllusionAIState.gen_param)

async def illuson_gen(message: Message, state: FSMContext):
    await state.clear()
    cmd = message.text
    await message.bot.send_message(chat_id=config.LOG_CHAT, text=f"<code>{message.from_user.id}</code> <a href='{message.from_user.url}'>{message.from_user.first_name}</a> sended\n<b>{cmd}</b>", parse_mode="html", reply_markup=ban_kb(message.from_user.id))
    msg = get_translation("wait_ai_msg", message.from_user.id)
    await message.answer(msg)
    image_link = upload_image_to_imgbb(f"photos/{message.from_user.id}.jpg")
    photo_link = await gen_illusion(image_link, cmd)
    msg = get_translation("result", message.from_user.id)
    await message.answer_photo(photo_link, caption=msg, reply_markup=ai_continue("illusion", message.from_user.id))

async def gen_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    msg = get_translation("gen_text", call.from_user.id)
    await call.message.answer(msg, parse_mode="html")
    await state.set_state(GenAIState.gen_param)

async def gen(message: Message, state: FSMContext):
    await state.clear()
    cmd = message.text
    await message.bot.send_message(chat_id=config.LOG_CHAT, text=f"<code>{message.from_user.id}</code> <a href='{message.from_user.url}'>{message.from_user.first_name}</a> sended\n<b>{cmd}</b>", parse_mode="html", reply_markup=ban_kb(message.from_user.id))
    msg = get_translation("wait_ai_msg", message.from_user.id)
    await message.answer(msg)
    photo_link = await gen_photo(cmd)
    msg = get_translation("result", message.from_user.id)
    await message.answer_photo(photo_link, caption=msg, reply_markup=ai_continue("gen", message.from_user.id))

async def cutter_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    msg = get_translation("send_cutter", call.from_user.id)
    await call.message.answer(msg)
    await state.set_state(CutAIState.image)

async def cutter_photo(message: Message, state: FSMContext):
    await state.clear()
    file_id = await download_photo(message, message.from_user.id)
    await message.bot.send_photo(chat_id=config.LOG_CHAT, photo=file_id, caption=f"<code>{message.from_user.id}</code> <a href='{message.from_user.url}'>{message.from_user.first_name}</a> sended", parse_mode="html", reply_markup=ban_kb(message.from_user.id))
    image_link = upload_image_to_imgbb(f"photos/{message.from_user.id}.jpg")
    photo_link = await cut_photo(image_link, message.from_user.id)
    msg = get_translation("result", message.from_user.id)
    await message.answer_document(FSInputFile(photo_link), caption=msg, reply_markup=ai_continue("cutter", message.from_user.id))


# other func

async def donate(call: CallbackQuery):
    await call.answer()
    file_id = await download_photo(call.message, call.from_user.id)
    msg = get_translation("donate", call.from_user.id)
    donate_text = f"🖤{msg}:\n"
    with open("donate.txt", "rt", encoding="utf-8") as d:
        donate_text += d.read()
    p = InputMediaPhoto(media=file_id, caption=donate_text, parse_mode='html')
    await call.message.edit_media(media=p, reply_markup=func_kb(call.from_user.id), disable_web_page_preview=True)

async def download_photo(message, user_id):
    photo_link = f"photos/{user_id}.jpg"
    file_info = await message.bot.get_file(message.photo[-1].file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)
    with open(photo_link, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())
    return message.photo[-1].file_id

async def lang(call: CallbackQuery):
    language = database.select(f"select locale from users where id = {call.from_user.id}", one=True)[0]
    if language == "en":
        database.insert_delete(f"update users set locale = 'ru' where id = {call.from_user.id}")
        await call.answer("🇷🇺Ваш язык изменён на русский")
    else:
        database.insert_delete(f"update users set locale = 'en' where id = {call.from_user.id}")
        await call.answer("🇺🇸Your language is english")

# admin
async def ban(call: CallbackQuery, callback_data: dict):
    await call.message.delete()
    user_id = callback_data.id
    await call.bot.ban_chat_member(chat_id=config.CHANNEL, user_id=user_id)
    await call.message.answer(f"❌<code>{user_id}</code> blocked", parse_mode='html')

async def admin(call: CallbackQuery):
    await call.answer()
    if str(call.from_user.id) in config.ADMIN_IDS:
        await call.message.answer("⚠️Выберите, что нужно делать", reply_markup=admin_kb())

async def spam(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("💚Отправьте сообщение\n❌/cansel")
    await state.set_state(SpamState.start)

async def send_spam(message: Message, state: FSMContext):
    await state.clear()
    if message.text == "/cansel":
        await message.answer("❌Отменено!")
        return
    await message.answer("🚀Запущено")
    users = database.select(f"select id from users")
    keyboard = None
    txt = message.html_text
    if message.reply_markup:
        keyboard = message.reply_markup
    if message.photo:
        file_id = message.photo[-1].file_id
        for user in users:
            try:
                await message.bot.send_photo(
                    chat_id=user[0],
                    caption=txt,
                    photo=file_id,
                    parse_mode="html",
                    reply_markup=keyboard
                )
            except:
                pass
    if message.sticker:
        file_id = message.sticker.file_id
        for user in users:
            try:
                await message.bot.send_sticker(
                    chat_id=user[0],
                    sticker=file_id
                )
            except:
                pass
    elif message.video:
        file_id = message.video.file_id
        for user in users:
            try:
                await message.bot.send_video(
                    chat_id=user[0],
                    caption=txt,
                    video=file_id,
                    parse_mode="html",
                    reply_markup=keyboard
                )
            except:
                pass
    elif message.animation:
        file_id = message.animation.file_id
        for user in users:
            try:
                await message.bot.send_animation(
                    chat_id=user[0],
                    caption=txt,
                    animation=file_id,
                    parse_mode="html",
                    reply_markup=keyboard
                )
            except:
                pass
    if message.text:
        for user in users:
            try:
                await message.bot.send_message(
                    chat_id=user[0],
                    text=txt,
                    parse_mode="html",
                    reply_markup=keyboard
                )
            except:
                pass
    await message.answer("✅Finished")

async def main():
    bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=config.API_TOKEN, default=bot_properties)
    dp = Dispatcher(storage=MemoryStorage())
    # middleware
    dp.message.middleware(ExistsUserMiddleware())
    # start
    dp.message.register(welcome, Command(commands="start"))
    dp.callback_query.register(lang, F.data == "lang")
    # admin
    dp.callback_query.register(admin, F.data == "admin")
    dp.callback_query.register(spam, F.data == "spam")
    dp.message.register(send_spam, SpamState.start)
    # edit
    dp.message.register(edit, Command(commands="edit"))
    dp.callback_query.register(edit_call, F.data == "edit")
    dp.callback_query.register(call_bad_quality, F.data == "bad_quality")
    dp.callback_query.register(jm, F.data == "jm")
    dp.callback_query.register(sketch, F.data == "sketch")
    dp.callback_query.register(moire, F.data == "moire")

    dp.callback_query.register(noise, F.data == "noise")
    dp.callback_query.register(bright, F.data == "bright")
    dp.callback_query.register(sat, F.data == "sat")

    dp.message.register(photo, EditState.get_photo)
    dp.callback_query.register(choose_font, F.data == "text")
    dp.callback_query.register(add_text, AddText.filter())
    dp.message.register(add_up_text, AddUpText.text)
    dp.message.register(add_down_text, AddDownText.text)
    # ai
    dp.message.register(ai_start, Command(commands="ai"))
    dp.callback_query.register(ai_start_call, F.data == "ai")
    dp.callback_query.register(gen_start, F.data == "gen")
    dp.callback_query.register(illusion_start, F.data == "illusion")
    dp.callback_query.register(cutter_start, F.data == "cutter")
    dp.message.register(gen, GenAIState.gen_param)
    dp.message.register(illuson_photo, IllusionAIState.image)
    dp.message.register(illuson_gen, IllusionAIState.gen_param)
    dp.message.register(cutter_photo, CutAIState.image)
    # other commands
    dp.callback_query.register(donate, F.data == "donate")
    dp.callback_query.register(ban, Ban.filter())
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
