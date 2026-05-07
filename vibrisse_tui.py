import os
import sys
import asyncio
import httpx
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.box import ROUNDED
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.patch_stdout import patch_stdout

console = Console()
BASE_URL = "http://localhost:8001/api"

class VibrisseTUI:
    def __init__(self):
        self.session = PromptSession(history=InMemoryHistory())
        self.current_model = "Unknown"
        self.current_path = os.getcwd()
        self.status = "Offline"
        self.ram_info = "N/A"
        self.thread_id = None
        self.running = True

    async def fetch_status(self):
        """Récupère les infos du backend pour mettre à jour le dashboard."""
        try:
            async with httpx.AsyncClient() as client:
                # Config
                resp_config = await client.get(f"{BASE_URL}/system/config", timeout=2.0)
                if resp_config.status_code == 200:
                    data = resp_config.json()
                    self.current_model = data.get("model", "Unknown")
                    self.current_path = data.get("target_path", ".")
                
                # Health
                resp_health = await client.get(f"{BASE_URL}/system/health", timeout=2.0)
                if resp_health.status_code == 200:
                    data = resp_health.json()
                    self.status = "● Online" if data.get("ollama") == "connected" else "○ No Ollama"
                    ram = data.get("ram", {})
                    self.ram_info = f"{ram.get('used')} / {ram.get('total')} GB ({ram.get('percent')}%)"
                else:
                    self.status = "⚠ Backend Error"
        except Exception:
            self.status = "🔴 Offline"

    def create_header(self):
        ascii_art = r"""
  _    _  _  _            _                    
 | |  | |(_)| |          (_)                   
 | |  | | _ | |__   _ __  _  ___  ___   ___   
 | |  | || || '_ \ | '__|| |/ __|/ __| / _ \  
  \ \/ / | || |_) || |   | |\__ \\__ \|  __/  
   \__/  |_||_.__/ |_|   |_||___/|___/ \___|  
        """
        banner = Text(ascii_art, style="bold #a78bfa")
        return Panel(
            Align.center(banner),
            border_style="#7b39ed",
            subtitle="[bold white]v1.1.0[/bold white] • [dim white]Swift CLI Center[/dim white]",
            box=ROUNDED
        )

    def create_dashboard(self):
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Col1", ratio=1)
        table.add_column("Col2", ratio=1)

        info_table = Table(show_header=False, box=None)
        info_table.add_row("[dim]Model:[/dim]", f"[bold #a78bfa]{self.current_model}[/bold #a78bfa]")
        info_table.add_row("[dim]Project:[/dim]", f"[#7b39ed]{os.path.basename(self.current_path)}[/#7b39ed]")
        info_table.add_row("[dim]Path:[/dim]", f"[dim]{self.current_path}[/dim]")

        status_style = "#10b981" if "Online" in self.status else ("#f59e0b" if "Ollama" in self.status else "#ef4444")
        
        tools_table = Table(show_header=False, box=None)
        tools_table.add_row("[dim]Status:[/dim]", f"[{status_style}]{self.status}[/{status_style}]")
        tools_table.add_row("[dim]RAM:[/dim]", f"[white]{self.ram_info}[/white]")
        tools_table.add_row("[dim]Thread:[/dim]", f"[dim]{self.thread_id or 'None'}[/dim]")

        table.add_row(info_table, tools_table)
        
        return Panel(
            table,
            title="[bold white]Control Center[/bold white]",
            border_style="white",
            box=ROUNDED,
            padding=(1, 2)
        )

    async def handle_command(self, cmd_input: str):
        parts = cmd_input.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "/help":
            console.print("\n[bold #7b39ed]Commandes Vibrisse Pro :[/bold #7b39ed]")
            console.print("  [bold white]/model [name][/bold white] - Liste ou change le modèle")
            console.print("  [bold white]/path [path][/bold white]  - Change le dossier du projet")
            console.print("  [bold white]/stats[/bold white]        - Détails RAM et système")
            console.print("  [bold white]/tools[/bold white]        - Liste les outils et serveurs MCP")
            console.print("  [bold white]/scan[/bold white]         - Relancer l'analyse du projet")
            console.print("  [bold white]/ui[/bold white]           - Ouvrir l'interface Web")
            console.print("  [bold white]/new[/bold white]          - Nouvelle discussion")
            console.print("  [bold white]/clear[/bold white]        - Effacer l'écran")
            console.print("  [bold white]/exit[/bold white]         - Quitter")
            console.print("")

        elif cmd == "/ui":
            webbrowser.open("http://localhost:8001")
            console.print("[green]🌍 Ouverture du Studio...[/green]")

        elif cmd == "/model":
            async with httpx.AsyncClient() as client:
                if not args:
                    resp = await client.get(f"{BASE_URL}/system/models")
                    models = resp.json().get("models", [])
                    console.print(f"\n[bold]Modèles disponibles :[/bold] {', '.join(models)}")
                else:
                    new_model = args[0]
                    resp = await client.post(f"{BASE_URL}/system/config/model", json={"model": new_model})
                    if resp.status_code == 200:
                        console.print(f"[green]✓ Modèle changé pour {new_model}[/green]")
                        await self.fetch_status()
                    else:
                        console.print(f"[red]❌ Erreur lors du changement de modèle.[/red]")

        elif cmd == "/path":
            if not args:
                console.print(f"[yellow]Usage: /path <absolute_path>[/yellow]")
            else:
                new_path = args[0]
                async with httpx.AsyncClient() as client:
                    resp = await client.post(f"{BASE_URL}/system/config/target", json={"path": new_path})
                    if resp.status_code == 200:
                        console.print(f"[green]✓ Dossier changé pour {new_path}[/green]")
                        console.print(f"[dim]Ré-indexation lancée en arrière-plan...[/dim]")
                        await self.fetch_status()
                    else:
                        console.print(f"[red]❌ Erreur : {resp.json().get('message')}[/red]")

        elif cmd == "/stats":
            await self.fetch_status()
            console.print(f"\n[bold #7b39ed]Système :[/bold #7b39ed] {self.ram_info}")
            console.print(f"[bold #7b39ed]Status :[/bold #7b39ed] {self.status}")

        elif cmd == "/tools":
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{BASE_URL}/system/mcp/status")
                data = resp.json()
                console.print(f"\n[bold #7b39ed]Serveurs MCP connectés :[/bold #7b39ed]")
                for server in data.get("details", []):
                    console.print(f"  ● [bold white]{server['id']}[/bold white] ({server['tools_count']} outils)")
                console.print(f"\n[bold #7b39ed]Outils natifs :[/bold #7b39ed] [yellow]shell, filesystem, web_search[/yellow]")

        elif cmd == "/scan":
            async with httpx.AsyncClient() as client:
                await client.post(f"{BASE_URL}/system/onboarding/reset")
                await client.post(f"{BASE_URL}/system/config/target", json={"path": self.current_path})
                console.print("[green]✓ Scan du projet relancé.[/green]")

        elif cmd == "/new":
            self.thread_id = None
            console.print("[bold #a78bfa]✨ Nouvelle discussion initialisée.[/bold #a78bfa]")

        elif cmd == "/clear":
            console.clear()
            console.print(self.create_header())

        elif cmd in ["/exit", "/quit"]:
            self.running = False

        else:
            # Simulation d'envoi de message (prototype simplifié)
            console.print(f"\n[bold #7b39ed]Vibrisse[/bold #7b39ed] [dim](thinking...)[/dim]")
            console.print("[dim]Note: Le chat interactif complet est optimisé pour l'interface Web (/ui).[/dim]")
            console.print("[white]Commande ou message reçu :[/white] " + cmd_input)

    async def start(self):
        console.clear()
        console.print(self.create_header())
        await self.fetch_status()
        
        prompt_style = PtStyle.from_dict({
            'prompt': 'bold #7b39ed',
            'at': '#a78bfa',
        })

        while self.running:
            with patch_stdout():
                try:
                    console.print(self.create_dashboard())
                    user_input = await self.session.prompt_async([
                        ('class:prompt', ' vibrisse'),
                        ('class:at', ' ❯ '),
                    ], style=prompt_style)

                    if not user_input.strip():
                        continue
                    
                    if user_input.startswith("/"):
                        await self.handle_command(user_input)
                    else:
                        await self.handle_command(user_input)
                        
                except (KeyboardInterrupt, EOFError):
                    self.running = False

        console.print("\n[bold #7b39ed]Au revoir ![/bold #7b39ed]")

if __name__ == "__main__":
    tui = VibrisseTUI()
    asyncio.run(tui.start())
