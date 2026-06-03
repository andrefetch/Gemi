import sys
import argparse

from .agent import Agent

def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot_Application")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    agent = Agent()

    for event in agent.send(args.user_prompt, verbose=args.verbose):
        if event.kind == "function_call":
            if args.verbose:
                print(f"Calling function: {event.text}")
            else:
                name = event.text.split("(", 1)[0]
                print(f" - Calling function: {name}")
        elif event.kind == "function_result":
            print(f"-> {event.text}")
        elif event.kind == "text":
            print(event.text)
        elif event.kind == "error":
            print(event.text)
            sys.exit(1)


if __name__ == "__main__":
    main()
