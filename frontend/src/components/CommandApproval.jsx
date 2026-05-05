import React from 'react';
import { ShieldAlert, Terminal, Check, X } from 'lucide-react';
import './ApprovalModal.css';

const CommandApproval = ({ command, onApprove, onCancel }) => {
  return (
    <div className="approval-overlay">
      <div className="approval-card">
        <div className="approval-header">
          <ShieldAlert className="warning-icon" size={24} />
          <h3>Validation de sécurité</h3>
        </div>
        
        <div className="approval-body">
          <p>L'agent souhaite exécuter la commande suivante sur votre système :</p>
          <div className="command-preview">
            <Terminal size={16} />
            <code>{command}</code>
          </div>
          <p className="warning-text">
            ⚠️ Attention : L'exécution de commandes terminal peut être dangereuse. 
            Vérifiez bien la commande avant de l'autoriser.
          </p>
        </div>
        
        <div className="approval-footer">
          <button className="cancel-btn" onClick={onCancel}>
            <X size={18} />
            <span>Annuler</span>
          </button>
          <button className="approve-btn" onClick={onApprove}>
            <Check size={18} />
            <span>Autoriser l'exécution</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommandApproval;
