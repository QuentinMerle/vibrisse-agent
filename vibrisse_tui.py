import os
import sys
import asyncio
import httpx
import webbrowser
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.history import InMemoryHistory

BASE_URL = "http://localhost:8001/api"

class VibrisseTUI:
    def __init__(self):
        self.session = PromptSession(history=InMemoryHistory())
        self.current_model = "Unknown"
        self.current_path = os.getcwd()
        self.status = "Offline"
        self.ram_info = "N/A"
        self.running = True

    async def fetch_status(self):
        try:
            async with httpx.AsyncClient() as client:
                resp_config = await client.get(f"{BASE_URL}/system/config", timeout=2.0)
                if resp_config.status_code == 200:
                    data = resp_config.json()
                    self.current_model = data.get("model", "Unknown")
                    self.current_path = data.get("target_path", ".")
                
                resp_health = await client.get(f"{BASE_URL}/system/health", timeout=2.0)
                if resp_health.status_code == 200:
                    data = resp_health.json()
                    self.status = "ONLINE" if data.get("ollama") == "connected" else "NO OLLAMA"
                    ram = data.get("ram", {})
                    self.ram_info = f"{ram.get('used')} / {ram.get('total')} GB ({ram.get('percent')}%)"
        except Exception:
            self.status = "OFFLINE"

    def print_dashboard(self):
        os.system('clear')
        style = PtStyle.from_dict({
            'border': '#7b39ed',
            'logo': 'bold #a78bfa',
            'label': 'ansigray',
            'value': 'bold #a78bfa',
            'success': '#10b981',
            'warn': 'bold yellow',
            'header': 'bold white',
        })
        
        ascii_logo = r"""
  _    _  _  _            _                    
 | |  | |(_)| |          (_)                   
 | |  | | _ | |__   _ __  _  ___  ___   ___   
 | |  | || || '_ \ | '__|| |/ __|/ __| / _ \  
  \ \/ / | || |_) || |   | |\__ \\__ \|  __/  
   \__/  |_||_.__/ |_|   |_||___/|___/ \___|  
        """
        
        # Header Panel
        print_formatted_text(HTML(f"<logo>{ascii_logo}</logo>"), style=style)
        print_formatted_text(HTML(f"<border>┌──────────────────────────────────────────────────────────────────┐</border>"), style=style)
        print_formatted_text(HTML(f"<border>│</border>  <header>v1.1.0-alpha</header> <ansigray>•</ansigray> <header>Vibrisse Agent Studio</header>                       <border>│</border>"), style=style)
        print_formatted_text(HTML(f"<border>└──────────────────────────────────────────────────────────────────┘</border>"), style=style)

        # Dashboard Grid
        print_formatted_text(HTML(f"<border>┌─ <header>DASHBOARD</header> ───────────────────────────────────────────────────────┐</border>"), style=style)
        
        status_color = "success" if "ONLINE" in self.status else "red"
        
        # Row 1
        line1_left = f" <label>Model:</label>    <value>{self.current_model:<15}</value> "
        line1_right = f" <label>Tools:</label>  <warn>shell, filesystem, fetch</warn> "
        print_formatted_text(HTML(f"<border>│</border>{line1_left}   {line1_right} <border>│</border>"), style=style)
        
        # Row 2
        line2_left = f" <label>Project:</label>  <project>{os.path.basename(self.current_path):<15}</project> "
        line2_right = f" <label>MCP:</label>    <warn>memory, github, linear</warn> "
        print_formatted_text(HTML(f"<border>│</border>{line2_left}   {line2_right} <border>│</border>"), style=style)

        # Row 3
        line3_left = f" <label>RAM:</label>      <white>{self.ram_info:<15}</white> "
        line3_right = f" <label>Status:</label> <{status_color}>● {self.status}</{status_color}> "
        print_formatted_text(HTML(f"<border>│</border>{line3_left}   {line3_right} <border>│</border>"), style=style)

        print_formatted_text(HTML(f"<border>└──────────────────────────────────────────────────────────────────┘</border>"), style=style)
        print_formatted_text(HTML("\n<ansigray>Bienvenue dans Vibrisse TUI. Tapez </ansigray><white><b>/help</b></white><ansigray> pour les commandes.</ansigray>"))

    async def handle_command(self, cmd_input: str):
        parts = cmd_input.split()
        if not parts: return
        cmd = parts[0].lower()
        args = parts[1:]
        
        style = PtStyle.from_dict({
            'cmd': 'bold #7b39ed',
            'help': '#a78bfa',
        })

        if cmd == "/help":
            print_formatted_text(HTML("\n<cmd>Commandes Vibrisse :</cmd>"), style=style)
            print_formatted_text(HTML("  <white><b>/model</b></white> - Liste/Change modèle"))
            print_formatted_text(HTML("  <white><b>/path</b></white>  - Change dossier"))
            print_formatted_text(HTML("  <white><b>/tools</b></white> - Serveurs MCP"))
            print_formatted_text(HTML("  <white><b>/ui</b></white>    - Interface Web"))
            print_formatted_text(HTML("  <white><b>/exit</b></white>  - Quitter\n"), style=style)
            input("Appuyez sur Entrée...")

        elif cmd == "/ui":
            webbrowser.open("http://localhost:8001")
        
        elif cmd == "/model":
            async with httpx.AsyncClient() as client:
                if not args:
                    resp = await client.get(f"{BASE_URL}/system/models")
                    models = resp.json().get("models", [])
                    print_formatted_text(HTML(f"\n<b>Modèles :</b> {', '.join(models)}"))
                else:
                    new_model = args[0]
                    await client.post(f"{BASE_URL}/system/config/model", json={"model": new_model})
                    print_formatted_text(HTML(f"\n<green>✓ Modèle : {new_model}</green>"))
                input("\nAppuyez sur Entrée...")

        elif cmd in ["/exit", "/quit"]:
            self.running = False

    async def start(self):
        await self.fetch_status()
        prompt_style = PtStyle.from_dict({
            'prompt': 'bold #7b39ed',
            'at': '#a78bfa',
        })

        while self.running:
            self.print_dashboard()
            try:
                user_input = await self.session.prompt_async([
                    ('class:prompt', ' vibrisse'),
                    ('class:at', ' > '),
                ], style=prompt_style)

                if not user_input.strip(): continue
                await self.handle_command(user_input)
                
            except (KeyboardInterrupt, EOFError):
                self.running = False

        print_formatted_text(HTML("\n<purple><b>Au revoir !</b></purple>"))

if __name__ == "__main__":
    tui = VibrisseTUI()
    asyncio.run(tui.start())
