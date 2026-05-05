import React from 'react';
import { Cpu, Database, Globe, Search, Code, CheckCircle } from "lucide-react";

const STEP_LABELS = {
  'intent_analysis': 'Analyse de l\'intention...',
  'retrieving_code': 'Recherche dans le code source...',
  'retrieve_code': 'Recherche dans le code source...',
  'searching_web': 'Recherche sur le Web...',
  'web_search': 'Recherche sur le Web...',
  'reranking': 'Optimisation des résultats...',
  'generating_answer': 'Rédaction de la réponse...',
  'vision_analysis': 'Analyse visuelle en cours...',
  'expert_review': 'Contrôle qualité expert...',
};

const MessageSteps = ({ steps }) => {
  if (!steps || steps.length === 0) return null;

  const filteredSteps = steps.filter(step => 
    !step.startsWith('reasoning') && 
    !step.startsWith('router') &&
    !['completed', 'agent_thinking', 'final_response', 'expert_review_passed'].includes(step)
  );

  if (filteredSteps.length === 0) return null;

  const getIcon = (step) => {
    if (step === 'vision_analysis') return <Cpu size={12} />;
    if (step.includes('code') || step.includes('reranked')) return <Database size={12} />;
    if (step.includes('web') || step.includes('search')) return <Globe size={12} />;
    if (step === 'intent_analysis') return <Search size={12} />;
    if (step === 'generating_answer') return <Code size={12} />;
    return <CheckCircle size={12} />;
  };

  const getLabel = (step) => {
    if (STEP_LABELS[step]) return STEP_LABELS[step];
    if (step.startsWith('reranked:')) return `Reranking: ${step.split(':')[1]} fichiers`;
    return step;
  };

  return (
    <div className="steps-container">
      <div className="message-steps">
        {filteredSteps.map((step, idx) => (
          <div key={idx} className="step-badge">
            {getIcon(step)}
            <span>{getLabel(step)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MessageSteps;
