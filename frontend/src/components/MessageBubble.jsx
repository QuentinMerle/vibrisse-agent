import React, { useState } from "react";
import { useTranslation } from 'react-i18next';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, RotateCcw, Copy, Check } from "lucide-react";
import VibrisseAvatar from "./chat/VibrisseAvatar";
import ThinkingConsole from "./ThinkingConsole";
import CodeBlock from "./chat/CodeBlock";
import MessageSteps from "./chat/MessageSteps";
import { extractThinking } from "../utils/chatUtils";
import './Messages.css';

import QualityMetrics from "./chat/QualityMetrics";

export default function MessageBubble({ message, isLatest, onRetry, question }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(answer || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = message.role === "user";
  const showRetry = isLatest && isUser && !message.isLoading;

  const { thinking, answer, isComplete } = extractThinking(message.content || "");
  
  // Utilisation de l'historique propre s'il est disponible, 
  // sinon repli sur les pensées live envoyées par le backend,
  // et en dernier recours l'extraction directe du texte.
  let liveThoughts = "";
  if (message.thoughts && message.thoughts.length > 0) {
    liveThoughts = message.thoughts.join('\n\n');
  }
  const finalThoughts = message.thoughts_history ? message.thoughts_history.join('\n\n') : (liveThoughts || thinking);

  // On cache le corps du message s'il s'agit d'un appel d'outil (étape intermédiaire)
  // pour éviter les doublons si le modèle a mis du texte avant son appel.
  const isToolCall = !!(message.tool_calls && message.tool_calls.length > 0);
  const shouldShowAnswer = answer && !isToolCall;

  return (
    <div className={`message-wrapper ${isUser ? "user" : "agent"} ${message.isLoading ? "loading" : ""}`} style={{ paddingBottom: '24px' }}>
      <div className="avatar">
        {isUser ? <User size={20} /> : <VibrisseAvatar size={20} isThinking={message.isLoading} />}
      </div>
      
      <div className="message-body">
        <div className="message-content">{isUser && message.image_data && (
            <div className="message-image"><img src={message.image_data} alt="Attached" /></div>
          )}{finalThoughts && (
            <ThinkingConsole content={finalThoughts} isComplete={isComplete || !!message.thoughts_history} />
          )}{shouldShowAnswer && (
            <div className="text"><ReactMarkdown
                children={answer}
                remarkPlugins={[remarkGfm]}
                components={{
                  code({node, inline, className, children, ...props}) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <CodeBlock language={match[1]} children={children} />
                    ) : (
                      <code className="inline-code" {...props}>{children}</code>
                    );
                  },
                  h3: ({node, ...props}) => <h3 {...props} />,
                  ul: ({node, ...props}) => <ul {...props} />,
                  ol: ({node, ...props}) => <ol {...props} />,
                  li: ({node, ...props}) => <li {...props} />,
                }}
              /></div>
          )}{!isUser && (
            <div className="message-footer">
              <QualityMetrics message={message} question={question} />
              <div className="footer-right">
                <span className="timestamp">
                  {(() => {
                    const d = new Date(message.timestamp);
                    return isNaN(d.getTime()) ? new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                  })()}
                </span>
                <button 
                  className={`copy-btn ${copied ? 'copied' : ''}`}
                  onClick={handleCopy}
                  title="Copier la réponse"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                </button>
              </div>
            </div>
          )}{message.isLoading && !answer && (
            <div className="thinking-loader" style={{ marginTop: finalThoughts ? '12px' : '0' }}>
              <div className="thinking-loader-top">
                <div className="dots">
                  <span></span><span></span><span></span>
                </div>
                <span className="thinking-text">{t('chat.working')}</span>
              </div>
              {message.detail && (
                <p className="thinking-detail-subtext">
                  {message.detail}
                </p>
              )}
            </div>
          )}

          {showRetry && (
            <button className="retry-btn" onClick={() => onRetry(message.content)}>
              <RotateCcw size={14} />
              <span>{t('chat.retry_btn')}</span>
            </button>
          )}
        </div>

        {!isUser && <MessageSteps steps={message.steps} />}
      </div>
    </div>
  );
}
