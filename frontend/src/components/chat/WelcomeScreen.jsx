import React from 'react';
import { useTranslation } from 'react-i18next';
import { Code, Search, Zap } from 'lucide-react';
import VibrisseAvatar from './VibrisseAvatar';
import './WelcomeScreen.css';

const WelcomeScreen = ({ onSuggestionClick }) => {
  const { t } = useTranslation();
  
  const suggestions = [
    {
      icon: <Code size={18} />,
      title: t('welcome.suggestion_code_title'),
      text: t('welcome.suggestion_code_text'),
      action: t('welcome.suggestion_code_text')
    },
    {
      icon: <Search size={18} />,
      title: t('welcome.suggestion_bug_title'),
      text: t('welcome.suggestion_bug_text'),
      action: t('welcome.suggestion_bug_text')
    },
    {
      icon: <Zap size={18} />,
      title: t('welcome.suggestion_opt_title'),
      text: t('welcome.suggestion_opt_text'),
      action: t('welcome.suggestion_opt_text')
    }
  ];

  return (
    <div className="welcome-screen fade-in">
      <div className="welcome-content">
        <div className="welcome-logo">
          <div className="logo-glow"></div>
          <VibrisseAvatar size={64} containerSize={110} />
        </div>
        
        <h1 className="welcome-title">{t('welcome.title')}</h1>
        <p className="welcome-subtitle">
          {t('welcome.subtitle')}
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
