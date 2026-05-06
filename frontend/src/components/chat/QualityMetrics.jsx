import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Target, Zap, Activity, Info } from 'lucide-react';
import { api } from '../../services/api';
import './QualityMetrics.css';

export default function QualityMetrics({ message, question }) {
  const { t } = useTranslation();
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  // On ne lance l'évaluation que si on a du contexte et une réponse complète
  const canEvaluate = message.context && message.context.length > 0 && message.content && !message.isLoading;

  const runEvaluation = async () => {
    if (loading || scores) return;
    setLoading(true);
    setError(false);

    try {
      const data = await api.evaluateRAG({
        question: question,
        contexts: message.context,
        generation: message.content
      });
      
      if (data.status === "error") throw new Error(data.message || "Erreur inconnue");
      setScores(data);
    } catch (err) {
      console.error("Evaluation failed:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  if (!canEvaluate) return null;

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'var(--success-color, #10b981)';
    if (score >= 0.5) return 'var(--warning-color, #f59e0b)';
    return 'var(--error-color, #ef4444)';
  };

  return (
    <div className="quality-metrics-container">
      {!scores && !loading && !error && (
        <div className="eval-trigger-group">
          <button className="eval-trigger-btn" onClick={runEvaluation}>
            <ShieldCheck size={12} />
            <span>{t('ragas.verify_btn')}</span>
          </button>
          <div className="eval-info-tip" data-tooltip={t('ragas.info_tip')}>
            <Info size={12} />
          </div>
        </div>
      )}

      {loading && (
        <div className="eval-loading">
          <Activity size={12} className="animate-pulse" />
          <span>{t('ragas.analyzing')}</span>
        </div>
      )}

      {error && (
        <div className="eval-error">
          <span>{t('ragas.error')}</span>
          <button onClick={runEvaluation}>{t('ragas.retry')}</button>
        </div>
      )}

      {scores && (
        <div className="metrics-row" onClick={() => setScores(null)} style={{ cursor: 'pointer' }} title={t('ragas.recalculate_tip')}>
          <div className="metric-item" title={t('ragas.faithfulness_tip')}>
            <ShieldCheck size={12} style={{ color: getScoreColor(scores.faithfulness) }} />
            <span className="label">{t('ragas.faithfulness')}</span>
            <span className="value">{(scores.faithfulness * 100).toFixed(0)}%</span>
          </div>
          
          <div className="metric-item" title={t('ragas.relevancy_tip')}>
            <Target size={12} style={{ color: getScoreColor(scores.answer_relevancy) }} />
            <span className="label">{t('ragas.relevancy')}</span>
            <span className="value">{(scores.answer_relevancy * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
    </div>
  );
}
