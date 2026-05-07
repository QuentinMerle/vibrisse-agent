import os
from langchain_core.tools import tool
import subprocess
from app.core.config import settings

@tool
def web_search(query: str):
    """Search the web for up-to-date information (weather, news, latest docs, API changes). Use when local RAG is insufficient."""
    tavily_key = settings.TAVILY_API_KEY
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
        try:
            from langchain_tavily import TavilySearch
            search = TavilySearch(max_results=3)
            results = search.invoke(query)
            if isinstance(results, str):
                return results[:4000]
            elif isinstance(results, list):
                clean_text = ""
                for i, res in enumerate(results):
                    snippet = res.get("content", str(res))[:1000]
                    clean_text += f"\n[Source {i+1}]: {snippet}\n"
                return clean_text
            else:
                return str(results)[:4000]
        except Exception as e:
            print(f"⚠️ Tavily failure: {e}", flush=True)

    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        result = search.invoke(query)
        return f"\n[Web Source (DuckDuckGo)]: {result[:3000]}\n"
    except Exception as e:
        return f"Critical error: Unable to access the web ({str(e)})"

@tool
def run_terminal_command(command: str):
    """Execute a terminal command to get system info (versions, files, config, hardware) or perform actions. Use primarily for any local environment questions."""
    try:
        forbidden = ["rm -rf", "format", "mkfs", "> /dev/sda", "dd if=", ":(){ :|:& };:"]
        if any(f in command for f in forbidden):
            return "Error: Command deemed dangerous and blocked by security system."

        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=30
        )
        output = result.stdout if result.stdout else result.stderr
        if len(output) > 3000:
            output = output[:3000] + "\n... [Output truncated at 3000 chars]"
        return output if output else "Command executed successfully (no output)."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Execution error: {str(e)}"

@tool
def write_file(filename: str, content: str):
    """Create or update a file with the specified content. Useful for saving articles, code, or documentation."""
    from pathlib import Path
    try:
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        file_path = (target_dir / filename).absolute()
        
        if not str(file_path).startswith(str(target_dir)):
            return f"Error: Attempted to write outside authorized project directory ({target_dir})."

        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Success: File '{filename}' written successfully ({len(content)} characters)."
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def list_dir(directory: str = "."):
    """List files and folders in a specific directory. Useful for understanding project structure."""
    from pathlib import Path
    try:
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        path = (target_dir / directory).absolute()
        
        if not str(path).startswith(str(target_dir)):
            return "Error: Access outside project directory forbidden."
            
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist."
            
        items = os.listdir(path)
        items = [i for i in items if not i.startswith('.') and i != "node_modules" and i != "__pycache__"]
        
        return f"Content of {directory} :\n" + "\n".join(sorted(items))
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@tool
def read_file(filename: str):
    """Read the complete content of a file. Use when RAG doesn't provide enough detail for a specific file."""
    from pathlib import Path
    try:
        clean_name = filename.lstrip("@").lstrip("./")
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        path = (target_dir / clean_name).absolute()
        
        if not str(path).startswith(str(target_dir)):
            return "Error: Access outside project directory forbidden."
            
        if not path.is_file():
            return f"Error: '{filename}' is not a valid file."
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(5000)
            if len(content) >= 5000:
                content += "\n... [File truncated at 5000 characters]"
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def grep_search(pattern: str, directory: str = "."):
    """Search for a string or pattern within project files. Ideal for finding specific variables or function calls."""
    import subprocess
    from pathlib import Path
    try:
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        cmd = f"grep -rnI --exclude-dir={{node_modules,__pycache__,.git}} \"{pattern}\" {target_dir / directory}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout
        
        if not output:
            return f"No results found for '{pattern}'."
            
        if len(output) > 3000:
            output = output[:3000] + "\n... [Too many results, truncated]"
            
        return output
    except Exception as e:
        return f"Error during grep: {str(e)}"
