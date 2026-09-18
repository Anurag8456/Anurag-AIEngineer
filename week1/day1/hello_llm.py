import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key =os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
CLIENT = Groq(api_key=my_api_key)

model="llama-3.3-70b-versatile"
role="user"
prompt="do you know Ronaldo?"
message={
    "role": role,   
    "content": prompt
}
messages=[message]
response = CLIENT.chat.completions.create(model=model, messages=messages)
print(response)

print("#############################")
answer = response.choices[0].message.content
print(answer)