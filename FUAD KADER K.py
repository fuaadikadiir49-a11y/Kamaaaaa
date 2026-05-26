import os
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ForceReply

# --- CONFIGURATION ---
API_ID = 31441293
API_HASH = "11f104f3b18044056b9b261c9d454bbf"
BOT_TOKEN = "8816350183:AAEVZoav9bGH4N_KqGugUazoi1qvHsUEqPg"

app = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# Data itti fayyadamaa (Thumbnail, Afaan, fi File ID)
user_data = {}

STRINGS = {
    "Oromo": {
        "start": "Baga nagaaan dhufte! Bot kanaan failii kee Rename gochuu dandeessa.",
        "welcome": "Galatoomi! Maaloo jalqaba **Fakkii** (Thumbnail) ergi, sana booda **Failii** rename ta'u ergi.",
        "thumb_saved": "✅ **Custom thumbnail saved.** Amma failii rename ta'u ergi.",
        "ask_name": "✍️ Maaloo **maqaa haaraa** failii kanaa barreessi (Extension isaa ofuma kootiin itti dabala):",
        "processing": "⌛ **Failiin bu'aa jira... Maaloo obsi.**",
        "uploading": "📤 **Uploading... Gara Telegramitti deebisaa jira.**",
        "error": "❌ Dogoggorri uumameera: "
    },
    "Amharic": {
        "start": "እንኳን ደህና መጡ! በዚህ ቦት ፋይሎችን መቀየር ይችላሉ።",
        "welcome": "እናመሰግናለን! እባክዎ መጀመሪያ **ፎቶ** (Thumbnail) ይላኩ፣ ከዚያ መቀየር የሚፈልጉትን **ፋይል** ይላኩ።",
        "thumb_saved": "✅ **ፎቶው ተቀምጧል።** አሁን ፋይሉን ይላኩ።",
        "ask_name": "✍️ እባክዎ የፋይሉን **አዲስ ስም** ብቻ ይጻፉ (ማራዘሚያውን/Extension እኔው እጨምራለሁ)፡",
        "processing": "⌛ **ፋይሉ እየወረደ ነው... እባክዎ ይታገሱ።**",
        "uploading": "📤 **በመጫን ላይ ነው... እባክዎ ይታገሱ።**",
        "error": "❌ ስህተት ተፈጥሯል፡ "
    },
    "English": {
        "start": "Welcome! Use this bot to rename your files easily.",
        "welcome": "Thank you! Please send a **Photo** first (for thumbnail), then send the **File** you want to rename.",
        "thumb_saved": "✅ **Custom thumbnail saved.** Now send the file to rename.",
        "ask_name": "✍️ Please enter the **new name** for the file (Extension will be added automatically):",
        "processing": "⌛ **Downloading file... Please wait.**",
        "uploading": "📤 **Uploading... Please wait.**",
        "error": "❌ An error occurred: "
    }
}

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    keyboard = ReplyKeyboardMarkup(
        [["Afaan Oromoo", "Amharic", "English"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.reply_text("Maaloo afaan kee filadhu / Please choose your language:", reply_markup=keyboard)

@app.on_message(filters.text & filters.private & ~filters.reply)
async def handle_text(client, message):
    user_id = message.from_user.id
    lang_map = {"Afaan Oromoo": "Oromo", "Amharic": "Amharic", "English": "English"}

    if message.text in lang_map:
        lang = lang_map[message.text]
        user_data[user_id] = {"lang": lang, "thumb": None, "file_msg": None}
        await message.reply_text(STRINGS[lang]["welcome"])

@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "Oromo")
    
    msg = await message.reply_text("⌛...")
    photo_path = await message.download()
    
    if user_id not in user_data:
        user_data[user_id] = {"lang": lang}
    
    user_data[user_id]["thumb"] = photo_path
    await msg.edit_text(STRINGS[lang]["thumb_saved"])

# Failiin yoo dhufu maqaa akka barreessan gaafachuu
@app.on_message((filters.document | filters.video | filters.audio) & filters.private)
async def ask_for_name(client, message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"lang": "Oromo", "thumb": None}
    
    lang = user_data[user_id].get("lang", "Oromo")
    user_data[user_id]["file_msg"] = message
    
    await message.reply_text(
        STRINGS[lang]["ask_name"], 
        reply_markup=ForceReply(selective=True)
    )

# Maqaa ergame fudhatanii extension ka duraa itti dabaluun rename gochuu
@app.on_message(filters.text & filters.private & filters.reply)
async def rename_handler(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_data or not user_data[user_id].get("file_msg"):
        return

    lang = user_data[user_id].get("lang", "Oromo")
    input_name = message.text  # Maqaa haaraa namichi erge
    file_message = user_data[user_id]["file_msg"] 

    msg = await message.reply_text(STRINGS[lang]["processing"])
    
    try:
        # Gosa file addaan baasuu fi maqaa isaa ka duraa irraa extension baasuu
        file_media = file_message.document or file_message.video or file_message.audio
        orig_name = file_media.file_name if file_media else "file"
        
        # Extension isaa addaan baasuu (fkn: .mp4 ykn .mkv)
        _, extension = os.path.splitext(orig_name)
        
        # Maqaa haaraa fi extension walitti fiduu
        new_name = f"{input_name}{extension}"

        # Failii buusuu
        file_path = await file_message.download()
        thumb_path = user_data[user_id].get("thumb")

        await msg.edit_text(STRINGS[lang]["uploading"])

        # Gosa failii addaan baasanii erguu
        if file_message.document:
            await message.reply_document(file_path, thumb=thumb_path, file_name=new_name, caption=f"**{new_name}**")
        elif file_message.video:
            await message.reply_video(file_path, thumb=thumb_path, file_name=new_name, caption=f"**{new_name}**")
        elif file_message.audio:
            await message.reply_audio(file_path, thumb=thumb_path, file_name=new_name, caption=f"**{new_name}**")

        await msg.delete()
        
        if os.path.exists(file_path):
            os.remove(file_path)
        user_data[user_id]["file_msg"] = None  
            
    except Exception as e:
        await msg.edit_text(f"{STRINGS[lang]['error']}{e}")

print("Bot is running and auto-appending extensions...")
app.run()
