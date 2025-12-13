import logging
import asyncio
import requests
import threading
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- KONFIGURÁCIÓ ---
TOKEN = "8074888500:AAEQvVzcKVcZLOW-LbNm-rUR9qDg-DShZeI" 

# Mivel nincs csatorna, a bot NEKED küldi a jelzéseket privátban (Teszt mód):
ADMIN_ID = 1979330363
VIP_CHANNEL_ID = ADMIN_ID 

WEB_APP_URL = "https://veresbarnabas97-ui.github.io/SkyAI-Web3/"
BSCSCAN_API_KEY = "XBNK3KPNE1GECVV633RI2GUNADQVFYGCGH"
MY_WALLET_BSC = "0xC424c3119e5D1fA6dD91eF72aF25e1F4A260f69C"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- START MENÜ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 WEB3 TERMINÁL NYITÁSA", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("💎 Prémium Csatlakozás", url="https://t.me/VeresBarnabas1")]
    ]
    await update.message.reply_text(
        "🌌 **Üdvözöl a SkyAI Rendszer!**\n\nA kereskedéshez és a token vásárláshoz nyisd meg az appot.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# --- AI JELZÉS GENERÁTOR ---
async def send_ai_signals(application):
    """Ez a funkció automatikusan küld jelzéseket"""
    print("📡 AI Signal Generator Várakozás (10mp)...")
    await asyncio.sleep(10)
    print("📡 AI Signal Generator Elindítva!")
    
    pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "SKY/BNB"]
    actions = ["LONG 🟢", "SHORT 🔴"]
    
    while True:
        try:
            # Véletlenszerű jelzés generálása
            pair = random.choice(pairs)
            action = random.choice(actions)
            price = random.randint(200, 65000)
            tp = price * 1.05
            sl = price * 0.95
            
            msg = (
                f"🤖 **SkyAI Sniper Alert**\n\n"
                f"Eszköz: **{pair}**\n"
                f"Irány: **{action}**\n"
                f"Belépő: ${price}\n\n"
                f"🎯 TP: ${tp:.2f}\n"
                f"🛡 SL: ${sl:.2f}\n\n"
                f"⚡ *Confidence: {random.randint(85,99)}%*"
            )
            
            # Üzenet küldése (Most neked, privátban)
            try:
                await application.bot.send_message(chat_id=VIP_CHANNEL_ID, text=msg, parse_mode='Markdown')
                print(f"✅ Jelzés elküldve (Adminnak): {pair}")
            except Exception as e:
                print(f"⚠️ Hiba az üzenetküldésnél: {e}")
            
            # Várakozás (pl. 300 mp = 5 perc)
            await asyncio.sleep(300) 
            
        except Exception as e:
            print(f"Signal Error: {e}")
            await asyncio.sleep(60)

# --- POST INIT (Automata indítás) ---
async def post_init(application):
    asyncio.create_task(send_ai_signals(application))

# --- BLOCKCHAIN WATCHER (PÉNZ FIGYELŐ) ---
def watch_blockchain(application):
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={MY_WALLET_BSC}&startblock=0&endblock=99999999&sort=desc&apikey={BSCSCAN_API_KEY}"
    last_hash = None
    print("👀 Blockchain Watcher Elindítva...")
    
    while True:
        try:
            response = requests.get(url).json()
            if response['status'] == '1' and len(response['result']) > 0:
                tx = response['result'][0]
                if tx['hash'] != last_hash and tx['to'].lower() == MY_WALLET_BSC.lower():
                    last_hash = tx['hash']
                    amount = float(tx['value']) / 10**18
                    
                    msg_text = (
                        f"🚨 **ÚJ BEFIZETÉS!**\n\n"
                        f"💰 {amount:.4f} BNB\n"
                        f"Küldő: `{tx['from']}`\n\n"
                        f"👉 Ellenőrizd a tárcádat!"
                    )
                    asyncio.run_coroutine_threadsafe(
                        application.bot.send_message(chat_id=ADMIN_ID, text=msg_text, parse_mode='Markdown'),
                        application.loop
                    )
                    print("💰 Pénz érkezett!")
            
            time.sleep(60)
        except Exception as e:
            print(f"Watcher Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler('start', start))

    watcher_thread = threading.Thread(target=watch_blockchain, args=(application,))
    watcher_thread.daemon = True
    watcher_thread.start()

    print(f"SkyAI Bot (@SkyAI00bot) Online...")
    application.run_polling()
