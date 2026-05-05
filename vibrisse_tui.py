import os
import sys
import time
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.box import ROUNDED
from rich.layout import Layout
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.history import InMemoryHistory

console = Console()

def create_header():
    # Correction de l'orthographe (un seul 'R') et ajout de couleurs Vibrisse
    ascii_art = r"""
  _    _  _  _            _                    
 | |  | |(_)| |          (_)                   
 | |  | | _ | |__   _ __  _  ___  ___   ___   
 | |  | || || '_ \ | '__|| |/ __|/ __| / _ \  
  \ \/ / | || |_) || |   | |\__ \\__ \|  __/  
   \__/  |_||_.__/ |_|   |_||___/|___/ \___|  
    """
    # On applique un dégradé manuel ou une couleur vive
    banner = Text(ascii_art, style="bold #a78bfa") # Violet clair
    
    # On peut même styliser les lettres individuellement si on veut être ultra-pro
    return Panel(
        Align.center(banner),
        border_style="#7b39ed", # Violet plus foncé
        subtitle="[bold white]v1.0.0-alpha[/bold white] • [dim white]Vibrisse Agent[/dim white]",
        box=ROUNDED
    )

def create_dashboard():
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Col1", ratio=1)
    table.add_column("Col2", ratio=1)

    # Info Column (Couleurs cohérentes avec la Web UI)
    info_table = Table(show_header=False, box=None)
    info_table.add_row("[dim]Model:[/dim]", "[bold #a78bfa]gemma4:e4b[/bold #a78bfa]")
    info_table.add_row("[dim]Provider:[/dim]", "Ollama (Local)")
    info_table.add_row("[dim]Context:[/dim]", "[#10b981]0 / 8192 (0%)[/#10b981]") # Vert succès conservé
    info_table.add_row("[dim]Project:[/dim]", f"[#7b39ed]{os.path.basename(os.getcwd())}[/#7b39ed]")

    # Tools Column
    tools_table = Table(show_header=False, box=None)
    tools_table.add_row("[dim]Tools:[/dim]", "[bold yellow]shell, filesystem, fetch[/bold yellow]")
    tools_table.add_row("[dim]MCP:[/dim]", "[bold yellow]memory, github, linear[/bold yellow]")
    tools_table.add_row("[dim]Status:[/dim]", "[bold #10b981]● Connected[/bold #10b981]")

    table.add_row(info_table, tools_table)
    
    return Panel(
        table,
        title="[bold white]Dashboard[/bold white]",
        border_style="white",
        box=ROUNDED,
        padding=(1, 2)
    )

def run_tui():
    console.clear()
    console.print(create_header())
    console.print(create_dashboard())
    console.print("\n[dim]Bienvenue dans Vibrisse TUI. Tapez [/dim][bold white]/help[/bold white][dim] pour les commandes.[/dim]")
    console.print("[dim]Appuyez sur [/dim][bold #ef4444]Ctrl+C[/bold #ef4444][dim] pour quitter.[/dim]\n")

    session = PromptSession(history=InMemoryHistory())
    
    prompt_style = PtStyle.from_dict({
        'prompt': 'bold #7b39ed',
        'at': '#a78bfa',
    })

    while True:
        try:
            user_input = session.prompt([
                ('class:prompt', ' vibrisse'),
                ('class:at', ' ❯ '),
            ], style=prompt_style)
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                break
                
            if user_input.lower() == '/help':
                console.print("\n[bold #7b39ed]Commandes Vibrisse :[/bold #7b39ed]")
                console.print("  [bold white]/ui[/bold white]    - Lancer l'interface Web (Studio)")
                console.print("  [bold white]/new[/bold white]   - Nouvelle discussion")
                console.print("  [bold white]/clear[/bold white] - Effacer l'écran")
                console.print("  [bold white]/exit[/bold white]  - Quitter la TUI")
                console.print("")
                continue

            if user_input.lower() == '/ui':
                console.print("\n[bold #10b981]🌍 Ouverture de l'interface Studio...[/bold #10b981]")
                webbrowser.open("http://localhost:8001")
                continue

            if user_input.lower() == '/new':
                console.print("\n[bold #a78bfa]✨ Nouvelle session initialisée.[/bold #a78bfa]\n")
                # On pourrait ici appeler l'API pour reset
                continue

            if user_input.lower() == '/clear':
                run_tui()
                continue

            # Simulation de réponse stylisée
            console.print(f"\n[bold #7b39ed]Vibrisse[/bold #7b39ed] [dim](thinking...)[/dim]")
            time.sleep(0.5)
            console.print("[white]Désolé, la connexion au backend n'est pas encore implémentée dans ce prototype TUI.[/white]\n")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break

    console.print("\n[bold #7b39ed]Au revoir ![/bold #7b39ed]")

if __name__ == "__main__":
    run_tui()
