from dotenv import load_dotenv
import os
import time
from discord_webhook import DiscordWebhook
import random
import logging
from aiogram import Bot, Dispatcher, executor, types
import random, string
import requests
load_dotenv()

############ General variables ############
BOT_TOKEN=os.getenv("BOT_TOKEN") # Bot token
ACCESS_IDS=os.getenv("USER_WITH_ACCESS").split(",") # List of userids with access to the bot
ACCESS_IDS=[x for x in ACCESS_IDS if x!=""]
WEBHOOK_URLS=os.getenv("WEBHOOK_URLS") # List of discord webhook urls to send messages to
FILES_EXTENSIONS=["txt","zip","anom","loli","rar","svb"]
applieduser_filename="applieduser.json"#

############ Bot setup AIOGRAM ############
# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/cmds` command
    """
    if str(message.from_user.id) in ACCESS_IDS:
        await message.reply(f"<b>Hi @{message.from_user.username}</b>\nHow are you doing?\n\nJust send me a file and I will forward it to Discord :) .")
    else:
        await message.reply("You don't have access to this bot\n")


@dp.message_handler(content_types=['document','photo','video','audio'])
async def handle_others(message: types.Message):
    """
    This handler will be called when user sends a file matching the content types specified
    """
    content_type=message.content_type
    fileid,filename=getFileId(message,content_type),getFileName(message,content_type)
    file_object=await bot.get_file(file_id=fileid)

    if(file_object.file_size<=8000000):
        await bot.download_file(file_path=file_object.file_path,destination=f"./{filename}") # Download file
        if filename.split(".")[-1] in FILES_EXTENSIONS:
            await message.reply(sendFile_2(filename))
        else:
            await message.reply(sendFile_1(filename))
        delFile(filename) # Delete the file after sending it

    elif(file_object.file_size<=20000000):
        await message.reply("File size is big but trying to upload to anonfiles and send it...")
        await bot.download_file(file_path=file_object.file_path,destination=f"./{filename}") # Download file
        response=uploadAnonfiles(filename)
        if(type(response)==list): # If it is a list -> error
            await message.reply(response[1])
        else:
            await message.reply(sendText(response))
        delFile(filename) # Delete the file after sending it
    
    else:
        message.reply("File size is too big... aborted!")



        
    

@dp.message_handler()
async def msg_forwader(message: types.Message):
    """
    This handler will be called when user sends a message
    """
    await message.reply(sendText(message.text))
    
######################## USEFUL FUNCTIONS #######################
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
    elif contenttype == "audio":
        return message.audio.file_id

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

def delFile(filename):
    """Delete a file

    Args:
        filename (string): The filename to delete
    """
    try:
        os.remove(filename)
    except:
        pass



def uploadAnonfiles(filename):
    """Upload a file to anonfiles and return the link or error

    Return type is not ideal  as it returns two types of values

    Args:
        filename (string): filename to upload

    Returns:
        array/string: array if there is an error, string if there is no error
    """
    request=requests.post(url="https://api.anonfiles.com/upload",files={"file":open(filename,"rb")}).json()
    if(request["status"]==True):
        return request["data"]["file"]["url"]["full"]
    else:
        return ["error",["error"]["message"]]

    


##################### DISCORD BOT ##############################

WEBHOOKS=os.getenv("WEBHOOK_URLS").split(",")
WEBHOOKS=[x for x in WEBHOOKS if x!=""]

# send the file to first webhook - memes & co
def sendFile_1(filename):
    webhook = DiscordWebhook(url=WEBHOOKS[0], username="LearnIT Forward Bot")
    time.sleep(4)
    with open(filename, 'rb') as f:
        webhook.add_file(file=f.read(), filename=filename)
    # send the webhook
    try:
        response = webhook.execute(remove_embeds=True, remove_files=True)
    except Exception as e:
        return "Error: "+str(e)
    if response.status_code==200:
        return f"Successfully forwarded to Discord! [{response.status_code}] "
    return f"Error while forwarding to Discord! - [{response.status_code}] "

#send the text to second webhook .txt file & co
def sendText(text):
    webhook = DiscordWebhook(url=WEBHOOKS[1], username="LearnIT Forward Bot", rate_limit_retry=True,
                            content=text)
    try:
        response = webhook.execute()
    except Exception as e:
        return "Error: "+str(e)
    if response.status_code==200:
        return f"Successfully forwarded to Discord! - [{response.status_code}] "
    return f"Error while forwarding to Discord! - [{response.status_code}] "

# send the file to second webhook text & co
def sendFile_2(filename):
    webhook = DiscordWebhook(url=WEBHOOKS[1], username="LearnIT Forward Bot")
    time.sleep(4)
    with open(filename, 'rb') as f:
        webhook.add_file(file=f.read(), filename=filename)
    # send the webhook
    response = webhook.execute(remove_embeds=True, remove_files=True)
    if response.status_code==200:
        return f"Successfully forwarded to Discord! [{response.status_code}] "
    return f"Error while forwarding to Discord! - [{response.status_code}] "



executor.start_polling(dp, skip_updates=True)