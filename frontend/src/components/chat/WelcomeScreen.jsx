import React from 'react';
import { Sparkles, MessageSquare, Code, Search, Zap } from 'lucide-react';
import './WelcomeScreen.css';

const WelcomeScreen = ({ onSuggestionClick }) => {
  const suggestions = [
    {
      icon: <Code size={18} />,
      title: "Analyse de code",
      text: "Analyse l'architecture de ce projet et explique-moi les choix techniques.",
      action: "Analyse l'architecture de ce projet et explique-moi les choix techniques."
    },
    {
      icon: <Search size={18} />,
      title: "Recherche de bugs",
      text: "Trouve des bugs potentiels ou des failles de sécurité dans le dossier src.",
      action: "Trouve des bugs potentiels ou des failles de sécurité dans le dossier src."
    },
    {
      icon: <Zap size={18} />,
      title: "Optimisation",
      text: "Comment pourrais-je optimiser les performances de ce frontend ?",
      action: "Comment pourrais-je optimiser les performances de ce frontend ?"
    }
  ];

  return (
    <div className="welcome-screen fade-in">
      <div className="welcome-content">
        <div className="welcome-logo">
          <div className="logo-glow"></div>
          <Sparkles size={64} className="logo-icon" />
        </div>
        
        <h1 className="welcome-title">Bienvenue sur Vibrisse Agent</h1>
        <p className="welcome-subtitle">
          Votre agent expert en code est prêt. Que souhaitez-vous accomplir aujourd'hui ?
        </p>

        <div className="suggestions-grid">
          {suggestions.map((s, i) => (
            <button 
              key={i} 
              className="suggestion-card"
              onClick={() => onSuggestionClick(s.action)}
            >
              <div className="suggestion-icon-wrapper">
                {s.icon}
              </div>
              <div className="suggestion-text-wrapper">
                <span className="suggestion-title">{s.title}</span>
                <span className="suggestion-text">{s.text}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
