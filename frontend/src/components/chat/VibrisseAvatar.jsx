import React from 'react';
import { Bot } from 'lucide-react';
import './VibrisseAvatar.css';

export default function VibrisseAvatar({ size = 20, containerSize, isThinking = false }) {
  const containerStyle = containerSize ? { width: `${containerSize}px`, height: `${containerSize}px` } : {};
  
  return (
    <div 
      className={`vibrisse-avatar-container ${isThinking ? 'thinking' : ''}`}
      style={containerStyle}
    >
      <div className="bot-icon-wrapper">
        {/* Bandeau de masquage + Oreilles de chat blanches */}
        <div className="cat-ears">
          <div className="ear left-ear"></div>
          <div className="ear right-ear"></div>
        </div>

        <Bot size={size} />

        {/* Moustaches (Vibrisses) blanches */}
        <div className="whiskers">
          <div className="whisker-group left">
            <span className="w-line"></span>
            <span className="w-line"></span>
          </div>
          <div className="whisker-group right">
            <span className="w-line"></span>
            <span className="w-line"></span>
          </div>
        </div>
      </div>
    </div>
  );
}
