import requests

TOKEN = "6137712700:AAH5GlhyBYVRS6QB-v-UHhTqB0kqQYQUj546137712700:AAH5GlhyBYVRS6QB-v-UHhTqB0kqQYQUj54"


def Send_Telegram_Message(message):
    url = 'https://api.telegram.org/bot5064982142:AAHSSW33lW7S1lePZ-ecxSubtlLrpBQKWWg/sendmessage?chat_id=-719268472&text={}'.format(message)

    requests.get(url)

def getChatId():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(requests.get(url, verify='/Users/pankaj.wadhwa/Library/Python/3.8/lib/python/site-packages/certifi/cacert.pem'))

getChatId()



# "https://api.telegram.org/bot6137712700:AAH5GlhyBYVRS6QB-v-UHhTqB0kqQYQUj54/getUpdates"