
############################################# - [TELEGRAM BOT - PART] - #############################################

import asyncio
import telebot
import os
from dotenv import load_dotenv
import random, string
import json
import time
import requests
load_dotenv()

# Some declaration
bot_token=os.getenv('telegram_bot_token')
verified_userid=os.getenv('user_with_access')

## Bot initialization
bot = telebot.TeleBot(bot_token, parse_mode="HTML")
# Main message handler
@bot.message_handler(commands=["start"])
def start_cmd(message):
    if str(message.from_user.id) in verified_userid:
        bot.reply_to(message,f"Hello <b>@{message.from_user.username}</b>\nHow are you?\n\nJust forward your content here and I will try to forward it to Discord server channel.\nNote: I can forward only document,photo and video for now !!!")
    else:
        bot.reply_to(message,f"<b>Sorry you don't have access to his bot!</b>")



@bot.message_handler(content_types=["document","photo","video"])
def handle_all(message):
    '''
    Function to handle document, photo and video content
    :param message: message object
    '''
    if str(message.from_user.id) in verified_userid:
        content=message.content_type
        bot.reply_to(message,f"Content type is valid. Creating a file with the info..")

        fileId=getFileId(message,content)
        fileSize=getFileSize(message,content)   
        fileName=getFileName(message,content)

        create_userid_contentfile(message.from_user.id,fileName,fileId,fileSize,message.from_user.username)
        time.sleep(1)
        bot.edit_message_text("Done! Getting the file path...",message.chat.id, message.message_id+1)
        file_path=get_file_path(fileId)
        time.sleep(1)
        bot.edit_message_text("Done! Downloading the file...",message.chat.id, message.message_id+1)

        if fileSize>=8000000:
            bot.edit_message_text("File size is too big. Aborted ❌",message.chat.id, message.message_id+1)
        else:
            download_file(file_path,fileName)
            time.sleep(1)
            bot.edit_message_text("Done! Forwarding it to Discord bot.. yeeet",message.chat.id, message.message_id+1)
            bot.edit_message_text("Done! Forwarded ✅",message.chat.id, message.message_id+1)
            # the dc_bot function should be called here
    else:
        bot.reply_to(message,f"<b>Sorry you don't have access to his bot!</b>")


def create_userid_contentfile(userid,*args):
    '''
    Create a json file with parameter userid
    :param userid: The user id to create a json file - {userid}_content.json
    :param *args: content_type, file_name, files_id, files_size and forwarded_from parameters
    '''
    file=f"{userid}_content.json"
    del_file(file)
    content={
        "file_name":args[0],
        "file_id":args[1],
        "file_size":args[2],
        "forwarded_from":args[3]
    }
    with open(file,'a') as f:
        json.dump(content,f)


def del_file(file):
    '''
    Delete a file  
    :param file: file to delete
    '''
    if os.path.exists(file):
        os.remove(file)


def getFileId(message,contenttype):
    '''
    Return a file id
    :param message: message object
    :param contenttype: content type of a file 
    '''
    if contenttype == "photo":
        return message.photo[len(message.photo)-1].file_id
    elif contenttype == "video":
        return message.video.file_id
    elif contenttype == "document":
        return message.document.file_id


def getFileSize(message,contenttype):
    '''
    Return a file size in kb
    :param message: message object
    :param contenttype: content type of a file 
    '''
    if contenttype == "photo":
        return message.photo[len(message.photo)-1].file_size
    elif contenttype == "video":
        return message.video.file_size
    elif contenttype == "document":
        return message.document.file_size

def getFileName(message,contenttype):
    '''
    Return a file name or generate if no name exist
    :param message: message object
    :param contenttype: content type of a file 
    '''
    if contenttype == "photo":
        return getRandomWords()+".jpg"
    elif contenttype == "video":
        return getRandomWords()+".mp4"
    elif contenttype == "document":
        return message.document.file_name


def getRandomWords():
    '''
    Generate random word with Upper+lower case and numbers
    '''
    letters = string.ascii_lowercase+""+string.ascii_uppercase+""+string.digits
    return ''.join(random.choice(letters) for i in range(6))


def get_file_path(file_id):
    '''
    Get the file path of the document, video or photo send in the bot
    :param file_id: file id from the sent document, video or photo
    returns the file file path
    '''
    token = bot_token
    base_url=f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    req=requests.get(base_url).json()
    return req["result"]["file_path"]

def download_file(file_path,filename):
    '''
    Download the file with the help of the filepath and write it as binary to download it
    :param file_path: file path from the sent document, video or photo
    :param filename: to name the downloaded file
    '''
    token = bot_token
    base_url=f"https://api.telegram.org/file/bot{token}/{file_path}"
    req=requests.get(base_url)    
    with open(filename, 'wb') as f:
        f.write(req.content)


bot.polling() # start the bot



