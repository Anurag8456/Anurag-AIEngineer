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
#structured data extraction from unstructured text
from pydantic import BaseModel
class Ticket(BaseModel):
    name: str
    issue: str
    location: str
    email: str
    contact_number: str

schema = Ticket.model_json_schema()
response_format={
    "type": "json_object"
}
system_prompt=f"""return output in json format matching the schema{schema}
"""
message_system={
    "role": "system",
    "content" : system_prompt
    
}

text="Hello, i am Raj.i have an iphone which is not working properly. i live in delhi.my gmail is abc@gmail.com.my contact number is 9876543210."
prompt=f"""
This is a customer ticket. Please extract the following information from the text:
{text}
"""
message={
    "role": role,   
    "content": prompt
}
messages=[message_system,message]
response = CLIENT.chat.completions.create(model=model, messages=messages,response_format=response_format)

answer = response.choices[0].message.content
print(answer)
import json
raw_json =answer
data_file=json.loads(raw_json)

ticket = Ticket(**data_file)
print(ticket.contact_number)
print(ticket.email)
print(ticket.issue)
print(ticket.location)
print(ticket.name)