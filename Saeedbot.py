from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import re
import asyncio

BOT_TOKEN = "8493383117:AAG04DYFFrUgXpZjzAQ8urTFTBKiTKRh-0A"  # @BotFather se mila hua token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Mujhe do cheezen bhej sakte ho:\n"
        "1) Koi file jisme numbers ho (TXT/CSV, har line ya space se alag)\n"
        "2) Seedha copy-paste text jisme numbers ho.\n\n"
        "Main in sab numbers ko alag-alag messages me bhejunga."
    )

def extract_numbers_from_text(text: str):
    # comma / semicolon ko space se replace
    cleaned = text.replace(',', ' ').replace(';', ' ')
    parts = re.split(r'\s+', cleaned.strip())

    nums = []
    for p in parts:
        if p.isdigit():
            nums.append(p)
    return nums

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()

    # bytes -> text (jo decode nahi ho payega usko ignore)
    text = file_bytes.decode(errors="ignore")

    numbers = extract_numbers_from_text(text)

    if not numbers:
        await update.message.reply_text("File me koi valid number nahi mila (pure digits).")
        return

    await update.message.reply_text(f"File me {len(numbers)} numbers mile. Ab bhej raha hoon...")

    for n in numbers:
        await update.message.reply_text(str(n))
        await asyncio.sleep(0.1)  # halka delay taake flood na ho

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    numbers = extract_numbers_from_text(text)

    if not numbers:
        await update.message.reply_text("Text me koi valid number nahi mila (sirf 0-9 wale digits hone chahiye).")
        return

    await update.message.reply_text(f"Text me {len(numbers)} numbers mile. Ab bhej raha hoon...")

    for n in numbers:
        await update.message.reply_text(str(n))
        await asyncio.sleep(0.1)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
