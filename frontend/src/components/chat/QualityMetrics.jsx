import React, { useState, useEffect } from 'react';
import { ShieldCheck, Target, Zap, Activity, Info } from 'lucide-react';
import { api } from '../../services/api';
import './QualityMetrics.css';

export default function QualityMetrics({ message, question }) {
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
            <span>Vérifier la fidélité RAG</span>
          </button>
          <div className="eval-info-tip" data-tooltip="L'analyse nécessite un modèle local puissant (ex: Llama3 8B) pour être fiable.">
            <Info size={12} />
          </div>
        </div>
      )}

      {loading && (
        <div className="eval-loading">
          <Activity size={12} className="animate-pulse" />
          <span>Analyse Ragas en cours...</span>
        </div>
      )}

      {error && (
        <div className="eval-error">
          <span>Échec de l'analyse</span>
          <button onClick={runEvaluation}>Réessayer</button>
        </div>
      )}

      {scores && (
        <div className="metrics-row" onClick={() => setScores(null)} style={{ cursor: 'pointer' }} title="Cliquez pour recalculer">
          <div className="metric-item" title="Fidélité (Anti-hallucination)">
            <ShieldCheck size={12} style={{ color: getScoreColor(scores.faithfulness) }} />
            <span className="label">Fidélité:</span>
            <span className="value">{(scores.faithfulness * 100).toFixed(0)}%</span>
          </div>
          
          <div className="metric-item" title="Pertinence de la réponse">
            <Target size={12} style={{ color: getScoreColor(scores.answer_relevancy) }} />
            <span className="label">Pertinence:</span>
            <span className="value">{(scores.answer_relevancy * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
    </div>
  );
}
