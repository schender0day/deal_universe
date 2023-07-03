import os
import openai

import openai
import os

# Define the path of your API key file
file_path = "chat.txt"

# Ensure the file exists
if not os.path.exists(file_path):
    raise ValueError("API Key file does not exist")
response = openai.Completion.create(
  model="text-davinci-003",
  prompt="Convert this text to a programmatic command:\n\nExample: Ask Constance if we need some bread\nOutput: send-msg `find constance` Do we need some bread?\n\nReach out to the ski store and figure out if I can get my skis fixed before I leave on Thursday",
  temperature=0,
  max_tokens=100,
  top_p=1.0,
  frequency_penalty=0.2,
  presence_penalty=0.0,
  stop=["\n"]
)