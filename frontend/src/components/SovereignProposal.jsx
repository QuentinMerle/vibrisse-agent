import React from 'react';
import './SovereignProposal.css';
import { useTranslation } from 'react-i18next';

const SovereignProposal = ({ proposal, onAccept, onDecline }) => {
    const { t } = useTranslation();

    if (!proposal) return null;

    const isToCloud = proposal.direction === 'to_cloud';

    return (
        <div className="sovereign-proposal-overlay">
            <div className="sovereign-proposal-card">
                <div className="sovereign-proposal-header">
                    <div className="sovereign-icon">{isToCloud ? '🚀' : '🛡️'}</div>
                    <h3>{isToCloud ? 'Offload Boost' : 'Sovereign Routing'}</h3>
                </div>
                <div className="sovereign-proposal-body">
                    <p>
                        <strong>{isToCloud ? 'Analyse lourde détectée !' : 'Opportunité d\'économie détectée !'}</strong><br />
                        {isToCloud 
                            ? "Cette tâche demande une grande puissance de raisonnement. Voulez-vous passer sur un modèle Cloud pour plus de précision ?"
                            : "Cette tâche est purement technique. Vous pouvez économiser vos tokens Cloud en utilisant un modèle local."
                        }
                    </p>
                    <div className="sovereign-metrics">
                        <span>{isToCloud ? 'Précision : Maximale 💎' : 'Coût : Gratuit 🌿'}</span>
                        <span>{isToCloud ? 'Vitesse : Ultra ⚡' : 'Confidentialité : Totale 🔒'}</span>
                    </div>
                </div>
                <div className="sovereign-proposal-footer">
                    <button className="sovereign-btn-decline" onClick={onDecline}>
                        {isToCloud ? 'Rester en Local' : 'Rester sur le Cloud'}
                    </button>
                    <button className="sovereign-btn-accept" onClick={onAccept}>
                        {isToCloud ? 'Passer sur le Cloud' : 'Utiliser le modèle local'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SovereignProposal;
