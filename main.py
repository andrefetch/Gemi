import os
import argparse
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import available_functions
from functions.get_files_info import schema_get_files_info

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# Deprecated
# prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."

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

config = types.GenerateContentConfig(
    tools=[available_functions],
    system_instruction=system_prompt,
    temperature=0
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=messages,
    config=config,
)

if response.usage_metadata is None:
    raise RuntimeError("Prompt is empty, or there is an internal error.")

'''
Function Definitions
'''

def main() -> str:
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\n")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}\n")

    if not response.function_calls:
        print(f"{response.text}")
    else:
        for func_calls in response.function_calls:
            print(f"Calling function: {func_calls.name}({func_calls.args})")

if __name__ == "__main__":
    main()
