import { useEffect, useRef } from "react";
import { AlertTriangle, Check, X } from "lucide-react";
import './ApprovalModal.css';

export default function ApprovalModal({ pendingAction, onApprove, onReject }) {
  const modalRef = useRef(null);

  // Gestion du piège de focus (Focus Trap)
  useEffect(() => {
    if (!pendingAction) return;

    const modalElement = modalRef.current;
    if (!modalElement) return;

    // Liste des éléments focusables
    const focusableElements = modalElement.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus initial sur le bouton "Approuver" (le plus important/sécurisé d'un point de vue UX ici ?)
    // Ou sur le bouton "Rejeter" pour plus de sécurité. Choisissons "Approuver".
    const approveBtn = modalElement.querySelector('.btn-approve');
    approveBtn?.focus();

    const handleKeyDown = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) { // Shift + Tab
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else { // Tab
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }

      if (e.key === 'Escape') {
        onReject();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    
    // Empêcher le scroll du body quand la modale est ouverte
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [pendingAction, onReject]);

  if (!pendingAction) return null;

  const command = pendingAction[0]?.args?.command || "Commande inconnue";

  return (
    <div className="approval-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="approval-card" ref={modalRef}>
        <div className="approval-header">
          <AlertTriangle size={24} aria-hidden="true" />
          <h2 id="modal-title">Action requise</h2>
        </div>
        
        <p style={{ color: "var(--text-secondary)", lineHeight: "1.5" }}>
          L'agent demande l'autorisation d'exécuter la commande suivante sur votre système :
        </p>
        
        <div className="command-box">
          <span aria-hidden="true">&gt;</span> <code>{command}</code>
        </div>
        
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          Assurez-vous de comprendre cette commande avant de l'approuver.
        </p>

        <div className="approval-actions">
          <button className="btn-reject" onClick={onReject} aria-label="Rejeter et annuler l'action">
            <X size={18} style={{ marginRight: "8px", verticalAlign: "middle" }} aria-hidden="true" />
            Rejeter
          </button>
          <button className="btn-approve" onClick={onApprove} aria-label="Approuver et exécuter la commande">
            <Check size={18} style={{ marginRight: "8px", verticalAlign: "middle" }} aria-hidden="true" />
            Approuver
          </button>
        </div>
      </div>
    </div>
  );
}
