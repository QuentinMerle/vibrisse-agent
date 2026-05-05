import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

export const useConfig = () => {
  const [config, setConfig] = useState({
    model: "Chargement...",
    features: { vision: false, search: false, expert_review: false }
  });
  const [availableFiles, setAvailableFiles] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(localStorage.getItem("vibrisse_selected_model") || "");
  const [contextLimit, setContextLimit] = useState(32000);
  const [healthStatus, setHealthStatus] = useState(null);

  const fetchConfig = useCallback(async () => {
    try {
      const data = await api.getConfig();
      setConfig(data);
      if (data.context_limit) setContextLimit(data.context_limit);
    } catch (err) {
      console.error("Erreur config:", err);
    }
  }, []);

  const fetchFiles = useCallback(async () => {
    try {
      const data = await api.getFiles();
      if (data && data.files) {
        setAvailableFiles(data.files.map(f => ({ id: f, display: f })));
      }
    } catch (err) {
      console.error("Erreur files:", err);
    }
  }, []);

  const fetchModels = useCallback(async () => {
    try {
      const data = await api.getModels();
      setAvailableModels(data.models || []);
      if (!selectedModel && data.models?.length > 0) {
        const firstModel = data.models[0];
        setSelectedModel(firstModel);
        localStorage.setItem("vibrisse_selected_model", firstModel);
      }
    } catch (err) {
      console.error("Erreur models:", err);
    }
  }, [selectedModel]);

  const checkHealth = useCallback(async () => {
    try {
      const data = await api.checkHealth();
      setHealthStatus(data);
    } catch (err) {
      setHealthStatus({ status: "error", ollama: "disconnected" });
    }
  }, []);

  useEffect(() => {
    fetchConfig();
    fetchFiles();
    fetchModels();
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [fetchConfig, fetchFiles, fetchModels, checkHealth]);

  const updateSelectedModel = async (model) => {
    setSelectedModel(model);
    localStorage.setItem("vibrisse_selected_model", model);
    try {
      const data = await api.getModelLimit(model);
      if (data.limit) setContextLimit(data.limit);
    } catch (e) {
      console.error("Erreur récup limite:", e);
    }
  };

  const updateTargetPath = async (path) => {
    try {
      const data = await api.updateTargetPath(path);
      if (data.status === "success") {
        await fetchConfig();
        // On attend un court instant que l'ingestion commence côté Backend
        setTimeout(async () => {
          await fetchFiles();
        }, 2000);
        return true;
      }
      return false;
    } catch (e) {
      console.error("Erreur changement path:", e);
      return false;
    }
  };

  return {
    config,
    availableFiles,
    availableModels,
    selectedModel,
    contextLimit,
    healthStatus,
    updateSelectedModel,
    updateTargetPath
  };
};
