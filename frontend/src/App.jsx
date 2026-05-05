import { useState, useRef, useEffect } from 'react';
import ChatHeader from './components/ChatHeader';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import CommandApproval from './components/CommandApproval';
import { useChat } from './hooks/useChat';
import { useConfig } from './hooks/useConfig';
import { useSettings } from './hooks/useSettings';
import { useChatScroll } from './hooks/useChatScroll';
import SettingsModal from './components/SettingsModal';
import { processImageFile } from './utils/fileUtils';
import './App.css';

function App() {
  const {
    settings,
    updateSettings,
    isSettingsOpen,
    setIsSettingsOpen
  } = useSettings();

  const {
    messages,
    isLoading,
    currentThread,
    setCurrentThread,
    threads,
    fetchThreadHistory,
    isThreadsLoading,
    isHistoryLoading,
    contextUsage,
    isWaitingForApproval,
    pendingApprovalData,
    handleNewSession,
    handleWipeIndex,
    sendMessage,
    stopGeneration,
    handleApproval
  } = useChat(settings);

  const {
    config,
    availableFiles,
    availableModels,
    selectedModel,
    contextLimit,
    healthStatus,
    updateSelectedModel,
    updateTargetPath
  } = useConfig();

  const {
    virtuosoRef,
    autoScrollEnabled,
    handleUserScrollInteraction,
    handleScroll,
    resetAutoScroll
  } = useChatScroll(messages, isLoading);

  const [input, setInput] = useState("");
  const [image, setImage] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(localStorage.getItem("vibrisse_sidebar_collapsed") === "true");
  
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);
  const hasInitialized = useRef(false);

  const toggleSidebar = () => {
    const newState = !isSidebarCollapsed;
    setIsSidebarCollapsed(newState);
    localStorage.setItem("vibrisse_sidebar_collapsed", newState);
  };

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // CMD/CTRL + B: Toggle Sidebar
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault();
        toggleSidebar();
      }
      // CMD/CTRL + N: New Chat
      if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
        e.preventDefault();
        handleNewSession();
      }
      // CMD/CTRL + K: Focus Input
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSidebarCollapsed, handleNewSession]);

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;
    if (currentThread) fetchThreadHistory(currentThread);
  }, [currentThread, fetchThreadHistory]);

  const handleSendMessage = (overrideContent = null) => {
    sendMessage({
      content: input,
      image,
      model: selectedModel,
      overrideContent
    });
    if (!overrideContent) setInput("");
    setImage(null);
    resetAutoScroll();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    try {
      const base64 = await processImageFile(file);
      setImage(base64);
    } catch (err) {
      console.error("Erreur upload image:", err);
    }
  };

  return (
    <div className="app-container" style={{ flexDirection: 'column' }}>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar 
          threads={threads} 
          currentThread={currentThread} 
          onSelectThread={(tid) => {
            setCurrentThread(tid);
            localStorage.setItem("vibrisse_thread_id", tid);
            fetchThreadHistory(tid);
          }}
          onNewChat={handleNewSession}
          onWipeIndex={handleWipeIndex}
          isLoadingThreads={isThreadsLoading}
          healthStatus={healthStatus}
          contextUsage={contextUsage}
          contextLimit={contextLimit}
          onUpdateTargetPath={updateTargetPath}
          onOpenSettings={() => setIsSettingsOpen(true)}
          llmSettings={settings}
          isCollapsed={isSidebarCollapsed}
          onToggle={toggleSidebar}
        />
      
        <main 
          className="main-chat"
          onWheel={handleUserScrollInteraction}
          onTouchMove={handleUserScrollInteraction}
        >
          <ChatHeader 
            config={config} 
            availableModels={availableModels}
            selectedModel={selectedModel}
            contextUsage={contextUsage}
            contextLimit={contextLimit}
            onSelectModel={updateSelectedModel}
            onResetSession={handleNewSession}
            llmSettings={settings}
          />
          <ChatMessages 
            key={currentThread || 'new'}
            messages={messages} 
            virtuosoRef={virtuosoRef} 
            onRetry={(content) => handleSendMessage(content)} 
            onScroll={handleScroll}
            autoScrollEnabled={autoScrollEnabled}
            isHistoryLoading={isHistoryLoading}
            onSuggestionClick={(text) => {
              setInput(text);
              setTimeout(() => inputRef.current?.focus(), 50);
            }}
          />
          <ChatInput 
            input={input} setInput={setInput}
            image={image} setImage={setImage}
            isLoading={isLoading} 
            sendMessage={() => handleSendMessage()}
            onStop={stopGeneration}
            availableFiles={availableFiles}
            handleFileClick={() => fileInputRef.current?.click()}
            fileInputRef={fileInputRef}
            inputRef={inputRef}
            handleFileUpload={handleFileUpload}
          />
        </main>
      </div>

      {isWaitingForApproval && (
        <CommandApproval 
          command={pendingApprovalData?.command} 
          onApprove={() => handleApproval(true)} 
          onCancel={() => handleApproval(false)} 
        />
      )}

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
        settings={settings}
        onSave={updateSettings}
      />
    </div>
  );
}

export default App;
