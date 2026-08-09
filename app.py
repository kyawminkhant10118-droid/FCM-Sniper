import os
import time
import random
import asyncio
import logging
from aiohttp import web
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from pyrogram.errors import FloodWait

#  1. Disable ALL Logging for Zero Lag
logging.disable(logging.CRITICAL)

# --- Environment Variables ---
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Dynamic States
WORDS = ["FCM", "First", "Done", "1st", "Win", "ပါပြီ", "ကျနော်", "အနိုင်", "မန့်လိုက်ပြီ", "1"]
TARGET_IDS = set()
TARGET_USERNAMES = set()
TARGET_NAMES = {}
KEYWORD = ""
DELAY_SEC = 0.0

if not all([API_ID, API_HASH, SESSION_STRING, BOT_TOKEN, OWNER_ID]):
    print("Error: Required Environment Variables missing!")
    exit(1)

# --- High-Speed Engine Setup ---
userbot = Client(
    "fcm_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True,
    ipv6=True,  #  Direct Route for Lower Ping
    workdir="/tmp",
    max_concurrent_transmissions=50
)

bot = Client(
    "fcm_control_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=True,
    workdir="/tmp"
)

owner_filter = filters.user(OWNER_ID)

#  Render Free Web Service Health-Check Server
async def handle_healthcheck(request):
    return web.Response(text="Render Free Bot Engine Live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def notify_owner_bg(chat_title: str, word: str, latency_ms: float):
    try:
        msg = (
            f" **Snipe အောင်မြင်ပါသည်! (Render SG)**\n\n"
            f" **Channel:** {chat_title}\n"
            f" **မန့်လိုက်သောစာ:** `{word}`\n"
            f" **Bot Engine Latency:** `{latency_ms:.2f} ms`"
        )
        await bot.send_message(chat_id=OWNER_ID, text=msg)
    except Exception:
        pass


# ==========================================
#     EXTREME LOW-LATENCY SNIPER ENGINE
# ==========================================

@userbot.on_message(filters.group)
async def ultra_fast_snipe(client: Client, message: Message):
    sender_chat = message.sender_chat or message.forward_from_chat
    if not sender_chat:
        return

    if TARGET_IDS or TARGET_USERNAMES:
        c_id = sender_chat.id
        c_user = sender_chat.username.lower() if sender_chat.username else ""
        if c_id not in TARGET_IDS and c_user not in TARGET_USERNAMES:
            return

    if KEYWORD:
        text = message.text or message.caption or ""
        if KEYWORD not in text.lower():
            return

    if DELAY_SEC > 0:
        await asyncio.sleep(DELAY_SEC)

    if not WORDS:
        return
    chosen_word = random.choice(WORDS)

    t_start = time.perf_counter()
    try:
        await client.send_message(
            chat_id=message.chat.id,
            text=chosen_word,
            reply_to_message_id=message.id,
            parse_mode=ParseMode.DISABLED,
            disable_web_page_preview=True
        )
        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000

        asyncio.create_task(notify_owner_bg(sender_chat.title or "Channel", chosen_word, latency_ms))

    except FloodWait as e:
        asyncio.create_task(
            bot.send_message(OWNER_ID, f" **FloodWait:** `{e.value}` စက္ကန့် စောင့်ပါ။")
        )
    except Exception:
        pass


# ==========================================
#          CONTROL BOT COMMANDS
# ==========================================

@bot.on_message(filters.command("start") & owner_filter)
async def start_cmd(client: Client, message: Message):
    menu = (
        " **Pro FCM Sniper Control Panel (Render SG Free)**\n\n"
        " **Target Commands:**\n"
        " `/addtarget @channel` သို့ `/addtarget -100xxxx` - Target ထည့်ရန်\n"
        " `/deltarget @channel` - Target ဖြုတ်ရန်\n"
        " `/targets` - Target စာရင်းကြည့်ရန်\n"
        " `/cleartargets` - Target အကုန် ဖျက်ရန်\n\n"
        " **Word Commands:**\n"
        " `/addword စကားလုံး` - မန့်မည့် စကားလုံး တိုးရန်\n"
        " `/delword စကားလုံး` - စကားလုံး ဖျက်ရန်\n"
        " `/words` - စကားလုံး စာရင်း ကြည့်ရန်\n\n"
        " **Advanced Settings:**\n"
        " `/setkeyword စာသား` - Keyword Filter တင်ရန်\n"
        " `/clearkeyword` - Keyword Filter ဖြုတ်ရန်\n"
        " `/setdelay စက္ကန့်` - Delay ထည့်ရန်\n"
        " `/status` - လက်ရှိ Setting များ ကြည့်ရန်"
    )
    await message.reply_text(menu)

@bot.on_message(filters.command("addtarget") & owner_filter)
async def add_target(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        val = args[1].strip()
        c_title = None
        c_id = None
        c_username = None

        try:
            target_input = int(val) if val.lstrip("-").isdigit() else val
            chat = await userbot.get_chat(target_input)
            c_id = chat.id
            c_title = chat.title or "Unknown Channel"
            if chat.username:
                c_username = chat.username.lower()
        except Exception:
            pass

        if c_id:
            TARGET_IDS.add(c_id)
            if c_username:
                TARGET_USERNAMES.add(c_username)
            if c_title:
                TARGET_NAMES[c_id] = c_title
            
            res = (
                f" **Target Channel ထည့်သွင်းပြီးပါပြီ!**\n\n"
                f" **Channel Name:** `{c_title}`\n"
                f" **Channel ID:** `{c_id}`\n"
            )
            if c_username:
                res += f" **Username:** `@{c_username}`"
            await message.reply_text(res)
        else:
            if val.lstrip("-").isdigit():
                TARGET_IDS.add(int(val))
                await message.reply_text(f" **Target ID ထည့်ပြီးပါပြီ:** `{val}`")
            else:
                clean_user = val.lstrip("@").lower()
                TARGET_USERNAMES.add(clean_user)
                await message.reply_text(f" **Target Username ထည့်ပြီးပါပြီ:** `@{clean_user}`")
    else:
        await message.reply_text(" `/addtarget @channelname` သို့မဟုတ် `/addtarget -100xxxxxxx` ဟု သုံးပါ။")

@bot.on_message(filters.command("deltarget") & owner_filter)
async def del_target(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        val = args[1].strip()
        if val.lstrip("-").isdigit():
            TARGET_IDS.discard(int(val))
            TARGET_NAMES.pop(int(val), None)
            await message.reply_text(f" Target ID ဖျက်ပြီးပါပြီ: `{val}`")
        else:
            clean_user = val.lstrip("@").lower()
            TARGET_USERNAMES.discard(clean_user)
            await message.reply_text(f" Target Username ဖျက်ပြီးပါပြီ: `@{clean_user}`")
    else:
        await message.reply_text(" `/deltarget @channelname` ဟု သုံးပါ။")

@bot.on_message(filters.command("targets") & owner_filter)
async def list_targets(client: Client, message: Message):
    msg = " **လက်ရှိ Target Channel စာရင်း:**\n\n"
    if not TARGET_IDS and not TARGET_USERNAMES:
        msg += " Target မရှိပါ။ (ဝင်ထားသမျှ Channel တိုင်းကို Auto မန့်မည်)"
    else:
        for c_id in TARGET_IDS:
            name = TARGET_NAMES.get(c_id, "ID Target")
            msg += f" **{name}** (`{c_id}`)\n"
        for u in TARGET_USERNAMES:
            msg += f" `@{u}`\n"
            
    await message.reply_text(msg)

@bot.on_message(filters.command("cleartargets") & owner_filter)
async def clear_targets(client: Client, message: Message):
    TARGET_IDS.clear()
    TARGET_USERNAMES.clear()
    TARGET_NAMES.clear()
    await message.reply_text(" Target များအားလုံးကို ဖျက်လိုက်ပါပြီ။")

@bot.on_message(filters.command("addword") & owner_filter)
async def add_word(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        w = args[1].strip()
        WORDS.append(w)
        await message.reply_text(f" စကားလုံး ထည့်ပြီးပါပြီ: `{w}`")
    else:
        await message.reply_text(" `/addword စကားလုံး` ဟု သုံးပါ။")

@bot.on_message(filters.command("delword") & owner_filter)
async def del_word(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        w = args[1].strip()
        if w in WORDS:
            WORDS.remove(w)
            await message.reply_text(f" စကားလုံး ဖျက်ပြီးပါပြီ: `{w}`")
        else:
            await message.reply_text(" အဆိုပါ စကားလုံး စာရင်းထဲ မရှိပါ။")
    else:
        await message.reply_text(" `/delword စကားလုံး` ဟု သုံးပါ။")

@bot.on_message(filters.command("words") & owner_filter)
async def list_words(client: Client, message: Message):
    msg = " **မန့်မည့် Random စကားလုံးများ:**\n\n"
    for w in WORDS:
        msg += f" `{w}`\n"
    await message.reply_text(msg)

@bot.on_message(filters.command("setkeyword") & owner_filter)
async def set_keyword(client: Client, message: Message):
    global KEYWORD
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        KEYWORD = args[1].strip()
        await message.reply_text(f" Keyword Filter တင်လိုက်ပါပြီ: `{KEYWORD}`")
    else:
        await message.reply_text(" `/setkeyword စာသား` ဟု သုံးပါ။")

@bot.on_message(filters.command("clearkeyword") & owner_filter)
async def clear_keyword(client: Client, message: Message):
    global KEYWORD
    KEYWORD = ""
    await message.reply_text(" Keyword Filter ကို ဖြုတ်လိုက်ပါပြီ။")

@bot.on_message(filters.command("setdelay") & owner_filter)
async def set_delay(client: Client, message: Message):
    global DELAY_SEC
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        try:
            DELAY_SEC = float(args[1].strip())
            await message.reply_text(f" Delay သတ်မှတ်လိုက်ပါပြီ: `{DELAY_SEC}` စက္ကန့်")
        except ValueError:
            await message.reply_text(" ကိန်းဂဏန်း သာ ထည့်ပါ (ဥပမာ `/setdelay 0.5`)")
    else:
        await message.reply_text(" `/setdelay 0` သို့မဟုတ် `/setdelay 0.5` ဟု သုံးပါ။")

@bot.on_message(filters.command("status") & owner_filter)
async def status_cmd(client: Client, message: Message):
    status = f" **Current Engine Status (Render SG):**\n\n"
    status += f" **Targets:** `{len(TARGET_IDS) + len(TARGET_USERNAMES)} Channels`\n"
    status += f" **Words:** `{len(WORDS)} Words`\n"
    status += f" **Keyword Filter:** `{KEYWORD if KEYWORD else 'None'}`\n"
    status += f" **Delay:** `{DELAY_SEC}s`"
    await message.reply_text(status)

async def main():
    await userbot.start()
    await bot.start()
    await start_web_server()  #  Render Port Pass ဖြစ်ရန် Server စတင်ခြင်း
    await idle()

if __name__ == "__main__":
    bot.run(main())
