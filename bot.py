import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from service.ServicePart import ProcessingService

# Загрузка .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

# FSM-хранилище (в памяти)
storage = MemoryStorage()

# Инициализация бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=storage)

# FSM-состояния
class QAForm(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()

# Меню с кнопкой "Старт"
start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Старт")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Нажми кнопку или введи /start"
)

# Приветствие и меню
@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я бот проекта <b>Output-Safety & Leakage Guard</b>.\n\n"
        "Чтобы начать работу, нажми кнопку «🚀 Старт» ниже.",
        reply_markup=start_menu
    )

# Нажата кнопка "Старт"
@dp.message(F.text == "🚀 Старт")
async def begin_workflow(message: Message, state: FSMContext):
    await message.answer("✍️ Введи, пожалуйста, вопрос:")
    await state.set_state(QAForm.waiting_for_question)

# Получаем вопрос
@dp.message(QAForm.waiting_for_question)
async def handle_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Спасибо! Теперь введи ответ:")
    await state.set_state(QAForm.waiting_for_answer)

# Обрабатываем ответ и возвращаем результат
@dp.message(QAForm.waiting_for_answer)
async def handle_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question = user_data["question"]
    answer = message.text

    await message.answer("⏳ Обрабатываю вопрос + ответ...")

    ans = ProcessingService()
    masked_answer = await ans.getMascedAnswer(question, answer)

    await message.answer(masked_answer)

    # Предлагаем задать новый вопрос
    await message.answer("🔁 Введи следующий вопрос или нажми «🚀 Старт» для новой сессии.")
    await state.set_state(QAForm.waiting_for_question)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
