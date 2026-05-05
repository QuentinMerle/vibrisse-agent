import { useCallback } from 'react';
import { api } from '../services/api';

export const useChatActions = (state) => {
  const { setMessages, setContextUsage, setCurrentThread, fetchThreads } = state;

  const handleNewSession = useCallback(() => {
    setMessages([{ role: "agent", content: "Nouvelle session démarrée. Comment puis-je t'aider ?", steps: [] }]);
    setContextUsage(0);
    setCurrentThread(null);
    localStorage.removeItem("vibrisse_thread_id");
  }, [setMessages, setContextUsage, setCurrentThread]);

  const handleWipeIndex = useCallback(async () => {
    if (window.confirm("Voulez-vous vraiment vider l'indexation (RAG) et tout l'historique ? Cette action est irréversible.")) {
      try {
        await api.clearCache();
        handleNewSession();
        fetchThreads();
      } catch (err) {
        console.error("Erreur wipe:", err);
      }
    }
  }, [handleNewSession, fetchThreads]);

  return { handleNewSession, handleWipeIndex };
};
