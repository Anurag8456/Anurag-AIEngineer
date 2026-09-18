import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = Groq(api_key=my_api_key)
# Fixed model ID to a stable endpoint
model = "qwen/qwen3.8-27b" 

knowledge_base = {
    "age" : "The age of pratyush is 25 years",
    "net worth" : "The net worth of pratyush is 2000"
}

def retrieve_info(question):
    question = question.lower()
    if "age" in question:
        return knowledge_base["age"]
    elif "net worth" in question:
        return knowledge_base["net worth"]
    else:
        return None

def ask_llm(question):
    context = retrieve_info(question)
    
    # Guardrail: Do not call the API if we have no context
    if not context:
        return "Error: Information not found in knowledge base. No API call made."

    sys_prompt = f"answer in one line only. Answer only based on this context. do not hallucinate. Context: {context}"
    system_message = {
        "role": "system",
        "content": sys_prompt
    }
    message = {
        "role": "user",
        "content": question
    }
    messages = [system_message, message]
    
    response = client.chat.completions.create(
        model=model, 
        messages=messages,
        max_tokens=100  # This forces the request well below your 1000 token limit
    )
    answer = response.choices[0].message.content
    return answer

# Fixed the typo in the query
question = "what is pratyush's agge?"
print(ask_llm(question))