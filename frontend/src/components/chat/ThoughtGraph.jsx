import React, { useMemo } from 'react';
import ReactFlow, { 
    Background, 
    Controls, 
    MiniMap,
    Handle,
    Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import './ThoughtGraph.css';

// Custom Node Style for Obsidian Glass
const CustomNode = ({ data }) => {
    return (
        <div className={`tg-node ${data.type.toLowerCase()} ${data.active ? 'active' : ''}`}>
            <Handle type="target" position={Position.Top} style={{ visibility: 'hidden' }} />
            <div className="tg-node-icon">{data.icon}</div>
            <div className="tg-node-label">{data.label}</div>
            <Handle type="source" position={Position.Bottom} style={{ visibility: 'hidden' }} />
        </div>
    );
};

const nodeTypes = {
    custom: CustomNode,
};

const ThoughtGraph = ({ nodes = [], edges = [], activeWorker = 'General' }) => {
    
    // Calcul dynamique des positions si elles ne sont pas fournies
    const layoutedNodes = useMemo(() => {
        if (!nodes || !Array.isArray(nodes)) return [];
        return nodes.map((node, index) => {
            if (node.position) return node;
            
            // Layout vertical simple par type
            let x = 250;
            let y = 0;
            
            const nodeType = node.data.type?.toUpperCase();
            if (nodeType === 'SUPERVISOR') y = 0;
            if (nodeType === 'WORKER') {
                y = 100;
                // Décalage horizontal pour les workers multiples (ex: Vision + Coder)
                const workers = nodes.filter(n => n.data.type?.toUpperCase() === 'WORKER');
                const workerIndex = workers.findIndex(n => n.id === node.id);
                x = 250 + (workerIndex * 220) - ((workers.length - 1) * 110);
            }
            if (nodeType === 'TOOL') {
                y = 200;
                // Décalage horizontal pour les outils multiples
                const tools = nodes.filter(n => n.data.type?.toUpperCase() === 'TOOL');
                const toolIndex = tools.findIndex(n => n.id === node.id);
                x = 250 + (toolIndex * 150) - ((tools.length - 1) * 75);
            }

            // Marquer le dernier nœud ajouté comme actif
            const isActive = index === nodes.length - 1;
            
            return {
                ...node,
                position: { x, y },
                data: { ...node.data, active: isActive }
            };
        });
    }, [nodes]);

    return (
        <div className="thought-graph-container">
            <ReactFlow
                nodes={layoutedNodes}
                edges={edges}
                nodeTypes={nodeTypes}
                fitView
                style={{ background: 'transparent' }}
            >
                <Background color="#333" gap={20} />
                <Controls />
            </ReactFlow>
        </div>
    );
};

export default ThoughtGraph;
