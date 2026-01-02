import telebot
import requests
from bs4 import BeautifulSoup
import threading

# Aapka Token
BOT_TOKEN = '8524830074:AAGtccQtKZrYVlg9WoYwsNnNK8-7VqjwOdE'
bot = telebot.TeleBot(BOT_TOKEN)

def get_path(user_input):
    clean = user_input.replace("+", "").replace(" ", "").strip()
    if "temporary-phone-number.com" in user_input:
        return user_input.replace("https://temporary-phone-number.com/", "").strip("/")

    # Country logic
    if clean.startswith("46"): return f"Sweden-Phone-Number/{clean}"
    if clean.startswith("358"): return f"Finland-Phone-Number/{clean}"
    if clean.startswith("44"): return f"UK-Phone-Number/{clean}"
    if clean.startswith("1"): return f"USA-Phone-Number/{clean}"
    return None

def fetch_single_sms(chat_id, path):
    url = f"https://temporary-phone-number.com/{path}"
    
    # Better Headers to bypass 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://temporary-phone-number.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        # Session use karne se cookies handle hoti hain, 403 ke chances kam hote hain
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=25)
        
        if res.status_code != 200:
            bot.send_message(chat_id, f"❌ Saeed, Site Error: {res.status_code}\n(Site ne Render ko block kiya hai)")
            return

        soup = BeautifulSoup(res.text, 'html.parser')

        # Latest SMS nikalne ki koshish (Updated selectors)
        msg_found = soup.find('div', class_='message_messages_details')
        if not msg_found:
            msg_found = soup.select_one('.direct-chat-text')
        if not msg_found:
            # Teesra option agar layout change ho
            msg_found = soup.find('td', {'data-label': 'Message'})

        if msg_found:
            txt = msg_found.get_text().strip()
            bot.send_message(chat_id, f"✅ **Saeed, Latest SMS Mil Gaya:**\n\n`{txt}`", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ Saeed, page khul gaya par koi SMS nahi mila. Shayad inbox khali hai.")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Error: {str(e)}")

    bot.send_message(chat_id, "⏹️ Tracking complete. Ab agla number bhejien.")

@bot.message_handler(func=lambda m: True)
def handle(message):
    path = get_path(message.text)
    if path:
        bot.reply_to(message, f"🔎 Saeed, checking latest message for: {path}...")
        threading.Thread(target=fetch_single_sms, args=(message.chat.id, path), daemon=True).start()
    else:
        bot.reply_to(message, "Saeed, ye number ya country sahi nahi hai.")

print("Bot is running...")
bot.infinity_polling()
