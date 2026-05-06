import React from 'react';
import { X, AlertTriangle } from 'lucide-react';
import './ConfirmModal.css';

const ConfirmModal = ({ isOpen, onClose, onConfirm, title, message, confirmText, isDanger = true }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="confirm-modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-left">
            <AlertTriangle size={18} className={isDanger ? 'text-danger' : 'text-primary'} />
            <h3>{title}</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
        
        <div className="modal-body">
          <p>{message}</p>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Annuler
          </button>
          <button 
            className={`btn-primary ${isDanger ? 'danger' : ''}`} 
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            {confirmText || 'Confirmer'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
