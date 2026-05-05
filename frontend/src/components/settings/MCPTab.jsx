import React from 'react';
import { Box, Trash2, RefreshCw, Plus, Plug } from 'lucide-react';

const MCPTab = ({ 
  mcpServers, 
  fetchMcpStatus, 
  handleDisconnectMcp, 
  handleConnectMcp, 
  isConnectingMcp,
  newMcpId, setNewMcpId,
  newMcpCmd, setNewMcpCmd,
  newMcpArgs, setNewMcpArgs
}) => {
  return (
    <div className="tab-content fade-in">
      <p className="settings-description">
        Connectez des serveurs Model Context Protocol (MCP) pour donner de nouveaux outils locaux à votre agent (GitHub, SQLite, etc.).
      </p>

      <div className="mcp-servers-list">
        <div className="mcp-list-header">
          <label>Serveurs Connectés</label>
          <button className="refresh-btn" onClick={fetchMcpStatus} title="Rafraîchir">
            <RefreshCw size={14} />
          </button>
        </div>
        
        {mcpServers.length === 0 ? (
          <div className="empty-state">Aucun serveur MCP connecté.</div>
        ) : (
          mcpServers.map(s => (
            <div key={s.id} className="mcp-server-item">
              <div className="mcp-info">
                <strong><Box size={14} /> {s.id}</strong>
                <span className="mcp-badge">{s.tools_count} outils</span>
              </div>
              <button className="mcp-disconnect-btn" onClick={() => handleDisconnectMcp(s.id)}>
                <Trash2 size={14} />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="mcp-add-form">
        <label>Ajouter un Serveur (Mode Stdio)</label>
        <div className="mcp-inputs">
          <input 
            type="text" 
            placeholder="ID (ex: sqlite)" 
            value={newMcpId} 
            onChange={e => setNewMcpId(e.target.value)} 
            className="mcp-input-sm"
          />
          <input 
            type="text" 
            placeholder="Commande (ex: npx)" 
            value={newMcpCmd} 
            onChange={e => setNewMcpCmd(e.target.value)}
            className="mcp-input-sm" 
          />
          <input 
            type="text" 
            placeholder="Arguments (ex: -y @modelcontextprotocol/server-sqlite --db /tmp/test.db)" 
            value={newMcpArgs} 
            onChange={e => setNewMcpArgs(e.target.value)} 
            className="mcp-input-lg"
          />
        </div>
        <button className="mcp-connect-btn" onClick={handleConnectMcp} disabled={isConnectingMcp}>
          {isConnectingMcp ? "Connexion..." : <><Plus size={14} /> Brancher le serveur</>}
        </button>
      </div>
    </div>
  );
};

export default MCPTab;
