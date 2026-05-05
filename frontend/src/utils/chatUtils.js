export const extractThinking = (text) => {
  const tags = [
    { start: "<think>", end: "</think>" },
    { start: "<thought>", end: "</thought>" },
    { start: "<thinking>", end: "</thinking>" }
  ];

  let thinking = "";
  let answer = text;

  // 1. Extraction des tags de réflexion standard
  for (const tag of tags) {
    const lowerText = answer.toLowerCase();
    const sIdx = lowerText.indexOf(tag.start);
    if (sIdx !== -1) {
      const eIdx = lowerText.indexOf(tag.end);
      if (eIdx !== -1) {
        thinking = answer.substring(sIdx + tag.start.length, eIdx);
        answer = (answer.substring(0, sIdx) + answer.substring(eIdx + tag.end.length)).trim();
      } else {
        thinking = answer.substring(sIdx + tag.start.length);
        answer = answer.substring(0, sIdx).trim();
      }
    }
  }

  // 2. Nettoyage agressif du JSON de routage qui peut fuiter
  // Supprime tout ce qui ressemble à {"datasource": ...} ou {"thought": ...} même s'il y a des espaces
  answer = answer.replace(/^\s*\{[\s\S]*?"datasource"[\s\S]*?\}\s*/, '');
  answer = answer.replace(/^\s*\{[\s\S]*?"thought"[\s\S]*?\}\s*/, '');
  
  // Supprime les IDs de chunks ou restes de JSON (ex: }1, 3, 4)
  answer = answer.replace(/^\s*\}\s*\d+(,\s*\d+)*\s*/, '');

  // 3. Nettoyage des tags orphelins
  answer = answer
    .replace(/<think>[\s\S]*?<\/think>/gi, '')
    .replace(/<thought>[\s\S]*?<\/thought>/gi, '')
    .replace(/<thinking>[\s\S]*?<\/thinking>/gi, '')
    .replace(/<\/?think>/gi, '')
    .replace(/<\/?thought>/gi, '')
    .replace(/<\/?thinking>/gi, '')
    .trim();

  return { 
    thinking: thinking.trim(), 
    answer: answer || (thinking ? "" : text), // Fallback si tout a été nettoyé
    isComplete: text.toLowerCase().includes("</") 
  };
};
