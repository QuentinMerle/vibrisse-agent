import { useEffect } from 'react';
import { useChatState } from './useChatState';
import { useChatStream } from './useChatStream';
import { useChatActions } from './useChatActions';

export const useChat = (settings) => {
  const state = useChatState();
  const stream = useChatStream(state, settings);
  const actions = useChatActions(state);

  useEffect(() => {
    state.fetchThreads();
  }, [state.fetchThreads]);

  return {
    ...state,
    ...stream,
    ...actions,
    // Wrapper for handleApproval to pass the state's pendingApprovalData
    handleApproval: (approved) => stream.handleApproval(approved, state.pendingApprovalData)
  };
};
