import os
import argparse
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."

if api_key is None:
    raise RuntimeError("API Key is missing or not found.")

'''
Parser for running user argument into the command lkine
'''

parser = argparse.ArgumentParser(description="Chatbot_Application")
parser.add_argument("user_prompt", type=str, help="User prompt")
args = parser.parse_args()

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=args.user_prompt
)

if response.usage_metadata is None:
    raise RuntimeError("Prompt is empty, or there is an internal error.")

'''
Function Definitions
'''

def main():
    print(f"User prompt: {args.user_prompt}\n")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\n")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}\n")
    print(f"Reponse: {response.text}")


if __name__ == "__main__":
    main()
