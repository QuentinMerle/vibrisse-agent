import { useState, useCallback } from 'react';
import { api } from '../services/api';

export const useChatState = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentThread, setCurrentThread] = useState(localStorage.getItem("vibrisse_thread_id"));
  const [threads, setThreads] = useState([]);
  const [isThreadsLoading, setIsThreadsLoading] = useState(false);
  const [contextUsage, setContextUsage] = useState(0);
  const [isWaitingForApproval, setIsWaitingForApproval] = useState(false);
  const [pendingApprovalData, setPendingApprovalData] = useState(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);

  const fetchThreads = useCallback(async () => {
    setIsThreadsLoading(true);
    try {
      const data = await api.getThreads();
      setThreads(data.threads || []);
    } catch (err) {
      console.error("Erreur threads:", err);
    } finally {
      setIsThreadsLoading(false);
    }
  }, []);

  const fetchThreadHistory = useCallback(async (tid) => {
    if (!tid) return;
    setIsHistoryLoading(true);
    try {
      const data = await api.getThreadHistory(tid);
      if (data.messages && data.messages.length > 0) {
        setMessages(data.messages);
      }
      if (data.context_usage !== undefined) {
        setContextUsage(data.context_usage);
      }
    } catch (err) {
      console.error("Erreur history:", err);
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  return {
    messages, setMessages,
    isLoading, setIsLoading,
    currentThread, setCurrentThread,
    threads, setThreads,
    isThreadsLoading,
    isHistoryLoading,
    contextUsage, setContextUsage,
    isWaitingForApproval, setIsWaitingForApproval,
    pendingApprovalData, setPendingApprovalData,
    fetchThreads,
    fetchThreadHistory
  };
};
