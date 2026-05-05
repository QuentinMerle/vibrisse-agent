import React, { useEffect, useRef, useState } from 'react';
import { Plus, Trash2, CheckCircle2, Settings, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import ThreadList from './layout/ThreadList';
import SystemPulse from './layout/SystemPulse';
import ProjectSection from './layout/ProjectSection';
import './Sidebar.css';

const Sidebar = ({ 
  threads, currentThread, onSelectThread, onNewChat, onWipeIndex, isLoadingThreads,
  healthStatus, contextUsage, contextLimit, onUpdateTargetPath, onOpenSettings, llmSettings,
  isCollapsed, onToggle
}) => {
  const sidebarRef = useRef(null);
  const [isIndexing, setIsIndexing] = useState(false);
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const items = sidebarRef.current?.querySelectorAll('.thread-item');
        if (!items || items.length === 0) return;

        const currentIndex = Array.from(items).indexOf(document.activeElement);
        if (currentIndex === -1) return;

        e.preventDefault();
        if (e.key === 'ArrowDown') {
          const nextIndex = (currentIndex + 1) % items.length;
          items[nextIndex].focus();
        } else {
          const prevIndex = (currentIndex - 1 + items.length) % items.length;
          items[prevIndex].focus();
        }
      }
    };

    const sidebarElement = sidebarRef.current;
    sidebarElement?.addEventListener('keydown', handleKeyDown);
    return () => sidebarElement?.removeEventListener('keydown', handleKeyDown);
  }, [threads]);

  const handleUpdatePath = async (path) => {
    setIsIndexing(true);
    const success = await onUpdateTargetPath(path);
    setIsIndexing(false);
    return success;
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`} aria-label="Menu latéral" ref={sidebarRef}>
      <div className="sidebar-header">
        <button 
          className="collapse-btn" 
          onClick={onToggle} 
          title={isCollapsed ? "Développer" : "Réduire"}
        >
          {isCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
        </button>
        {!isCollapsed && <span className="sidebar-title">DISCUSSIONS</span>}
      </div>

      <button className="new-chat-btn" onClick={onNewChat} title="Démarrer une nouvelle discussion">
        <Plus size={18} aria-hidden="true" />
        {!isCollapsed && <span>Nouvelle discussion</span>}
      </button>

      {!isCollapsed && (
        <ThreadList 
          isLoadingThreads={isLoadingThreads} 
          threads={threads} 
          currentThread={currentThread} 
          onSelectThread={onSelectThread}
          isCollapsed={isCollapsed}
        />
      )}

      {isCollapsed && <div style={{ flex: 1 }}></div>}

      <div className={`sidebar-cockpit ${isCollapsed ? 'collapsed' : ''}`}>
        <SystemPulse 
          healthStatus={healthStatus} 
          contextUsage={contextUsage} 
          contextLimit={contextLimit} 
          llmSettings={llmSettings} 
          isCollapsed={isCollapsed}
        />

        <ProjectSection 
          isIndexing={isIndexing} 
          onUpdateTargetPath={handleUpdatePath} 
          setShowToast={setShowToast}
          isCollapsed={isCollapsed}
        />
      </div>

      {showToast && !isCollapsed && (
        <div className="toast-notification">
          <CheckCircle2 size={18} />
          Projet indexé !
        </div>
      )}

      <div className="sidebar-footer">
        <button className="sidebar-footer-btn" onClick={onOpenSettings} title="Paramètres Multi-LLM">
          <Settings size={16} />
          {!isCollapsed && <span>Réglages</span>}
        </button>
        <button className="sidebar-footer-btn danger" onClick={onWipeIndex} title="Réinitialiser l'index">
          <Trash2 size={16} />
          {!isCollapsed && <span>Réinitialiser</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
