import { useState, useRef, useEffect } from 'react';

export const useChatScroll = (messages, isLoading) => {
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);
  const virtuosoRef = useRef(null);

  const scrollToBottom = () => {
    if (autoScrollEnabled && virtuosoRef.current) {
      virtuosoRef.current.scrollToIndex({ index: messages.length - 1, behavior: 'auto' });
    }
  };

  useEffect(() => {
    if (autoScrollEnabled) scrollToBottom();
  }, [messages, isLoading, autoScrollEnabled]);

  const handleUserScrollInteraction = () => {
    if (isLoading && autoScrollEnabled) {
      setAutoScrollEnabled(false);
      console.log("🛑 Scroll auto désactivé par l'utilisateur");
    }
  };

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    // On pourrait rajouter une logique pour réactiver l'auto-scroll si l'utilisateur redescend tout en bas
  };

  const resetAutoScroll = () => setAutoScrollEnabled(true);

  return {
    virtuosoRef,
    autoScrollEnabled,
    handleUserScrollInteraction,
    handleScroll,
    resetAutoScroll
  };
};
