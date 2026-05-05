import React from 'react';
import { MessageSquare, History } from 'lucide-react';

const ThreadList = ({ isLoadingThreads, threads, currentThread, onSelectThread, isCollapsed }) => {
  return (
    <nav className={`sidebar-section ${isCollapsed ? 'collapsed' : ''}`} aria-label="Historique des discussions">
      {!isCollapsed && (
        <div className="section-header" aria-hidden="true">
          <History size={14} />
          <span>Récents</span>
        </div>
      )}
      <div className="thread-list">
        {isLoadingThreads ? (
          <div className="loading-threads">
            <div className="spinner-small"></div>
            {!isCollapsed && <span>Chargement...</span>}
          </div>
        ) : threads.length === 0 ? (
          !isCollapsed && <div className="empty-threads">Aucun historique</div>
        ) : (
          <ul className="thread-list">
            {threads.map((thread) => (
              <li key={thread.id}>
                <button 
                  className={`thread-item ${currentThread === thread.id ? 'active' : ''}`}
                  onClick={() => onSelectThread(thread.id)}
                  aria-current={currentThread === thread.id ? 'true' : 'false'}
                  title={isCollapsed ? thread.title : undefined}
                >
                  <MessageSquare size={16} aria-hidden="true" />
                  {!isCollapsed && <span className="thread-label">{thread.title}</span>}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </nav>
  );
};

export default ThreadList;
