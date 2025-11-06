# --- Fix imghdr issue before anything else ---
import sys, types
sys.modules['imghdr'] = types.ModuleType('imghdr')
setattr(sys.modules['imghdr'], 'what', lambda f, h=None: None)

# --- Now safely import telegram modules ---
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Bot
import time

# --- Your bot token and channel ID ---
BOT_TOKEN = "8295264520:AAHqHCIQdcgKN-IPJ2HOVBgO3ENShr7CW00"
CHANNEL_ID = -1002608505865

print("🤖 Bot starting...")
bot = Bot(token=BOT_TOKEN)


# === 1️⃣ Function: Fetch old files once (safe) ===
def fetch_existing_files_once():
    try:
        print("📂 Scanning for previously uploaded files...")
        offset = 0
        batch_size = 100
        all_files = []
        while True:
            updates = bot.get_updates(offset=offset, limit=batch_size, timeout=10)
            if not updates:
                break
            for update in updates:
                msg = update.message
                if not msg:
                    continue
                file_id = None
                if msg.document:
                    file_id = msg.document.file_id
                elif msg.video:
                    file_id = msg.video.file_id
                elif msg.audio:
                    file_id = msg.audio.file_id
                elif msg.photo:
                    file_id = msg.photo[-1].file_id
                if file_id:
                    all_files.append(file_id)
            offset = updates[-1].update_id + 1
            time.sleep(1)

        if all_files:
            with open("file_ids.txt", "w") as f:
                for fid in all_files:
                    f.write(fid + "\n")
            print(f"✅ Saved {len(all_files)} old file IDs to file_ids.txt")
        else:
            print("❌ No old files found.")
    except Exception as e:
        print("⚠️ Error fetching existing files:", e)


# === 2️⃣ Function: Handle new or forwarded files ===
def handle_file(update, context):
    msg = update.message
    if not msg:
        return

    file_id = None
    if msg.document:
        file_id = msg.document.file_id
    elif msg.video:
        file_id = msg.video.file_id
    elif msg.audio:
        file_id = msg.audio.file_id
    elif msg.photo:
        file_id = msg.photo[-1].file_id

    if file_id:
        msg.reply_text(f"🆔 File ID:\n<code>{file_id}</code>", parse_mode="HTML")
        print(f"✅ File ID: {file_id}")


# === 3️⃣ Start the bot ===
def main():
    fetch_existing_files_once()
    print("🤖 Now starting bot for new files...")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.document | Filters.video | Filters.audio | Filters.photo, handle_file))

    updater.start_polling()
    print("🚀 Bot is running! Send or forward any file to get its ID.")
    updater.idle()


if __name__ == "__main__":
    main()