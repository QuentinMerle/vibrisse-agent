import React from 'react';

const ContextGauge = ({ usage = 0, limit = 32000 }) => {
  const percent = Math.min(Math.round((usage / limit) * 100), 100);
  
  // Détermination de la couleur
  let color = 'var(--success)';
  if (percent > 85) color = 'var(--danger)';
  else if (percent > 60) color = '#f59e0b'; // Amber
  
  const formatValue = (val) => {
    if (val >= 1000) return (val / 1000).toFixed(1) + 'k';
    return val;
  };

  return (
    <div 
      className="context-gauge-container" 
      data-tooltip={`Mémoire du LLM : ${formatValue(usage)} / ${formatValue(limit)} caractères. Plus elle est pleine, plus l'agent risque d'oublier des détails.`}
    >
      <div className="context-gauge-label">
        <span>CONTEXTE</span>
        <span>{percent}%</span>
      </div>
      <div className="context-gauge-bar-bg">
        <div 
          className="context-gauge-bar-fill" 
          style={{ 
            width: `${percent}%`,
            backgroundColor: color,
            boxShadow: `0 0 8px ${color}44`
          }} 
        />
      </div>
    </div>
  );
};

export default ContextGauge;
