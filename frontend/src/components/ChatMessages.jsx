import React from 'react';
import { Virtuoso } from 'react-virtuoso';
import MessageBubble from './MessageBubble';
import WelcomeScreen from './chat/WelcomeScreen';
import MessageSkeleton from './chat/MessageSkeleton';

const ChatMessages = ({ 
  messages, virtuosoRef, onRetry, onScroll, 
  autoScrollEnabled, isHistoryLoading, onSuggestionClick 
}) => {
  if (isHistoryLoading) {
    return (
      <div className="messages-container" style={{ paddingTop: '60px' }}>
        <MessageSkeleton />
        <MessageSkeleton />
        <MessageSkeleton />
      </div>
    );
  }

  if (messages.length === 0) {
    return <WelcomeScreen onSuggestionClick={onSuggestionClick} />;
  }
  return (
    <Virtuoso
      ref={virtuosoRef}
      className="messages-container"
      data={messages}
      followOutput={autoScrollEnabled ? 'smooth' : false}
      totalListHeightChanged={(height) => {
        if (autoScrollEnabled && virtuosoRef.current && messages.length > 0) {
          virtuosoRef.current.scrollToIndex({ 
            index: messages.length - 1, 
            align: 'end', 
            behavior: 'auto' 
          });
        }
      }}
      increaseViewportBy={800} // Pré-rendu pour éviter les saccades
      atBottomStateChange={(atBottom) => {
        // Sync avec l'auto-scroll si besoin
      }}
      components={{
        Header: () => <div style={{ height: '40px', flexShrink: 0 }} />,
        Footer: () => <div style={{ height: '180px', flexShrink: 0 }} />
      }}
      itemContent={(idx, msg) => {
        const isLatest = idx === messages.length - 1;
        // Trouver la question utilisateur correspondante pour l'évaluation Ragas
        let question = "";
        if (msg.role === "agent") {
          for (let i = idx - 1; i >= 0; i--) {
            if (messages[i].role === "user") {
              question = messages[i].content;
              break;
            }
          }
        }

        return (
          <MessageBubble 
            key={msg.id || idx}
            message={msg} 
            question={question}
            isLatest={isLatest} 
            onRetry={onRetry} 
          />
        );
      }}
    />
  );
};

export default ChatMessages;
