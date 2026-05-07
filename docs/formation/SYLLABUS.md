# 🎓 Master Plan : Devenir AI Engineer (Vibrisse AI)

Ce programme est conçu pour emmener un développeur de la compréhension brute des LLMs à la conception de systèmes agentiques complexes, sécurisés et industrialisables.

## 🚀 Chapitre 0 : L'Étincelle (L'IA à nu)
*Objectif : Comprendre la mécanique sans abstraction.*
*   **Le "Hello World"** : Script Python minimaliste communiquant avec Ollama via `requests`.
*   **Paramètres d'inférence** : Température, Top-P, et fenêtres de contexte.
*   **Pair-Programming 101** : Apprendre à utiliser l'IA (Cursor/Antigravity) pour expliquer et optimiser ce premier script.
*   **Mots-Clés** : *Inférence, Tokens, Température, Top-P, Context Window, Zero-shot.*

## 🏗️ Chapitre 1 : Infrastructure & Sécurité (Le Socle)
*Objectif : Bâtir une base technique robuste et protégée.*
*   **LiteLLM** : Créer une couche d'abstraction agnostique (Local vs Cloud).
*   **Streaming SSE (FastAPI)** : Architecture asynchrone pour une interface réactive.
*   **Security & Scrubbing** : Implémenter le masquage automatique des secrets (PII/API Keys) pour garantir la confidentialité des logs.
*   **Mots-Clés** : *Abstraction Layer, SSE (Server-Sent Events), PII Scrubbing, GGUF, Latence.*

## 🧠 Chapitre 2 : La Mémoire Dynamique (RAG & Watchers)
*Objectif : Connecter l'IA à des données privées et vivantes.*
*   **Triple-Layer Search** : Combiner recherche vectorielle (ChromaDB), lexicale (BM25) et **Surgical Grep** (ripgrep) pour une précision chirurgicale.
*   **Watcher Service** : Monitoring du système de fichiers pour un index RAG synchrone.
*   **Semantic Cache** : Optimisation de la latence et des coûts.
*   **Mots-Clés** : *Embeddings, Surgical Grep, Hybrid Search, BM25, Sparse vs Dense, Watchers.*

## 🔍 Chapitre 3 : Précision Chirurgicale (Data Engineering & Reranking)
*Objectif : Maximiser la pertinence du contexte injecté.*
*   **Context Pruning** : Nettoyage intelligent du code source (suppression bruits/headers) pour maximiser le focus du modèle.
*   **Project Manifest** : Automatiser l'onboarding et la compréhension d'architecture.
*   **Mots-Clés** : *Tree-Sitter, Context Pruning, Token Optimization, Reranking, Cross-Encoder.*

## 🤖 Chapitre 4 : Le Raisonnement Modulaire (Agents & Skills)
*Objectif : Concevoir une intelligence segmentée et spécialisée.*
*   **Supervisor/Worker Architecture** : Segmenter l'intelligence par rôles (Coder, Architect, Writer).
*   **Robust Parsing** : Implémenter un moteur de parsing multi-couches (JSON, XML, Keywords) pour une stabilité maximale.
*   **Mots-Clés** : *DAG, Supervisor/Worker, Robust Parsing, XML Fallback, State Management.*

## 🔌 Chapitre 5 : L'Écosystème Étendu (MCP & Multi-modal)
*Objectif : Ouvrir l'IA sur les outils de production.*
*   **Model Context Protocol (MCP)** : Connecter nativement son agent à GitHub, Linear, et Slack.
*   **Human-in-the-Loop (HITL)** : Créer des barrières de sécurité pour les actions critiques.
*   **Vision Analyst** : Intégrer l'analyse multi-modale pour le débugging visuel.
*   **Mots-Clés** : *MCP (Model Context Protocol), Tool Calling, HITL (Human-in-the-Loop), Multi-modality.*

## 🎨 Chapitre 6 : L'Expérience Studio & FinOps (Le Produit Fini)
*Objectif : Packager et piloter la rentabilité de la solution.*
*   **Studio UI (React)** : Design Obsidian Glass, Skeletons et **Context Gauges** (observabilité contextuelle).
*   **Hacker TUI** : Créer une interface terminal haute performance avec Python Rich.
*   **FinOps & Token Tracking** : Suivi précis de la consommation et estimation des coûts.
*   **Évaluation (RAGAS)** : Mesurer la performance réelle pour valider le passage en production.
*   **Mots-Clés** : *FinOps, Token Tracking, RAGAS (Faithfulness/Relevancy), Obsidian Glass UX, Skeleton UI.*

---
*Vibrisse AI: Small models, Great tools.*
