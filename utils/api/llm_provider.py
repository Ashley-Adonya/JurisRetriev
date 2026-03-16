import requests
import os
import dotenv


def generate_response_openai(contents, model="gpt-5", url="https://api.openai.com/v1/responses"):
    dotenv.load_dotenv()

    result = requests.post(url, headers={
      "Authorization" : f"Bearer {os.getenv("OPENAI_API_KEY")}" ,
        'Content-Type': 'application/json',

    }, 
    json = {
       "model": model,
        "messages": contents
    }
    )
    if result.status_code == 200:
        return result.json()["choices"][0]["message"]["content"] 
        
    raise Exception(f"open ai api not working result: {result.text}")

def initialize_context(sys_prompt, user_message):
	return [
        {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
    ]
