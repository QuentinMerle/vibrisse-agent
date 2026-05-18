import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, Image as ImageIcon, Mic, MicOff, Square, X } from 'lucide-react';
import { MentionsInput, Mention } from 'react-mentions';
import './ChatInput.css';

// Style spécifique pour react-mentions
const mentionsStyle = {
  control: {
    fontSize: '15px',
    fontWeight: 'normal',
    lineHeight: '1.5',
    fontFamily: 'inherit',
  },
  '&multiLine': {
    control: {
      fontFamily: 'inherit',
    },
    highlighter: {
      padding: '12px 14px',
      border: '1px solid transparent',
      lineHeight: '1.5',
      color: 'transparent', // CRUCIAL : évite le dédoublement du texte
    },
    input: {
      padding: '12px 14px',
      border: '1px solid transparent',
      outline: 'none',
      lineHeight: '1.5',
      color: '#f1f5f9',
    },
  },
  suggestions: {
    backgroundColor: 'transparent',
    list: {
      backgroundColor: '#0f172a',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      fontSize: 14,
      borderRadius: '12px',
      overflowY: 'auto',
      maxHeight: '300px',
      zIndex: 1000,
      top: 'auto',
      bottom: '100%',
      marginBottom: '10px',
      boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
    },
    item: {
      padding: '10px 14px',
      borderBottom: '1px solid rgba(255, 255, 255, 0.03)',
      color: '#94a3b8',
      '&focused': {
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        color: 'white',
      },
    },
  },
};

const ChatInput = ({ 
  input, setInput, image, setImage, isLoading, sendMessage, onStop,
  availableFiles, availableDirs, handleFileClick, fileInputRef, inputRef, handleFileUpload
}) => {
  const { t } = useTranslation();
  const [isListening, setIsListening] = useState(false);

  const toggleListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert(t('input.mic_not_supported'));
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

  return (
    <div className="input-area">
      <div className="input-top-bar">
        {image && (
          <div className="image-preview-container">
            <div className="image-preview-badge">
              <ImageIcon size={12} />
              <span>{t('input.image_attached')}</span>
              <button 
                className="remove-image-btn"
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setImage(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }} 
                aria-label={t('input.remove_image')}
                style={{ position: 'relative', zIndex: 100 }}
              >
                <X size={12} strokeWidth={3} />
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="input-wrapper">
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileUpload} 
          accept="image/*" 
          style={{ display: 'none' }} 
        />
        
        <button className="icon-btn" onClick={handleFileClick} title={t('input.attach_image')} aria-label={t('input.attach_image')}>
          <ImageIcon size={20} color={image ? "#a78bfa" : "#94a3b8"} aria-hidden="true" />
        </button>

        <div className="mentions-input-container">
          <MentionsInput
            inputRef={inputRef}
            value={input}
            onChange={(e) => {
              const val = e.target.value;
              // Si on détecte un collage (gros changement) avec des sauts de ligne à la fin, on trim
              if (val.length > input.length + 5 && val.endsWith('\n')) {
                setInput(val.trim());
              } else {
                setInput(val);
              }
            }}
            placeholder={t('input.placeholder')}
            style={mentionsStyle}
            a11ySuggestionsListLabel={t('input.files_label')}
            aria-label={t('input.input_label')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          >
            <Mention
              trigger="@"
              data={[...availableFiles, ...availableDirs]}
              displayTransform={(id, display) => `@${display}`}
              className="mention-highlight file"
            />
            <Mention
              trigger="/"
              data={availableDirs}
              displayTransform={(id, display) => `/${display}`}
              className="mention-highlight dir"
            />
          </MentionsInput>
        </div>

        <button 
          className={`icon-btn mic-btn ${isListening ? 'listening' : ''}`}
          onClick={toggleListening}
          title={t('input.mic_tooltip')}
          aria-label={isListening ? t('input.mic_stop') : t('input.mic_start')}
        >
          {isListening ? <MicOff size={20} color="#ef4444" aria-hidden="true" /> : <Mic size={20} color="#94a3b8" aria-hidden="true" />}
        </button>

        {isLoading ? (
          <button 
            className="send-btn stop-btn" 
            onClick={onStop} 
            aria-label={t('input.stop_generation')}
          >
            <Square size={20} fill="currentColor" aria-hidden="true" />
          </button>
        ) : (
          <button 
            className="send-btn" 
            onClick={() => sendMessage()} 
            disabled={!input.trim() && !image}
            aria-label={t('input.send_message')}
          >
            <Send size={20} aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatInput;
