import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  fontFamily: 'inherit',
});

const MermaidDiagram = ({ chart }) => {
  const [svg, setSvg] = useState('');
  const [error, setError] = useState(false);
  // Generate a random ID for this specific diagram rendering
  const [id] = useState(`mermaid-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    let isMounted = true;
    
    const renderDiagram = async () => {
      try {
        if (chart) {
          // mermaid.render returns an object { svg } in v10+
          const { svg: svgResult } = await mermaid.render(id, chart);
          if (isMounted) {
            setSvg(svgResult);
            setError(false);
          }
        }
      } catch (err) {
        console.error("Mermaid parsing error", err);
        if (isMounted) {
          setError(true);
        }
      }
    };
    
    renderDiagram();
    
    return () => {
      isMounted = false;
      const el = document.getElementById(id);
      if (el) el.remove();
    };
  }, [chart, id]);

  if (error) {
    return (
      <div className="mermaid-error" style={{ color: '#ef4444', padding: '16px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>
        <p>Invalid Mermaid syntax:</p>
        <pre style={{ fontSize: '12px', marginTop: '8px' }}>{chart}</pre>
      </div>
    );
  }

  return (
    <div 
      className="mermaid-container"
      style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

export default MermaidDiagram;
