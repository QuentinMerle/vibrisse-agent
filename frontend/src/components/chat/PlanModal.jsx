import React from 'react';
import { X, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from './CodeBlock';
import './PlanModal.css';

const PlanModal = ({ isOpen, onClose, plan, pendingPlan, onPlanApproval }) => {
  return (
    <>
      {/* Backdrop transparent pour fermer au clic en dehors de la sidebar */}
      {isOpen && <div className="sidebar-backdrop" onClick={onClose} />}
      
      <div className={`plan-sidebar obsidian-glass ${isOpen ? 'open' : ''}`}>
        <div className="modal-header">
          <div className="header-title">
            <FileText className="header-icon" size={20} />
            <h2>Plan d'Implémentation</h2>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-body markdown-body text">
          {plan ? (
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <CodeBlock language={match[1]} children={children} />
                  ) : (
                    <code className="inline-code" {...props}>{children}</code>
                  );
                }
              }}
            >
              {plan}
            </ReactMarkdown>
          ) : (
            <div className="empty-state">Aucun plan disponible.</div>
          )}
        </div>

        {pendingPlan && (
          <div className="modal-footer plan-modal-footer">
            <button className="secondary-btn reject-btn" onClick={() => { onPlanApproval(false); onClose(); }}>
              Rejeter
            </button>
            <button className="primary-btn approve-btn" onClick={() => { onPlanApproval(true); onClose(); }}>
              Approuver le plan
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default PlanModal;
