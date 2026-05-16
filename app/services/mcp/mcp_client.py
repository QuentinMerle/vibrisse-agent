import os
import asyncio
import logging
from typing import List, Dict, Optional
from contextlib import AsyncExitStack

# Le SDK officiel d'Anthropic pour le MCP
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from langchain_core.tools import StructuredTool
from app.services.mcp.persistence import mcp_persistence

logger = logging.getLogger(__name__)

class MCPManager:
    """
    Gestionnaire global pour les serveurs MCP.
    Maintient les connexions actives et traduit les outils MCP en outils LangChain.
    """
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self._exit_stacks: Dict[str, AsyncExitStack] = {}

    async def connect_stdio(self, server_id: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None, persist: bool = True):
        """Connecte l'agent à un serveur MCP local via la ligne de commande (stdio)."""
        if server_id in self.sessions:
            logger.info(f"Le serveur MCP {server_id} est déjà connecté.")
            return

        # On prépare l'environnement pour le sous-processus (ex: clés API pour le serveur MCP)
        server_env = os.environ.copy()
        if env:
            server_env.update(env)
            
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=server_env
        )
        
        try:
            # On utilise AsyncExitStack pour garder le flux ouvert "indéfiniment" en tâche de fond
            stack = AsyncExitStack()
            self._exit_stacks[server_id] = stack
            
            # 1. Ouverture du processus
            stdio_ctx = stdio_client(server_params)
            read_stream, write_stream = await stack.enter_async_context(stdio_ctx)
            
            # 2. Initialisation de la session MCP
            session = ClientSession(read_stream, write_stream)
            await stack.enter_async_context(session)
            
            await session.initialize()
            self.sessions[server_id] = session
            
            # 3. Sauvegarde persistante
            if persist:
                await mcp_persistence.save_server(server_id, command, args, env)
            
            logger.info(f"✅ Serveur MCP '{server_id}' connecté avec succès.")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion au serveur MCP '{server_id}': {e}")
            if server_id in self._exit_stacks:
                await self._exit_stacks[server_id].aclose()
                del self._exit_stacks[server_id]
            raise

    async def load_persistent_servers(self):
        """Recharge tous les serveurs sauvegardés au démarrage."""
        logger.info("🔌 Reconnexion automatique des serveurs MCP...")
        servers = await mcp_persistence.load_all_servers()
        for s in servers:
            try:
                # On ne persiste pas à nouveau ce qu'on vient de charger
                await self.connect_stdio(s["server_id"], s["command"], s["args"], s["env"], persist=False)
            except Exception as e:
                logger.error(f"Échec de reconnexion auto pour {s['server_id']}: {e}")

    async def get_langchain_tools(self, server_id: str) -> List[StructuredTool]:
        """Récupère les outils du serveur MCP et les traduit au format LangChain (@tool)."""
        if server_id not in self.sessions:
            logger.warning(f"Impossible de récupérer les outils : Serveur '{server_id}' non connecté.")
            return []
            
        session = self.sessions[server_id]
        response = await session.list_tools()
        
        lc_tools = []
        for mcp_tool in response.tools:
            
            # Fonction asynchrone qui sera appelée par le LLM
            async def run_tool(**kwargs) -> str:
                try:
                    res = await session.call_tool(mcp_tool.name, arguments=kwargs)
                    # res.content est une liste d'objets TextContent ou ImageContent
                    return "\n".join([content.text for content in res.content if hasattr(content, "text")])
                except Exception as e:
                    return f"Erreur de l'outil {mcp_tool.name}: {e}"

            # Traduction magique : on convertit la définition du serveur en un "StructuredTool" LangChain
            lc_tool = StructuredTool.from_function(
                func=None,
                coroutine=run_tool,
                name=mcp_tool.name,
                description=mcp_tool.description
            )
            lc_tools.append(lc_tool)
            
        return lc_tools
        
    async def disconnect(self, server_id: str):
        """Coupe la connexion proprement."""
        if server_id in self._exit_stacks:
            await self._exit_stacks[server_id].aclose()
            del self._exit_stacks[server_id]
            if server_id in self.sessions:
                del self.sessions[server_id]
            
            # Suppression persistante
            await mcp_persistence.remove_server(server_id)
            
            logger.info(f"Serveur MCP '{server_id}' déconnecté.")

# Instance unique globale (Singleton) pour que toute l'application partage les mêmes connexions
mcp_manager = MCPManager()
