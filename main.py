import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."

if api_key is None:
    raise RuntimeError("API Key is missing or not found.")

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=prompt
)

if response.usage_metadata is None:
    raise RuntimeError("Prompt is empty, or there is an internal error.")

'''
Function Definitions
'''

def main():
    print(f"User prompt: {prompt}\n")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\n")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}\n")
    print(f"Reponse: {response.text}")


if __name__ == "__main__":
    main()
