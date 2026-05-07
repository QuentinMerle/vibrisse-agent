import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';

export const useChatActions = (state) => {
  const { t } = useTranslation();
  const { setMessages, setContextUsage, setCurrentThread, fetchThreads } = state;

  const handleNewSession = useCallback(() => {
    setMessages([{ role: "agent", content: t('chat.new_session_msg'), steps: [] }]);
    setContextUsage(0);
    setCurrentThread(null);
    localStorage.removeItem("vibrisse_thread_id");
  }, [setMessages, setContextUsage, setCurrentThread, t]);

  const handleWipeIndex = useCallback(async () => {
    try {
      await api.clearCache();
      handleNewSession();
      fetchThreads();
    } catch (err) {
      console.error("Erreur wipe:", err);
    }
  }, [handleNewSession, fetchThreads]);

  return { handleNewSession, handleWipeIndex };
};
