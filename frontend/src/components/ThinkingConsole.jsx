import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Brain, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import './ThinkingConsole.css';

export default function ThinkingConsole({ content, isComplete }) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(true);

  if (!content) return null;

  // Nettoyage des balises internes qui pourraient fuiter (ex: <content>, <call>, etc.)
  const cleanContent = content
    .replace(/<\/?content>/gi, '')
    .replace(/<\/?call>/gi, '')
    .replace(/<\/?thought>/gi, '')
    .replace(/<\/?thinking>/gi, '')
    .trim();

  return (
    <div className={`thinking-accordion ${isOpen ? "open" : "closed"} ${isComplete ? "complete" : "active"}`}>
      <button 
        className="accordion-header" 
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label={isComplete ? t('chat.thinking.complete') : t('chat.thinking.active')}
      >
        <div className="accordion-header-left">
          <div className={`think-icon-wrap ${!isComplete ? "spin" : ""}`}>
            {isComplete
              ? <Sparkles size={14} className="think-icon-done" aria-hidden="true" />
              : <Brain size={14} className="think-icon-live" aria-hidden="true" />
            }
          </div>
          <span className="think-label">
            {isComplete ? t('chat.thinking.complete') : t('chat.thinking.active')}
          </span>
          {!isComplete && (
            <div className="dots" aria-hidden="true">
              <span /><span /><span />
            </div>
          )}
        </div>
        <div className="accordion-header-right">
          {isComplete && <span className="think-badge">✓</span>}
          {isOpen ? <ChevronUp size={13} className="chevron" aria-hidden="true" /> : <ChevronDown size={13} className="chevron" aria-hidden="true" />}
        </div>
      </button>

      {isOpen && (
        <div className="thinking-console-content" role="status" aria-live="polite">
          {!isComplete && <div className="scan-line" />}
          <div className="console-text">
            <ReactMarkdown>{cleanContent}</ReactMarkdown>
            {!isComplete && <span className="cursor-blink" aria-hidden="true" />}
          </div>
        </div>
      )}
    </div>
  );
}
