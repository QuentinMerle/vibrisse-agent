import { useRef } from 'react';
import { api } from '../services/api';

export const useChatStream = (state, settings) => {
  const {
    setMessages, setIsLoading, setCurrentThread,
    fetchThreads, setContextUsage, setIsWaitingForApproval,
    setPendingApprovalData, currentThread
  } = state;

  const abortControllerRef = useRef(null);

  const processStream = async (response, isApproval = false) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let lineBuffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      lineBuffer += decoder.decode(value, { stream: true });
      const lines = lineBuffer.split("\n");
      lineBuffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const dataStr = line.replace("data: ", "").trim();
          if (dataStr === "[DONE]") {
            setIsLoading(false);
            setMessages(prev => {
              const newMsgs = [...prev];
              if (newMsgs.length > 0) newMsgs[newMsgs.length - 1].isLoading = false;
              return newMsgs;
            });
            continue;
          }
          try {
            const data = JSON.parse(dataStr);
            
            if (data.offload_proposal) {
              console.log("⚖️ Offload Proposal Detected:", data.offload_proposal);
              state.setOffloadProposal(data.offload_proposal);
              setIsLoading(false);
            }

            setMessages(prev => {
              const newMsgs = [...prev];
              let targetIdx = -1;
              for (let i = newMsgs.length - 1; i >= 0; i--) {
                if (newMsgs[i].role === 'agent') {
                  targetIdx = i;
                  break;
                }
              }

              if (targetIdx === -1) return prev;

              const targetMsg = { ...newMsgs[targetIdx] };

              if (data.status === "thinking") {
                targetMsg.isLoading = true;
              }

              if (data.status === "completed") {
                const isFinalStep = data.steps && data.steps.some(s =>
                  s.includes("Rédaction") || s.includes("Vérification")
                );
                if (isFinalStep) {
                  targetMsg.isLoading = false;
                }
              }

              if (data.chunk) {
                if (targetMsg.content === "⏳ Vibrisse prépare sa réponse...") {
                  targetMsg.content = "";
                }
                
                // Si on change de nœud de génération (ex: de generate_answer à expert_review_node),
                // on vide le contenu précédent pour éviter la double réponse à l'écran !
                if (data.node && targetMsg.lastActiveNode && targetMsg.lastActiveNode !== data.node) {
                  targetMsg.content = "";
                }
                if (data.node) {
                  targetMsg.lastActiveNode = data.node;
                }

                targetMsg.content = (targetMsg.content || "") + data.chunk;
                targetMsg.isLoading = false;
              }

              if (data.final_content) {
                // Pour l'approbation, on ne remplace que si c'est vide ou le placeholder
                if (isApproval) {
                   if (!targetMsg.content || targetMsg.content === "⏳ Vibrisse prépare sa réponse...") {
                    targetMsg.content = data.final_content;
                    targetMsg.isLoading = false;
                  }
                } else {
                  targetMsg.content = data.final_content;
                  if (data.thoughts_history) {
                    const current = targetMsg.thoughts_history || [];
                    const merged = Array.from(new Set([...current, ...data.thoughts_history]));
                    targetMsg.thoughts_history = merged;
                  }
                  targetMsg.isLoading = false;
                  if (data.detail) targetMsg.detail = data.detail;
                }
              }

              if (data.steps) {
                const existingSteps = targetMsg.steps || [];
                const uniqueStepsSet = new Set([...existingSteps, ...data.steps]);
                if (targetMsg.content.length > 0) {
                  data.steps.forEach(s => {
                    if (s.includes("Rédaction")) uniqueStepsSet.delete(s);
                  });
                }
                targetMsg.steps = Array.from(uniqueStepsSet);
              }

              if (!isApproval && data.tool_calls) {
                const sensitiveTool = data.tool_calls.find(tc =>
                  tc.name === "run_terminal_command" ||
                  tc.name === "write_file" ||
                  (tc.function && (tc.function.name === "run_terminal_command" || tc.function.name === "write_file"))
                );
                if (sensitiveTool) {
                  let cmd = "";
                  const args = sensitiveTool.args || (sensitiveTool.function?.arguments ? JSON.parse(sensitiveTool.function.arguments) : {});
                  
                  if (sensitiveTool.name === "run_terminal_command" || sensitiveTool.function?.name === "run_terminal_command") {
                    cmd = args.command || "";
                  } else if (sensitiveTool.name === "write_file" || sensitiveTool.function?.name === "write_file") {
                    const preview = args.content ? (args.content.length > 100 ? args.content.substring(0, 100) + "..." : args.content) : "";
                    cmd = `FILE: ${args.filename}\nCONTENT: ${preview}`;
                  }

                  setPendingApprovalData({
                    threadId: data.thread_id,
                    command: cmd
                  });
                  setIsWaitingForApproval(true);
                }
              }

              if (data.context_usage !== undefined) {
                setContextUsage(data.context_usage);
              }

              if (data.detail) {
                targetMsg.detail = data.detail;
              }

              if (data.context) {
                targetMsg.context = data.context;
              }
              
              if (data.thoughts) {
                const current = targetMsg.thoughts_history || [];
                // Gestion du RESET comme au backend
                if (data.thoughts[0] === "__RESET__") {
                  targetMsg.thoughts_history = data.thoughts.slice(1);
                } else {
                  const newThoughts = data.thoughts.filter(t => !current.includes(t));
                  if (newThoughts.length > 0) {
                    targetMsg.thoughts_history = [...current, ...newThoughts];
                  }
                }
              }

              if (data.graph_nodes) {
                const currentNodes = targetMsg.graph_nodes || [];
                const nodeMap = new Map(currentNodes.map(n => [n.id, n]));
                data.graph_nodes.forEach(n => nodeMap.set(n.id, n));
                targetMsg.graph_nodes = Array.from(nodeMap.values());
              }

              if (data.graph_edges) {
                const currentEdges = targetMsg.graph_edges || [];
                const edgeMap = new Map(currentEdges.map(e => [e.id || `${e.source}-${e.target}`, e]));
                data.graph_edges.forEach(e => {
                  const id = e.id || `${e.source}-${e.target}`;
                  edgeMap.set(id, { ...e, id });
                });
                targetMsg.graph_edges = Array.from(edgeMap.values());
              }

              if (data.active_worker) {
                targetMsg.active_worker = data.active_worker;
              }

              newMsgs[targetIdx] = targetMsg;
              return newMsgs;
            });
          } catch (e) { }
        }
      }
    }
  };

  const sendMessage = async ({ content, image, model, overrideContent = null }) => {
    const textToSend = overrideContent || content.trim();
    if (!textToSend && !image) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);

    if (!overrideContent) {
      setMessages(prev => [
        ...prev,
        { role: "user", content: textToSend, image: image, timestamp: Date.now() },
        { role: "agent", content: "", steps: [], isLoading: true, timestamp: Date.now() }
      ]);
    } else {
      setMessages(prev => {
        const newMsgs = [...prev];
        const lastIdx = newMsgs.length - 1;
        if (lastIdx >= 0 && newMsgs[lastIdx].role === 'agent') {
          newMsgs[lastIdx] = { ...newMsgs[lastIdx], content: "", steps: [], isLoading: true, error: null, timestamp: Date.now() };
        } else {
          newMsgs.push({ role: "agent", content: "", steps: [], isLoading: true, timestamp: Date.now() });
        }
        return newMsgs;
      });
    }

    try {
      const threadId = currentThread || Math.random().toString(36).substring(7);
      if (!currentThread) {
        setCurrentThread(threadId);
        localStorage.setItem("vibrisse_thread_id", threadId);
        setTimeout(fetchThreads, 1500);
      }

      const response = await api.chat({
        message: textToSend,
        thread_id: threadId,
        image: image,
        model: model
      }, abortControllerRef.current.signal, settings);

      await processStream(response);
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log("Ancienne génération nettoyée.");
      } else {
        console.error("Erreur chat:", err);
        setIsLoading(false);
        setMessages(prev => {
          const newMsgs = [...prev];
          if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].role === 'agent') {
            newMsgs[newMsgs.length - 1].isLoading = false;
          }
          return newMsgs;
        });
      }
    }
  };

  const handleApproval = async (approved, pendingApprovalData) => {
    if (!pendingApprovalData) return;

    const { threadId } = pendingApprovalData;
    setIsWaitingForApproval(false);
    setPendingApprovalData(null);
    setIsLoading(true);

    try {
      const response = await api.approveCommand({ thread_id: threadId, approved });
      await processStream(response, true);
    } catch (error) {
      console.error("Erreur Approval API:", error);
      setIsLoading(false);
    }
  };

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  return { sendMessage, handleApproval, stopGeneration };
};
