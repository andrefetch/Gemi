import os
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .prompts import system_prompt
from .functions.call_function import available_functions, call_function

@dataclass
class AgentEvent:

    kind: str
    text: str


class Agent:
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        max_iterations: int = 20,
    ) -> None:
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key is missing or not found.")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_iterations = max_iterations
        self.messages: list[types.Content] = []
        self.config = types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        )

    def send(self, user_prompt: str, verbose: bool = False):
        """Run one turn for `user_prompt`, yielding AgentEvents as it goes."""
        self.messages.append(
            types.Content(role="user", parts=[types.Part(text=user_prompt)])
        )

        for _ in range(self.max_iterations):
            response = self.client.models.generate_content(
                model=self.model,
                contents=self.messages,
                config=self.config,
            )

            if response.usage_metadata is None:
                yield AgentEvent("error", "Prompt is empty, or there is an internal error.")
                return

            for candidate in response.candidates:
                self.messages.append(candidate.content)

            if not response.function_calls:
                yield AgentEvent("text", response.text or "")
                return

            function_response_parts = []
            for func_call in response.function_calls:
                call_args = dict(func_call.args) if func_call.args else {}
                yield AgentEvent("function_call", f"{func_call.name}({call_args})")

                result = call_function(func_call, verbose)
                part = result.parts[0] if result.parts else None
                response_payload = (
                    part.function_response.response
                    if part and part.function_response
                    else None
                )

                if part and response_payload:
                    if verbose:
                        yield AgentEvent("function_result", str(response_payload))
                    function_response_parts.append(part)
                else:
                    yield AgentEvent("error", "Function call is not operating correctly.")
                    return

            self.messages.append(
                types.Content(role="user", parts=function_response_parts)
            )

        yield AgentEvent("error", "Maximum iterations reached without a final response.")
