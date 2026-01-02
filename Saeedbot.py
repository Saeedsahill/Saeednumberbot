import telebot
import cloudscraper
import random
from bs4 import BeautifulSoup
import threading

# Aapka Token
BOT_TOKEN = '8524830074:AAGtccQtKZrYVlg9WoYwsNnNK8-7VqjwOdE'
bot = telebot.TeleBot(BOT_TOKEN)

# Kuch working free proxy list (Aap aur bhi add kar sakte hain)
PROXY_LIST = [
    "http://50.222.245.47:80",
    "http://20.219.180.149:80",
    "http://162.223.90.130:80",
    "http://198.199.86.11:80",
]

def get_path(user_input):
    clean = user_input.replace("+", "").replace(" ", "").strip()
    if "temporary-phone-number.com" in user_input:
        return user_input.replace("https://temporary-phone-number.com/", "").strip("/")

    if clean.startswith("46"): return f"Sweden-Phone-Number/{clean}"
    if clean.startswith("358"): return f"Finland-Phone-Number/{clean}"
    if clean.startswith("44"): return f"UK-Phone-Number/{clean}"
    if clean.startswith("1"): return f"USA-Phone-Number/{clean}"
    return None

def fetch_single_sms(chat_id, path):
    url = f"https://temporary-phone-number.com/{path}"
    
    # Random proxy select karna
    proxy = random.choice(PROXY_LIST)
    proxies = {"http": proxy, "https": proxy}

    try:
        # Cloudscraper browser emulation ke saath
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Request with Proxy and Headers
        res = scraper.get(url, proxies=proxies, timeout=30)
        
        if res.status_code == 403:
            bot.send_message(chat_id, "❌ **Saeed, 403 Forbidden:** Proxy ne bhi kaam nahi kiya. Site ne data center block kiya hua hai.")
            return
        
        soup = BeautifulSoup(res.text, 'html.parser')

        # SMS nikalne ka logic
        msg_found = soup.find('div', class_='message_messages_details')
        if not msg_found:
            msg_found = soup.select_one('.direct-chat-text')
        
        if not msg_found:
            # Table logic as fallback
            rows = soup.find_all('tr')
            for row in rows:
                if "ago" in row.text.lower():
                    msg_found = row
                    break

        if msg_found:
            txt = msg_found.get_text().strip()
            clean_txt = "\n".join([line.strip() for line in txt.splitlines() if line.strip()])
            bot.send_message(chat_id, f"✅ **Saeed, Latest SMS Found:**\n\n`{clean_txt}`", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ Saeed, Page open hua par SMS nahi mila.")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Error: Proxy slow hai ya connection fail ho gaya. Dobara try karein.\n`{str(e)}`")

    bot.send_message(chat_id, "⏹️ Process Finished.")

@bot.message_handler(func=lambda m: True)
def handle(message):
    path = get_path(message.text)
    if path:
        bot.reply_to(message, f"🔎 Saeed, Proxy ke zariye bypass kar raha hoon: {path}...")
        threading.Thread(target=fetch_single_sms, args=(message.chat.id, path), daemon=True).start()
    else:
        bot.reply_to(message, "Saeed, ye number format theek nahi hai.")

print("Bot is running with Proxy & Cloudscraper...")
bot.infinity_polling()
