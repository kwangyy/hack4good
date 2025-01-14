from dotenv import load_dotenv
import os 
import slack
from pathlib import Path
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta 
import time
import re


app = Flask(__name__)

env_path = Path('.') / ".env"

load_dotenv(dotenv_path=env_path)
slack_event_adapter = SlackEventAdapter(os.environ.get("SIGNING_SECRET"), "/slack/events", app)

client = slack.WebClient(token=os.environ.get("SLACK_TOKEN"))
BOT_ID = client.api_call("auth.test")["user_id"]

SCHEDULED_MESSAGES = [
    {"text": "test", "post_at": int((datetime.now() + timedelta(seconds=63)).timestamp()), "channel": 'C088AGC3S5S'},
    {"text": "test 2", "post_at": int((datetime.now() + timedelta(seconds=64)).timestamp()), "channel": 'C088AGC3S5S'},
]

# Print the scheduled messages to verify timestamps
for message in SCHEDULED_MESSAGES:
    print(f"Scheduling message: {message['text']} at {message['post_at']} (Unix timestamp)")

# Events if bot is mentioned 
@slack_event_adapter.on("message")
def message(payload):
    # Let's just get some info
    print(payload)
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    # if user_id == "U087TAK61D5":
    #     client.chat_postMessage(channel=channel_id, text="wow you are a cool person!")

    # elif user_id == "U087TG04WNT":
    #     client.chat_postMessage(channel=channel_id, text="wow you are not cool at all!")

    # if BOT_ID != user_id:
    #     client.chat_postMessage(channel=channel_id, text=text)

# Slash command is basically just creating an API for this
@app.route("/test_command", methods=["POST"])
def test_command():
    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")

    client.chat_postMessage(channel=channel_id, text=user_id)
    return Response(), 200

@app.route("/generate_summaries", methods=["POST"])
def generate_summaries():
    """
    Basically we want to generate summaries of emails here.
    """
    pass 


@app.route("/reminder", methods=["POST"])
def reminder():
    """
    This is where we want to send reminders to people.
    """
    data = request.form
    text = data.get("text", "")
    print(text)
    channel = data.get("channel_id", "")

    
    users = ""
    message = ""
    for word in text.split():
        if word.startswith('@'):
            users += f"<{word}>"
        else:
            message += f"{word} "
    message = message.strip()
    if users != "":
        new_text = f"Hey {users}, reminder: {message}!"
    else:
        new_text = f"Just a reminder: {message}!"

    client.chat_postMessage(channel = channel, text = "Okay, I will remind them in this channel!")
    client.chat_postMessage(channel=channel, text=new_text)

    # try:
    #     # post_at = int((datetime.now() + timedelta(seconds=seconds)).timestamp())
    #     # client.chat_scheduleMessage(channel=channel, text=new_text, post_at=post_at)
    # except ValueError as e:
    #     client.chat_postMessage(channel=channel, text=f"Error: {e}")
    #     return Response(), 200
    
    return Response(), 200




# def schedule_messages(messages):
#     ids = []
#     for message in messages:
#         response = client.chat_scheduleMessage(channel=message["channel"], text=message["text"], post_at=message["post_at"]).data
#         id_ = response.get('scheduled_message_id')
#         ids.append(id_)
#     return ids  

# def delete_scheduled_messages(ids, channel):
#     for id_ in ids:
#         result = client.chat_deleteScheduledMessage(channel=channel, scheduled_message_id=id_)
#         print(result)

if __name__ == "__main__":
    app.run(debug=True)
