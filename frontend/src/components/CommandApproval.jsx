import React from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldAlert, Terminal, Check, X } from 'lucide-react';
import './ApprovalModal.css';

const CommandApproval = ({ command, onApprove, onCancel }) => {
  const { t } = useTranslation();

  return (
    <div className="approval-overlay">
      <div className="approval-card">
        <div className="approval-header">
          <ShieldAlert className="warning-icon" size={24} />
          <h3>{t('security.approval_title')}</h3>
        </div>
        
        <div className="approval-body">
          <p>{t('security.request_msg')}</p>
          <div className="command-preview">
            <Terminal size={16} />
            <code>{command}</code>
          </div>
          <p className="warning-text">
            {t('security.warning_text')}
          </p>
        </div>
        
        <div className="approval-footer">
          <button className="cancel-btn" onClick={onCancel}>
            <X size={18} />
            <span>{t('security.cancel_btn')}</span>
          </button>
          <button className="approve-btn" onClick={onApprove}>
            <Check size={18} />
            <span>{t('security.approve_btn')}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommandApproval;
