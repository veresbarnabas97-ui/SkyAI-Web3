import logging
import asyncio
import requests
import threading
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- KONFIGURÁCIÓ (ELLENŐRIZD!) ---
TOKEN = "8415660573:AAEn_SBRtcCkFXOTeicrYzCkglsuiDeL050" 
VIP_CHANNEL_ID = "-1008074888500" # Pl: -100123456789 (Mínusz jellel!)
ADMIN_ID = 1979330363
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

# --- AI JELZÉS GENERÁTOR (HÁTTÉRFELADAT) ---
async def send_ai_signals(application):
    """Ez a funkció automatikusan küld jelzéseket a VIP csatornába"""
    print("📡 AI Signal Generator Várakozás...")
    await asyncio.sleep(10) # Várunk 10 mp-t indítás után
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
            
            # Küldés a VIP Csatornába (Ha be van állítva ID)
            if "IDE_ÍRD" not in str(VIP_CHANNEL_ID):
                try:
                    await application.bot.send_message(chat_id=VIP_CHANNEL_ID, text=msg, parse_mode='Markdown')
                    print(f"✅ Jelzés elküldve: {pair}")
                except Exception as e:
                    print(f"⚠️ Nem tudtam üzenni a csatornába: {e}")
            else:
                print(f"ℹ️ Jelzés generálva (Demo): {pair} - Nincs beállítva Channel ID")
            
            # Várakozás a következő jelzésig (pl. 5 perc)
            await asyncio.sleep(300) 
            
        except Exception as e:
            print(f"Signal Error: {e}")
            await asyncio.sleep(60)

# --- POST INIT (EZ OLDJA MEG A HIBÁDAT) ---
async def post_init(application):
    """Ez fut le, AMIKOR a bot már elindult"""
    asyncio.create_task(send_ai_signals(application))

# --- BLOCKCHAIN WATCHER (SZINKRON SZÁL) ---
def watch_blockchain(application):
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={MY_WALLET_BSC}&startblock=0&endblock=99999999&sort=desc&apikey={BSCSCAN_API_KEY}"
    last_hash = None
    print("👀 Blockchain Watcher Elindítva...")
    
    while True:
        try:
            response = requests.get(url).json()
            if response['status'] == '1' and len(response['result']) > 0:
                tx = response['result'][0]
                # Csak a bejövő utalást figyeljük
                if tx['hash'] != last_hash and tx['to'].lower() == MY_WALLET_BSC.lower():
                    last_hash = tx['hash']
                    amount = float(tx['value']) / 10**18
                    
                    msg_text = (
                        f"🚨 **ÚJ BEFIZETÉS!**\n\n"
                        f"💰 {amount:.4f} BNB\n"
                        f"Küldő: `{tx['from']}`\n\n"
                        f"👉 Ellenőrizd a tárcádat!"
                    )
                    # Szálbiztos üzenetküldés
                    asyncio.run_coroutine_threadsafe(
                        application.bot.send_message(chat_id=ADMIN_ID, text=msg_text, parse_mode='Markdown'),
                        application.loop
                    )
                    print("💰 Pénz érkezett!")
            
            time.sleep(60) # 1 perc szünet
        except Exception as e:
            print(f"Watcher Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    # Itt adjuk hozzá a post_init-et, ez a kulcs!
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler('start', start))

    # Blockchain figyelő külön szálon (hogy ne akassza meg a botot)
    watcher_thread = threading.Thread(target=watch_blockchain, args=(application,))
    watcher_thread.daemon = True
    watcher_thread.start()

    print("SkyAI FULL SYSTEM Online...")
    application.run_polling()
