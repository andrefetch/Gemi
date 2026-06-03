from rich.markup import escape

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from .agent import Agent

MAX_RESULT_CHARS = 1000
SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

# Typewriter effect for Gemi's replies.
TYPE_INTERVAL = 0.012  # seconds between ticks
TYPE_CHARS_PER_TICK = 2  # baseline characters revealed per tick

class GemiApp(App):

    TITLE = "Gemi"
    SUB_TITLE = "Agentic File Assistant"

    CSS = """
    #chat {
        border: round $primary;
        padding: 0 1;
        margin: 0 1;
    }
    #chat Static {
        margin-bottom: 1;
        height: auto;
    }
    #thinking {
        height: 1;
        margin: 0 2;
        text-style: bold;
        color: $warning;
        display: none;
    }
    Input {
        dock: bottom;
        margin: 0 1 1 1;
    }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent()
        self._tokens = 0
        self._spinner_index = 0
        self._spinner_timer = None
        self._type_text = ""
        self._type_index = 0
        self._type_timer = None
        self._type_widget = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="chat")
        yield Static(id="thinking")
        yield Input(placeholder="Ask Gemi.. (Quit with Cntrl + C)")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def _add_message(self, markup: str) -> Static:
        """Append a message widget to the chat and scroll to it."""
        chat = self.query_one("#chat", VerticalScroll)
        message = Static(markup, markup=True)
        chat.mount(message)
        chat.scroll_end(animate=False)
        return message

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt:
            return
        self._add_message(f"[bold cyan]You[/]: {escape(prompt)}")
        event.input.value = ""
        event.input.disabled = True
        self._start_thinking()
        self.run_agent(prompt)

    @work(thread=True, exclusive=True)
    def run_agent(self, prompt: str) -> None:
        try:
            for ev in self.agent.send(prompt, verbose=True):
                if ev.kind == "usage":
                    self.call_from_thread(self._set_tokens, int(ev.text))
                elif ev.kind == "function_call":
                    self.call_from_thread(
                        self._add_message, f"[yellow]→ calling[/] [dim]{escape(ev.text)}"
                    )
                elif ev.kind == "function_result":
                    text = ev.text
                    if len(text) > MAX_RESULT_CHARS:
                        text = text[:MAX_RESULT_CHARS] + " …[truncated]"
                    self.call_from_thread(self._add_message, f"[dim]  {escape(text)}[/]")
                elif ev.kind == "text":
                    self.call_from_thread(self._start_typing, ev.text)
                elif ev.kind == "error":
                    self.call_from_thread(
                        self._add_message, f"[bold red]error[/] {escape(ev.text)}"
                    )
        except Exception as exc:
            self.call_from_thread(
                self._add_message, f"[bold red]error[/] {escape(str(exc))}"
            )
        finally:
            self.call_from_thread(self._finish_turn)

    def _finish_turn(self) -> None:
        self._stop_thinking()
        # If Gemi is still typing out its reply, let the typewriter
        # re-enable the input once it finishes.
        if self._type_timer is None:
            self._reenable_input()

    def _reenable_input(self) -> None:
        widget = self.query_one(Input)
        widget.disabled = False
        widget.focus()

    def _start_typing(self, text: str) -> None:
        """Reveal Gemi's reply character by character, in place in the chat."""
        self._stop_thinking()
        text = text or ""
        if not text:
            return
        self._type_text = text
        self._type_index = 0
        self._type_widget = self._add_message("[bold green]Gemi[/]: ")
        if self._type_timer is not None:
            self._type_timer.stop()
        self._type_timer = self.set_interval(TYPE_INTERVAL, self._type_tick)

    def _type_tick(self) -> None:
        # Scale speed so long replies don't take forever to type out.
        step = max(TYPE_CHARS_PER_TICK, len(self._type_text) // 200)
        self._type_index = min(self._type_index + step, len(self._type_text))
        shown = escape(self._type_text[: self._type_index])
        if self._type_widget is not None:
            self._type_widget.update(f"[bold green]Gemi[/]: {shown}")
        self.query_one("#chat", VerticalScroll).scroll_end(animate=False)
        if self._type_index >= len(self._type_text):
            self._finish_typing()

    def _finish_typing(self) -> None:
        if self._type_timer is not None:
            self._type_timer.stop()
            self._type_timer = None
        self._type_text = ""
        self._type_index = 0
        self._type_widget = None
        self._reenable_input()

    def _start_thinking(self) -> None:
        self._tokens = 0
        self._spinner_index = 0
        self.query_one("#thinking", Static).display = True
        self._render_thinking()
        self._spinner_timer = self.set_interval(0.1, self._tick_spinner)

    def _stop_thinking(self) -> None:
        if self._spinner_timer is not None:
            self._spinner_timer.stop()
            self._spinner_timer = None
        self.query_one("#thinking", Static).display = False

    def _tick_spinner(self) -> None:
        self._spinner_index = (self._spinner_index + 1) % len(SPINNER_FRAMES)
        self._render_thinking()

    def _set_tokens(self, tokens: int) -> None:
        self._tokens = tokens
        self._render_thinking()

    def _render_thinking(self) -> None:
        frame = SPINNER_FRAMES[self._spinner_index]
        self.query_one("#thinking", Static).update(
            f"{frame} Gemi is thinking… [dim]{self._tokens:,} tokens[/]"
        )


def main() -> None:
    GemiApp().run()


if __name__ == "__main__":
    main()
