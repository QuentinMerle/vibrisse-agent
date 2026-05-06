import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { History, FolderOpen, MapPin, Check } from 'lucide-react';

const ProjectSection = ({ isIndexing, onUpdateTargetPath, setShowToast, isCollapsed }) => {
  const { t } = useTranslation();
  const [pathValue, setPathValue] = useState("");
  const [activePath, setActivePath] = useState(localStorage.getItem("vibrisse_project_path") || "");
  const [isEditing, setIsEditing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("vibrisse_project_path");
    if (stored) {
      setActivePath(stored);
      if (!pathValue) setPathValue(stored);
    }
  }, []);

  const handleUpdate = async (path) => {
    if (!path) return;
    setIsUpdating(true);
    const success = await onUpdateTargetPath(path);
    if (success) {
      localStorage.setItem("vibrisse_project_path", path);
      setActivePath(path);
      setIsEditing(false);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    } else {
      alert("❌ " + t('project.error_invalid'));
    }
    setIsUpdating(false);
  };

  const handlePickDirectory = async () => {
    try {
      const response = await fetch('/api/system/pick-directory');
      const data = await response.json();
      if (data.status === 'success' && data.path) {
        setPathValue(data.path);
        // On ne met plus à jour automatiquement pour laisser l'utilisateur valider
      }
    } catch (error) {
      console.error("Failed to pick directory:", error);
    }
  };

  if (isCollapsed) {
    return (
      <div className="project-section collapsed" title={t('project.project_label', { path: activePath })}>
        <div className="active-project-card collapsed">
          <MapPin size={18} className="pin-icon" />
        </div>
      </div>
    );
  }

  return (
    <div className="project-section">
      <div className="section-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <History size={14} />
          <span>{t('project.target_title')}</span>
        </div>
        {isIndexing && <div className="spinner-small"></div>}
      </div>

      <div style={{ padding: '0 10px 10px' }}>
        {activePath && !isEditing ? (
          <div className="active-project-card">
            <div className="project-info-row">
              <MapPin size={14} className="pin-icon" />
              <div className="project-name-stack">
                <span className="project-folder-name">
                  {activePath === "." || activePath === "./" ? t('project.local_project') : (activePath.split('/').filter(Boolean).pop() || t('project.root'))}
                </span>
                <span className="project-full-path">{activePath}</span>
              </div>
            </div>
            <button 
              className="change-project-btn" 
              onClick={() => setIsEditing(true)}
              disabled={isIndexing}
            >
              {t('project.modify_btn')}
            </button>
          </div>
        ) : (
          <div className="project-edit-area" style={{ animation: 'fadeIn 0.3s ease-out' }}>
            <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
              <input 
                type="text" 
                placeholder={t('project.path_placeholder')}
                value={pathValue}
                onChange={(e) => setPathValue(e.target.value)}
                disabled={isIndexing}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleUpdate(pathValue);
                  if (e.key === 'Escape') setIsEditing(false);
                }}
                className="project-path-input"
                style={{
                  borderRadius: '8px',
                  padding: '6px 10px',
                  fontSize: '11px',
                  flex: 1,
                  minWidth: 0, // Crucial pour le flex
                  outline: 'none',
                  height: '32px'
                }}
              />
              
              <button 
                onClick={handlePickDirectory}
                disabled={isIndexing}
                className="pick-dir-btn"
                title={t('project.browse_tooltip')}
                style={{
                  borderRadius: '8px',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}
              >
                <FolderOpen size={14} />
              </button>

              <button 
                onClick={() => handleUpdate(pathValue)}
                disabled={isIndexing || isUpdating || !pathValue}
                className="confirm-project-btn"
                title={t('project.confirm_tooltip')}
                style={{
                  borderRadius: '8px',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'var(--primary)',
                  color: 'white',
                  border: 'none',
                  cursor: (isIndexing || isUpdating || !pathValue) ? 'not-allowed' : 'pointer',
                  flexShrink: 0
                }}
              >
                {isUpdating ? <div className="spinner-small" style={{ borderLeftColor: 'white' }}></div> : <Check size={16} />}
              </button>
            </div>
            {activePath && (
              <button className="cancel-edit-btn" onClick={() => setIsEditing(false)}>
                {t('project.cancel')}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectSection;
