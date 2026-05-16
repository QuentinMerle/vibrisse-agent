import pytest
import os
from pathlib import Path
from app.services.core.ghost_service import GhostService
from app.services.mcp.persistence import mcp_persistence

@pytest.mark.asyncio
async def test_ghost_mode_detection():
    """Vérifie que le GhostService détecte bien les tags dans un fichier."""
    test_content = """
    def hello():
        # @vibrisse: Ajoute une docstring
        print("hello")
    """
    test_file = "ghost_test_temp.py"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        directives = GhostService.scan_file(test_file)
        assert len(directives) == 1
        assert "Ajoute une docstring" in directives[0]
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

@pytest.mark.asyncio
async def test_mcp_persistence():
    """Vérifie que la sauvegarde et le rechargement des serveurs MCP fonctionnent."""
    server_id = "test-server"
    command = "node"
    args = ["server.js"]
    
    # On force un chemin de DB temporaire pour le test
    mcp_persistence.db_path = Path("./test_mcp.db")
    
    try:
        # 1. Sauvegarde
        await mcp_persistence.save_server(server_id, command, args)
        
        # 2. Rechargement
        servers = await mcp_persistence.load_all_servers()
        assert len(servers) >= 1
        
        test_server = next(s for s in servers if s["server_id"] == server_id)
        assert test_server["command"] == command
        assert test_server["args"] == args
        
        # 3. Suppression
        await mcp_persistence.remove_server(server_id)
        servers_after = await mcp_persistence.load_all_servers()
        assert not any(s["server_id"] == server_id for s in servers_after)
        
    finally:
        if mcp_persistence.db_path.exists():
            mcp_persistence.db_path.unlink()
