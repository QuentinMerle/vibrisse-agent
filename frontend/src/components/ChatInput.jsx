import React, { useState } from 'react';
import { Send, Image as ImageIcon, Mic, MicOff, Square, X } from 'lucide-react';
import { MentionsInput, Mention } from 'react-mentions';
import './ChatInput.css';

const ChatInput = ({ 
  input, setInput, image, setImage, isLoading, sendMessage, onStop,
  availableFiles, handleFileClick, fileInputRef, inputRef, handleFileUpload 
}) => {
  const [isListening, setIsListening] = useState(false);

  const toggleListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("La reconnaissance vocale n'est pas supportée sur ce navigateur.");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'fr-FR';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (transcript) {
        setInput(prev => prev ? `${prev} ${transcript}` : transcript);
      }
    };

    recognition.start();
  };

  // Style spécifique pour react-mentions
  const mentionsStyle = {
    control: {
      fontSize: '15px',
      fontWeight: 'normal',
      lineHeight: '1.5',
    },
    '&multiLine': {
      control: {
        fontFamily: 'inherit',
      },
      highlighter: {
        padding: '12px 0',
        border: '1px solid transparent',
        lineHeight: '1.5',
      },
      input: {
        padding: '12px 0',
        border: '1px solid transparent', // Match highlighter border
        outline: 'none',
        lineHeight: '1.5',
        color: '#f1f5f9',
      },
    },
    suggestions: {
      list: {
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255,255,255,0.1)',
        fontSize: 14,
        borderRadius: '12px',
        overflow: 'hidden',
        zIndex: 1000,
        top: 'auto', // Override top
        bottom: '100%', // Positionné au-dessus de l'input
        marginBottom: '10px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
      },
      item: {
        padding: '8px 12px',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        '&focused': {
          backgroundColor: '#6366f1',
          color: 'white',
        },
      },
    },
  };

  return (
    <div className="input-area">
      {image && (
        <div className="image-preview-container">
          <div className="image-preview-badge">
            <ImageIcon size={12} />
            <span>Image jointe</span>
            <button 
              className="remove-image-btn"
              type="button"
              onMouseDown={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setImage(null);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }} 
              aria-label="Supprimer l'image jointe"
              style={{ position: 'relative', zIndex: 100 }}
            >
              <X size={12} strokeWidth={3} />
            </button>
          </div>
        </div>
      )}

      <div className="input-wrapper">
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileUpload} 
          accept="image/*" 
          style={{ display: 'none' }} 
        />
        
        <button className="icon-btn" onClick={handleFileClick} title="Ajouter une image" aria-label="Joindre une image">
          <ImageIcon size={20} color={image ? "#a78bfa" : "#94a3b8"} aria-hidden="true" />
        </button>

        <div className="mentions-input-container">
          <MentionsInput
            inputRef={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Posez une question ou tapez @ pour citer un fichier..."
            style={mentionsStyle}
            a11ySuggestionsListLabel="Fichiers disponibles"
            aria-label="Votre message pour l'agent"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          >
            <Mention
              trigger="@"
              data={availableFiles}
              displayTransform={(id, display) => `@${display}`}
              className="mention-highlight"
            />
          </MentionsInput>
        </div>

        <button 
          className={`icon-btn mic-btn ${isListening ? 'listening' : ''}`}
          onClick={toggleListening}
          title="Parler au lieu de taper"
          aria-label={isListening ? "Arrêter la reconnaissance vocale" : "Démarrer la reconnaissance vocale"}
        >
          {isListening ? <MicOff size={20} color="#ef4444" aria-hidden="true" /> : <Mic size={20} color="#94a3b8" aria-hidden="true" />}
        </button>

        {isLoading ? (
          <button 
            className="send-btn stop-btn" 
            onClick={onStop} 
            aria-label="Arrêter la génération"
          >
            <Square size={20} fill="currentColor" aria-hidden="true" />
          </button>
        ) : (
          <button 
            className="send-btn" 
            onClick={() => sendMessage()} 
            disabled={!input.trim() && !image}
            aria-label="Envoyer le message"
          >
            <Send size={20} aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatInput;
