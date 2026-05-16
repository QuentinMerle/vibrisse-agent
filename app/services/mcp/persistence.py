import aiosqlite
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class MCPPersistence:
    """
    Gère la persistance des serveurs MCP dans une base de données locale.
    """
    
    def __init__(self):
        self.db_path = Path(settings.TARGET_PROJECT_PATH or ".") / ".vibrisse" / "mcp_servers.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS mcp_servers (
                    server_id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    args TEXT NOT NULL,
                    env TEXT,
                    workspace_path TEXT
                )
            """)
            await db.commit()

    async def save_server(self, server_id: str, command: str, args: List[str], env: Dict[str, str] = None):
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO mcp_servers (server_id, command, args, env, workspace_path) VALUES (?, ?, ?, ?, ?)",
                (server_id, command, json.dumps(args), json.dumps(env or {}), settings.TARGET_PROJECT_PATH)
            )
            await db.commit()
            logger.info(f"💾 Serveur MCP '{server_id}' sauvegardé dans la base persistante.")

    async def remove_server(self, server_id: str):
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM mcp_servers WHERE server_id = ?", (server_id,))
            await db.commit()
            logger.info(f"🗑️ Serveur MCP '{server_id}' retiré de la base persistante.")

    async def load_all_servers(self) -> List[Dict[str, Any]]:
        await self._init_db()
        servers = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT server_id, command, args, env FROM mcp_servers") as cursor:
                async for row in cursor:
                    servers.append({
                        "server_id": row[0],
                        "command": row[1],
                        "args": json.loads(row[2]),
                        "env": json.loads(row[3])
                    })
        return servers

mcp_persistence = MCPPersistence()
