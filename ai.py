import os
import openai
from telethon import TelegramClient, events

API_ID =  int(os.environ.get("API_ID", 123456))
API_HASH =  os.environ.get("API_HASH", 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
OPENAI_KEY = os.environ.get("OPENAI_KEY","sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
SRC_CHANNEL_ID = int(os.environ.get("SRC_CHANNEL_ID",-123456789))
MAX_ITERATIONS_REMEMBER = int(os.environ.get("MAX_ITERATIONS_REMEMBER", 5))

DESCRIPTION = os.environ.get("","The following is a conversation with an AI assistant. The assistant is helpful, aggressive, angry, and very critical. Speaking spanish.")
CHAT = DESCRIPTION + "\n\nHuman: "

openai.api_key = OPENAI_KEY
client = TelegramClient('session_name', API_ID, API_HASH)
client.start()

@client.on(events.NewMessage(chats = [SRC_CHANNEL_ID]))
async def handler(event):
	try:
		global DESCRIPTION
		global CHAT
		msg = event.message
		msg_txt = str(event.message.message)

		if msg_txt[0:8]=="/profile":
			DESCRIPTION = msg_txt[9:]
			CHAT = DESCRIPTION + "\n\nHuman: "
		else:
			response = openai.Completion.create(
				engine="davinci",
				prompt=CHAT + msg_txt + "\nAI:",
				temperature=0.9,
				max_tokens=150,
				top_p=1,
				frequency_penalty=0.0,
				presence_penalty=0.6,
				stop=["\n", " Human:", " AI:"]
				)
			msg.message = response.choices[0].text
			await client.send_message(	SRC_CHANNEL_ID, msg)
			
			#Limit to MAX_ITERATIONS_REMEMBER 
			iterations = CHAT.count("\nHuman:")
			if iterations > MAX_ITERATIONS_REMEMBER:
				CHAT = DESCRIPTION+"\n"+ CHAT[CHAT.find("\nHuman:", CHAT.find("\nHuman:") + 1):]
			else:	
				CHAT +=  msg_txt + "\nAI:"
				CHAT +=  msg.message + "\nHuman:"
			
	except Exception as ex:
		print(ex)

client.run_until_disconnected()