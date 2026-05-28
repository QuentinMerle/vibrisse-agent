import React from 'react';
import { FileText, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ArtifactView.css';

const ArtifactView = ({ id, content, type = 'plan' }) => {
  return (
    <div className="artifact-container">
      <div className="artifact-header">
        <FileText size={16} className="artifact-icon" />
        <span className="artifact-title">Artefact: {id}</span>
      </div>
      <div className="artifact-body markdown-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default ArtifactView;
