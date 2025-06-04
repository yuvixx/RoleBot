import wikipedia
import google.generativeai as genai
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
import textwrap

load_dotenv()

console = Console()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    console.print("[bold red]❌ GEMINI_API_KEY not set in .env[/bold red]")
    exit(1)

genai.configure(api_key=API_KEY)

def get_character_data(name):
    try:
        page = wikipedia.page(name)
        return page.title, page.summary
    except wikipedia.exceptions.DisambiguationError as e:
        console.print("\n[bold yellow]⚠️ Ambiguous name. Did you mean one of these?[/bold yellow]")
        for option in e.options[:5]:
            console.print(f" - [cyan]{option}[/cyan]")
        return None, None
    except Exception as ex:
        console.print(f"[bold red]❌ Error fetching character data: {ex}[/bold red]")
        return None, None

def initialize_chat(summary):
    system_prompt = (
        "You are roleplaying as the following historical or fictional figure:\n\n"
        f"{summary}\n\n"
        "Respond in first person, stay in character, and do not break character."
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        convo = model.start_chat(history=[{"role": "user", "parts": [system_prompt]}])
        return convo
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start chat: {e}[/bold red]")
        return None

def main():
    console.print("\n[bold green]🤖 Gemini Character Roleplay Chatbot[/bold green]")
    console.print("[italic]Type the name of a person (e.g., 'Albert Einstein') or character (e.g., 'Sherlock Holmes').[/italic]\n")
    
    character = Prompt.ask("[bold blue]🎭 Enter character name[/bold blue]").strip()
    name, summary = get_character_data(character)
    if not summary:
        console.print("[bold red]Exiting...[/bold red]")
        return

    convo = initialize_chat(summary)
    if not convo:
        console.print("[bold red]Exiting...[/bold red]")
        return

    console.print(Panel.fit(f"You are now chatting with [bold magenta]{name}[/bold magenta]. Type 'exit' to quit.\n", style="green"))

    while True:
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        if user_input.lower() in {"exit", "quit"}:
            console.print("\n[bold green]👋 Goodbye![/bold green]")
            break

        try:
            response = convo.send_message(user_input)
            reply = textwrap.fill(response.text, width=80)
            # Use Markdown to render if needed, else just print text
            console.print(Panel.fit(f"[magenta]{name}[/magenta]: {reply}", style="blue"))
        except Exception as e:
            console.print(f"[bold red]❌ Gemini API Error: {e}[/bold red]")
            break

if __name__ == "__main__":
    main()
