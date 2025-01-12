from dotenv import load_dotenv
import os 
import slack
from pathlib import Path
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)

env_path = Path('.') / ".env"

load_dotenv(dotenv_path=env_path)
slack_event_adapter = SlackEventAdapter(os.environ.get("SIGNING_SECRET"), "/slack/events", app)

client = slack.WebClient(token=os.environ.get("SLACK_TOKEN"))
BOT_ID = client.api_call("auth.test")["user_id"]

# Events if bot is mentioned 
@slack_event_adapter.on("message")
def message(payload):
    # Just getting some stuff 
    print(payload)
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if user_id == "U087TAK61D5":
        client.chat_postMessage(channel=channel_id, text="wow you are a cool person!")

    elif BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=text)

# Slash command is basically just creating an API for this
@app.route("/test_command", methods=["POST"])
def test_command():
    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")

    client.chat_postMessage(channel=channel_id, text=user_id)
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)
