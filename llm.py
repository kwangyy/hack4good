import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import re
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

load_dotenv()

client = InferenceClient(api_key=os.environ.get("HF_API_KEY"))

messages = []

completion = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct", 
	messages=messages, 
	max_tokens=500
)
date_now = datetime.now()

reminder_prompt = """
You are an expert parser for Slack messages. You are given a Slack message, and you will need to extract two things:
1. Extract what the reminder is about.
2. Extract when the reminder is for. 

You will need to return a JSON object with the following keys:
- "reminder_text": The text of the reminder.
- "time_input": The original time specification (e.g., "5 minutes", "10am tomorrow")
- "reminder_time": The absolute time for the reminder in "DD/MM/YYYY HH:MM:SS" format

Here is the Slack message:
{message}

Here are a few examples of the JSON you will need to return:
{{"message": "Remind me to take a break in 5 mins", 
  "reminder_text": "Remember to take a break",
  "time_input": "5 minutes",
  "reminder_time": "{(date_now + timedelta(minutes=5)).strftime('%d/%m/%Y %H:%M:%S')}"
}}
{{"message": "Remind me at 10am tomorrow for the meeting", 
  "reminder_text": "Meeting at 10am",
  "time_input": "10am tomorrow",
  "reminder_time": "{(date_now + timedelta(days=1)).replace(hour=10, minute=0, second=0).strftime('%d/%m/%Y %H:%M:%S')}"
}}
"""

print(completion.choices[0].message.content)

def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts JSON from response text, handling code blocks and multiline content.
    Removes comments before parsing.
    """
    def remove_comments(json_str):
        json_str = re.sub(r'#.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        return json_str

    # First try to find JSON within code blocks
    code_block_pattern = r'```json\s*([\s\S]*?)\s*```'
    code_block_match = re.search(code_block_pattern, response_text)
    
    if code_block_match:
        try:
            json_str = code_block_match.group(1)
            json_str = remove_comments(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # If no code block or invalid JSON, try general JSON pattern
    json_pattern = r'(?s)\{.*?\}(?=\s*$)'
    json_match = re.search(json_pattern, response_text)
    
    if json_match:
        try:
            json_str = json_match.group(0)
            json_str = remove_comments(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return None