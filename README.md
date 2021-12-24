# Telegram to Discord Forwarder
## Bot to forward telegram document, video or photos to discord server channel

### **How this bot works**
- First, only check for valid content type (video, photo, document or text)
- Then get the file path using the file id
- Before downloading the file, check the file size (if it is> 8MB)
- If it is less than 8MB, download the file from the file path, otherwise abort
- Call the function `send_file` to forward the file to the Discord channel

**Author** - [officialbishowb](https://t.me/officialbishowb)
