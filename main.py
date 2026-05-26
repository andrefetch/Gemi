import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."

if api_key is None:
    raise RuntimeError("API Key is missing or not found.")

'''
Parser for running user argument into the command line
'''

parser = argparse.ArgumentParser(description="Chatbot_Application")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
]

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=messages
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
