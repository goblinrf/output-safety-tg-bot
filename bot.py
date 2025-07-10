import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message
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

# Старт: запросить вопрос
@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await message.answer("👋 Привет! Введи вопрос:")
    await state.set_state(QAForm.waiting_for_question)

# Получаем вопрос, просим ввести ответ
@dp.message(QAForm.waiting_for_question)
async def handle_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Спасибо! Теперь введи ответ:")
    await state.set_state(QAForm.waiting_for_answer)

# Получаем ответ, вызываем сервис и завершаем
@dp.message(QAForm.waiting_for_answer)
async def handle_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question = user_data["question"]
    answer = message.text

    await message.answer("⏳ Обрабатываю вопрос + ответ...")

    ans = ProcessingService()
    masked_answer = await ans.getMascedAnswer(question, answer)

    # Ответ пользователю
    await message.answer(masked_answer)

    # Переход обратно к вопросу
    await message.answer("🔁 Введи следующий вопрос или /start для перезапуска:")
    await state.set_state(QAForm.waiting_for_question)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
