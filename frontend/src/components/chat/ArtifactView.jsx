import React from 'react';
import { FileText, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import MermaidDiagram from './MermaidDiagram';
import CodeDiff from './CodeDiff';
import CodeBlock from './CodeBlock';
import './ArtifactView.css';

const ArtifactView = ({ id, content, type = 'plan' }) => {
  return (
    <div className="artifact-container">
      <div className="artifact-header">
        <FileText size={16} className="artifact-icon" />
        <span className="artifact-title">Artefact: {id}</span>
      </div>
      <div className="artifact-body markdown-body">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            code({node, inline, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '');
              const language = match ? match[1] : '';
              
              if (!inline && language === 'mermaid') {
                return <MermaidDiagram chart={String(children).replace(/\n$/, '')} />;
              } else if (!inline && language === 'diff') {
                return <CodeDiff diffString={String(children).replace(/\n$/, '')} />;
              }
              
              return !inline && match ? (
                <CodeBlock language={language} children={String(children).replace(/\n$/, '')} />
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default ArtifactView;
