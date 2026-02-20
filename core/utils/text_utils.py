import re
from rich.console import Console
from rich.panel import Panel
from core.prompts import get_subtitle_trim_prompt
from core.tts_backend.estimate_duration import init_estimator, estimate_duration
from core.utils import ask_gpt, load_key, rprint

console = Console()

# Global estimator cache
ESTIMATOR = None


def check_len_then_trim(text, duration):
    """Check if the text's estimated reading duration exceeds the given duration, and trim if necessary."""
    global ESTIMATOR

    speed_factor = {
        "min": load_key("speed_factor.min"),
        "accept": load_key("speed_factor.accept"),
        "max": load_key("speed_factor.max")
    }

    if ESTIMATOR is None:
        ESTIMATOR = init_estimator()
    estimated_duration = estimate_duration(text, ESTIMATOR) / speed_factor['max']

    console.print(f"Subtitle text: {text}, "
                  f"[bold green]Estimated reading duration: {estimated_duration:.2f} seconds[/bold green]")

    if estimated_duration > duration:
        rprint(Panel(f"Estimated reading duration {estimated_duration:.2f} seconds exceeds given duration {duration:.2f} seconds, shortening...", title="Processing", border_style="yellow"))
        original_text = text
        prompt = get_subtitle_trim_prompt(text, duration)

        def valid_trim(response):
            if 'result' not in response:
                return {'status': 'error', 'message': 'No result in response'}
            return {'status': 'success', 'message': ''}

        try:
            response = ask_gpt(prompt, resp_type='json', log_title='sub_trim', valid_def=valid_trim)
            shortened_text = response['result']
        except Exception:
            rprint("[bold red]🚫 AI refused to answer due to sensitivity, so manually remove punctuation[/bold red]")
            shortened_text = re.sub(r'[,.!?;:，。！？；：]', ' ', text).strip()

        rprint(Panel(f"Subtitle before shortening: {original_text}\nSubtitle after shortening: {shortened_text}", title="Subtitle Shortening Result", border_style="green"))
        return shortened_text
    else:
        return text

