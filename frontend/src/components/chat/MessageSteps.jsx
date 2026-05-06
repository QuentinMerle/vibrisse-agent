import React from 'react';
import { useTranslation } from 'react-i18next';
import { Cpu, Database, Globe, Search, Code, CheckCircle, ListTodo } from "lucide-react";

const MessageSteps = ({ steps }) => {
  const { t } = useTranslation();
  if (!steps || steps.length === 0) return null;

  const filteredSteps = steps.filter(step => 
    !step.startsWith('reasoning') && 
    !step.startsWith('router') &&
    !['completed', 'agent_thinking', 'final_response', 'expert_review_passed'].includes(step)
  );

  if (filteredSteps.length === 0) return null;

  const getIcon = (step) => {
    if (step === 'vision_analysis' || step === 'vision_analysis_started') return <Cpu size={12} />;
    if (step.includes('code') || step.includes('reranked') || step === 'vectorstore') return <Database size={12} />;
    if (step.includes('web') || step.includes('search')) return <Globe size={12} />;
    if (step === 'intent_analysis' || step === 'router_started') return <Search size={12} />;
    if (step === 'generating_answer' || step === 'generation_started') return <Code size={12} />;
    if (step === 'planning' || step.includes('planned')) return <ListTodo size={12} />;
    if (step === 'tool_agent_execution') return <Code size={12} />;
    return <CheckCircle size={12} />;
  };

  const getLabel = (step) => {
    const mapping = {
      'intent_analysis': t('chat.steps.intent_analysis'),
      'router_started': t('chat.steps.intent_analysis'),
      'retrieving_code': t('chat.steps.retrieving_code'),
      'retrieve_code': t('chat.steps.retrieving_code'),
      'vectorstore': t('chat.steps.retrieving_code'),
      'searching_web': t('chat.steps.searching_web'),
      'web_search': t('chat.steps.searching_web'),
      'reranking': t('chat.steps.reranking'),
      'generating_answer': t('chat.steps.generating_answer'),
      'generation_started': t('chat.steps.generating_answer'),
      'vision_analysis': t('chat.steps.vision_analysis'),
      'vision_analysis_started': t('chat.steps.vision_analysis'),
      'expert_review': t('chat.steps.expert_review'),
      'expert_review_started': t('chat.steps.expert_review'),
      'planning': t('chat.steps.planning'),
      'tool_agent_planned': t('chat.steps.planning'),
      'tool_agent_execution': t('chat.steps.executing_tools'),
    };

    if (mapping[step]) return mapping[step];
    if (step.startsWith('reranked:')) return `${t('chat.steps.reranking')} (${step.split(':')[1]})`;
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
