import React from 'react';
import { Download, CheckCircle } from 'lucide-react';

const PersonaCard = ({ 
  profile, 
  isActive, 
  isInstalled, 
  isPulling, 
  onSelect, 
  onPull 
}) => {
  return (
    <div 
      className={`persona-card card-fixed ${isActive ? 'active' : ''} ${profile.is_hero ? 'is-hero' : ''}`}
      onClick={() => onSelect(profile.id)}
      role="radio"
      aria-checked={isActive}
      tabIndex={0}
    >
      <div className="persona-icon">{profile.icon}</div>
      <div className="persona-meta">
        <h3>{profile.title}</h3>
        <p>{profile.description}</p>
      </div>

      <div className="model-actions">
        <div className={`model-suggestion ${isInstalled ? 'installed' : 'missing'}`}>
          {profile.model}
        </div>
        
        {isInstalled ? (
          <div className="installed-badge" title="Model ready">
            <CheckCircle size={14} color="#10b981" />
          </div>
        ) : (
          <button 
            className={`btn-pull-mini ${isPulling ? 'loading' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              onPull(profile.model);
            }}
            disabled={isPulling}
          >
            {isPulling ? (
              <div className="spinner-mini" />
            ) : (
              <>
                <Download size={12} />
                <span>PULL</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default PersonaCard;
