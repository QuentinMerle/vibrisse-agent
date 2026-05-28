import React from 'react';

const CodeDiff = ({ diffString }) => {
  if (!diffString) return null;

  const lines = diffString.split('\n');

  return (
    <div className="diff-container">
      {lines.map((line, index) => {
        let type = 'normal';
        if (line.startsWith('+') && !line.startsWith('+++')) type = 'added';
        else if (line.startsWith('-') && !line.startsWith('---')) type = 'removed';
        else if (line.startsWith('@@')) type = 'chunk';
        else if (line.startsWith('---') || line.startsWith('+++')) type = 'header';
        
        return (
          <div key={index} className={`diff-line diff-${type}`}>
            <span className="diff-line-number">{index + 1}</span>
            <span className="diff-line-content">{line}</span>
          </div>
        );
      })}
    </div>
  );
};

export default CodeDiff;
