from rich.markup import escape

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, RichLog, Static

from .agent import Agent

MAX_RESULT_CHARS = 1000
SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

class GemiApp(App):

    TITLE = "Gemi"
    SUB_TITLE = "Agentic File Assistant"

    CSS = """
    RichLog {
        border: round $primary;
        padding: 0 1;
        margin: 0 1;
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

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="chat", wrap=True, markup=True, highlight=False)
        yield Static(id="thinking")
        yield Input(placeholder="Ask Gemi.. (Quit with Cntrl + C)")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt:
            return
        log = self.query_one("#chat", RichLog)
        log.write(f"[bold cyan]You[/]: {escape(prompt)}")
        event.input.value = ""
        event.input.disabled = True
        self._start_thinking()
        self.run_agent(prompt)

    @work(thread=True, exclusive=True)
    def run_agent(self, prompt: str) -> None:
        log = self.query_one("#chat", RichLog)
        try:
            for ev in self.agent.send(prompt, verbose=True):
                if ev.kind == "usage":
                    self.call_from_thread(self._set_tokens, int(ev.text))
                elif ev.kind == "function_call":
                    self.call_from_thread(
                        log.write, f"[yellow]→ calling[/] [dim]{escape(ev.text)}"
                    )
                elif ev.kind == "function_result":
                    text = ev.text
                    if len(text) > MAX_RESULT_CHARS:
                        text = text[:MAX_RESULT_CHARS] + " …[truncated]"
                    self.call_from_thread(log.write, f"[dim]  {escape(text)}[/]")
                elif ev.kind == "text":
                    self.call_from_thread(
                        log.write, f"[bold green]Gemi[/]: {escape(ev.text)}"
                    )
                elif ev.kind == "error":
                    self.call_from_thread(
                        log.write, f"[bold red]error[/] {escape(ev.text)}"
                    )
        except Exception as exc:
            self.call_from_thread(log.write, f"[bold red]error[/] {escape(str(exc))}")
        finally:
            self.call_from_thread(self._stop_thinking)
            self.call_from_thread(self._reenable_input)

    def _reenable_input(self) -> None:
        widget = self.query_one(Input)
        widget.disabled = False
        widget.focus()

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
