import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CheckCircle2, RotateCcw, Code } from "lucide-react";

const CodeBlock = ({ language, children }) => {
  const [copied, setCopied] = React.useState(false);
  const codeContent = String(children).replace(/\n$/, '');

  const handleCopy = () => {
    navigator.clipboard.writeText(codeContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-block-wrapper">
      <div className="code-header">
        <div className="code-header-left">
          <span className="lang-badge">{language}</span>
          <Code size={12} opacity={0.5} />
        </div>
        <button 
          className={`copy-code-btn ${copied ? 'copied' : ''}`} 
          onClick={handleCopy}
          title="Copier le code"
        >
          {copied ? <CheckCircle2 size={14} /> : <RotateCcw size={14} style={{ transform: 'rotate(180deg)' }} />}
          <span>{copied ? "Copié !" : "Copier"}</span>
        </button>
      </div>
      <SyntaxHighlighter
        children={codeContent}
        style={oneDark}
        language={language}
        PreTag="div"
        showLineNumbers={false}
        useInlineStyles={true}
        codeTagProps={{
          style: {
            backgroundColor: 'transparent',
            fontFamily: 'inherit'
          }
        }}
        customStyle={{
          margin: 0,
          borderRadius: '0 0 12px 12px',
          backgroundColor: '#121214',
          padding: '24px',
          fontSize: '0.85rem',
          lineHeight: '1.6',
          fontFamily: 'var(--font-mono)'
        }}
      />
    </div>
  );
};

export default CodeBlock;
