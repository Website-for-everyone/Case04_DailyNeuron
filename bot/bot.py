import os
import asyncio
import logging
from typing import Dict, Set
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8217851677:AAHN34TMuC1P4e6SppuazFN8BIiLHa_RyIc")
OWNER_HANDLE = os.getenv("OWNER_HANDLE", "@Idrisov_prod")

# User Subscriptions in-memory store
USER_SUBSCRIPTIONS: Dict[int, Set[str]] = {}

CATEGORIES = {
    "llm": "🧠 Большие языковые модели (LLM)",
    "video": "🎬 Генерация видео (Video Gen)",
    "oss": "⚡️ Open Source & Инференс",
    "agents": "🤖 Автономные ИИ-агенты"
}

DIGEST_ITEMS = [
    {
        "cat": "llm",
        "title": "DeepSeek-V3 671B MoE",
        "hype": "🔥 98%",
        "text": "Открытые веса, Multi-head Latent Attention (MLA), превзошла Llama 3.1 405B при стоимости обучения <$6M."
    },
    {
        "cat": "video",
        "title": "Wan 2.1 14B Video DiT",
        "hype": "🔥 94%",
        "text": "1080p фотореалистичная генерация, 3D Causal VAE, полная поддержка Text-to-Video и Image-to-Video."
    },
    {
        "cat": "oss",
        "title": "vLLM v0.7 PagedAttention-3",
        "hype": "⚡️ 89%",
        "text": "Zero-copy тензоры, прирост пропускной способности на 42%, нативное FP8 квантование."
    },
    {
        "cat": "agents",
        "title": "Smolagents от HuggingFace",
        "hype": "🤖 91%",
        "text": "Агенты пишут чистый Python код вместо JSON Tool Calling. Экономия 70% токенов, топ-1 на GAIA."
    }
]

def get_subscriptions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user_subs = USER_SUBSCRIPTIONS.get(user_id, set())
    buttons = []
    for cat_key, cat_name in CATEGORIES.items():
        is_subbed = cat_key in user_subs
        status_icon = "✅" if is_subbed else "➕"
        btn_text = f"{status_icon} {cat_name}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"toggle_sub_{cat_key}")])

    buttons.append([
        InlineKeyboardButton(text="📰 Получить дайджест сейчас", callback_data="get_digest_now")
    ])
    buttons.append([
        InlineKeyboardButton(text="🌐 Читать на сайте", url="http://localhost:8004"),
        InlineKeyboardButton(text="💬 Редактор (@Idrisov_prod)", url=f"https://t.me/Idrisov_prod")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in USER_SUBSCRIPTIONS:
        # Default all subscriptions on
        USER_SUBSCRIPTIONS[user_id] = {"llm", "video", "oss", "agents"}

    welcome_text = (
        "🧠 *Daily Neuron — Кибер-Редакционный Бот ИИ-Трендов*\n\n"
        "Мы отслеживаем прорывы в LLM, генерации видео, открытом коде и агентах.\n"
        "Утренний дайджест доставляется ежедневно в *09:00 AM*.\n\n"
        "Управляйте вашими подписками по категориям ниже:"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_subscriptions_keyboard(user_id))

@router.callback_query(F.data.startswith("toggle_sub_"))
async def cb_toggle_sub(call: CallbackQuery):
    user_id = call.from_user.id
    cat_key = call.data.replace("toggle_sub_", "")

    if user_id not in USER_SUBSCRIPTIONS:
        USER_SUBSCRIPTIONS[user_id] = set()

    if cat_key in USER_SUBSCRIPTIONS[user_id]:
        USER_SUBSCRIPTIONS[user_id].remove(cat_key)
    else:
        USER_SUBSCRIPTIONS[user_id].add(cat_key)

    await call.message.edit_reply_markup(reply_markup=get_subscriptions_keyboard(user_id))
    await call.answer(f"Настройки рубрики {cat_key.upper()} обновлены!")

@router.callback_query(F.data == "get_digest_now")
@router.message(Command("digest"))
async def deliver_digest(event: Message | CallbackQuery):
    user_id = event.from_user.id
    user_subs = USER_SUBSCRIPTIONS.get(user_id, {"llm", "video", "oss", "agents"})

    filtered = [item for item in DIGEST_ITEMS if item["cat"] in user_subs]
    if not filtered:
        filtered = DIGEST_ITEMS

    lines = ["🧠 *DAILY NEURON — УТРЕННИЙ ДАЙДЖЕСТ ТРЕНДОВ ИИ*\n"]
    for i, item in enumerate(filtered, 1):
        lines.append(
            f"*{i}. {item['title']}* ({item['hype']})\n"
            f"_{item['text']}_\n"
        )
    lines.append(f"🔗 Полный разбор с бенчмарками: http://localhost:8004\nУведомления: {OWNER_HANDLE}")

    digest_text = "\n".join(lines)
    logger.info(f"DISPATCH DIGEST to user {user_id}")

    if isinstance(event, CallbackQuery):
        await event.message.answer(digest_text, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(digest_text, parse_mode="Markdown")

@router.message(Command("subscribe"))
async def cmd_subscribe_param(message: Message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    user_id = message.from_user.id
    if user_id not in USER_SUBSCRIPTIONS:
        USER_SUBSCRIPTIONS[user_id] = set()

    if args and args[0].lower() in CATEGORIES:
        cat = args[0].lower()
        USER_SUBSCRIPTIONS[user_id].add(cat)
        await message.answer(f"✅ Вы подписались на рубрику: *{CATEGORIES[cat]}*.", parse_mode="Markdown")
    else:
        await message.answer(
            "Используйте: `/subscribe llm`, `/subscribe video`, `/subscribe oss`, `/subscribe agents`\nили выберите кнопки в /start.",
            parse_mode="Markdown"
        )

def create_daily_neuron_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    return bot, dp

async def main():
    bot, dp = create_daily_neuron_bot()
    logger.info("Daily Neuron Bot started polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
