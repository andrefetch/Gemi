import os
import sys
import argparse
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import available_functions
from functions.get_files_info import schema_get_files_info
from functions.call_function import call_function

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

'''
Function Definitions
'''

def main() -> str:

    for _ in range(20):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=messages,
            config=config,
    )  

        if response.usage_metadata is None:
            raise RuntimeError("Prompt is empty, or there is an internal error.")
        
        for candidate in response.candidates:
            messages.append(candidate.content)

        if not response.function_calls:
            print(f"{response.text}")
            break

        function_response_parts = []

        for func_calls in response.function_calls:

            function_call_result = call_function(func_calls, args.verbose)

            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

            if (function_call_result.parts) and (function_call_result.parts[0].function_response) and (function_call_result.parts[0].function_response.response):
                function_response_parts.append(function_call_result.parts[0])
            else:
                raise Exception("Error: Function call is not operating correctly.")
        
        messages.append(types.Content(role="user", parts=function_response_parts))
    
    else:
        print("Maximum iterations reached without a final response.")
        sys.exit(1)

if __name__ == "__main__":
    main()
