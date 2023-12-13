import requests

TOKEN = "6137712700:AAH5GlhyBYVRS6QB-v-UHhTqB0kqQYQUj54"
CHAT_ID = '-903897745'#'308329053'

def Send_Telegram_Message(message):
    global TOKEN, CHAT_ID
    url = "https://api.telegram.org/bot6137712700:AAH5GlhyBYVRS6QB-v-UHhTqB0kqQYQUj54/sendmessage?chat_id=-903897745&text={}".format(message)
    print(requests.get(url).json())
    # requests.get(url)

def getChatId():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(requests.get(url, verify='/Users/pankaj.wadhwa/Library/Python/3.8/lib/python/site-packages/certifi/cacert.pem'))