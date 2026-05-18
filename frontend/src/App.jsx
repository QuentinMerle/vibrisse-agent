import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import ChatHeader from './components/ChatHeader';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import CommandApproval from './components/CommandApproval';
import { useChat } from './hooks/useChat';
import { useConfig } from './hooks/useConfig';
import { useSettings } from './hooks/useSettings';
import { useChatScroll } from './hooks/useChatScroll';
import { useNotifications } from './hooks/useNotifications';
import SettingsModal from './components/SettingsModal';
import ConfirmModal from './components/layout/ConfirmModal';
import OnboardingWizard from './components/onboarding/OnboardingWizard';
import SovereignProposal from './components/SovereignProposal';
import { processImageFile } from './utils/fileUtils';
import './App.css';

function App() {
  const { t } = useTranslation();
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
    handleApproval,
    deleteThread,
    offloadProposal,
    setOffloadProposal
  } = useChat(settings);

  const handleAcceptOffload = () => {
    // La recommandation est au format "provider/model"
    const [recProvider, ...modelParts] = offloadProposal.recommendation.split('/');
    const recModel = modelParts.join('/');

    // 1. On change les réglages
    updateSettings({ ...settings, provider: recProvider });
    
    // 2. On relance la requête
    const lastUserMsg = messages.filter(m => m.role === 'user').pop();
    if (lastUserMsg) {
      sendMessage({
        content: lastUserMsg.content,
        image: lastUserMsg.image,
        model: recModel,
        overrideContent: lastUserMsg.content
      });
    }
    setOffloadProposal(null);
  };

  const handleDeclineOffload = () => {
    // On relance la requête mais en ignorant la proposition cette fois
    const lastUserMsg = messages.filter(m => m.role === 'user').pop();
    if (lastUserMsg) {
      sendMessage({
        content: lastUserMsg.content,
        image: lastUserMsg.image,
        model: settings.model,
        overrideContent: lastUserMsg.content
      });
    }
    setOffloadProposal(null);
  };

  const {
    config,
    availableFiles,
    availableDirs,
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

  const { notifications, clearNotifications } = useNotifications();
  const [activeToast, setActiveToast] = useState(null);

  const [input, setInput] = useState("");
  const [image, setImage] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(localStorage.getItem("vibrisse_sidebar_collapsed") === "true");
  const [confirmModal, setConfirmModal] = useState({ isOpen: false, threadId: null });
  const [resetOnboardingConfirm, setResetOnboardingConfirm] = useState({ isOpen: false });
  const [wipeIndexConfirm, setWipeIndexConfirm] = useState({ isOpen: false });
  
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);
  const hasInitialized = useRef(false);

  const openDeleteModal = (tid) => {
    setConfirmModal({ isOpen: true, threadId: tid });
  };

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

  // Handle visual toast for new notifications
  useEffect(() => {
    if (notifications.length > 0) {
      const latest = notifications[notifications.length - 1];
      setActiveToast(latest);
      const timer = setTimeout(() => setActiveToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notifications]);

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;
    if (currentThread) fetchThreadHistory(currentThread);
  }, [currentThread, fetchThreadHistory]);

  const handleSendMessage = (overrideContent = null) => {
    sendMessage({
      content: input,
      image,
      model: settings.provider === 'ollama' ? selectedModel : null,
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
          onDeleteThread={openDeleteModal}
          onNewChat={handleNewSession}
          onWipeIndex={() => setWipeIndexConfirm({ isOpen: true })}
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
            availableDirs={availableDirs}
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

      {offloadProposal && (
        <SovereignProposal 
          proposal={offloadProposal}
          onAccept={handleAcceptOffload}
          onDecline={handleDeclineOffload}
        />
      )}

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
        settings={settings}
        onSave={updateSettings}
        onResetOnboarding={() => setResetOnboardingConfirm({ isOpen: true })}
      />

      <ConfirmModal 
        isOpen={confirmModal.isOpen}
        title={t('sidebar.confirm_delete_title')}
        message={t('sidebar.confirm_delete_msg')}
        confirmText={t('common.delete')}
        onClose={() => setConfirmModal({ ...confirmModal, isOpen: false })}
        onConfirm={() => deleteThread(confirmModal.threadId)}
      />

      <ConfirmModal 
        isOpen={resetOnboardingConfirm.isOpen}
        title="Réinitialiser l'Onboarding"
        message="Voulez-vous vraiment relancer le processus de configuration initiale ? Vos paramètres actuels de modèle seront écrasés."
        confirmText="Relancer"
        onClose={() => setResetOnboardingConfirm({ isOpen: false })}
        onConfirm={async () => {
          try {
            await fetch('/api/system/onboarding/reset', { method: 'POST' });
            localStorage.removeItem('vibrisse_onboarded');
            window.location.reload();
          } catch (e) {
            console.error("Reset failed", e);
          }
        }}
      />

      <ConfirmModal 
        isOpen={wipeIndexConfirm.isOpen}
        title={t('sidebar.reset_btn')}
        message={t('sidebar.wipe_confirm')}
        confirmText={t('common.confirm')}
        onClose={() => setWipeIndexConfirm({ isOpen: false })}
        onConfirm={handleWipeIndex}
      />

      <OnboardingWizard 
        isOpen={config.onboarded === false}
        onClose={() => {}} 
        onComplete={() => {
          // On pourrait forcer un fetchConfig ici au lieu d'un reload
        }}
        updateSettings={updateSettings}
        updateTargetPath={updateTargetPath}
        updateSelectedModel={updateSelectedModel}
      />

      {activeToast && (
        <div className="ghost-toast" onClick={() => setActiveToast(null)}>
          <div className="ghost-toast-icon">👻</div>
          <div className="ghost-toast-content">
            <div className="ghost-toast-title">{activeToast.title}</div>
            <div className="ghost-toast-msg">{activeToast.message}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
