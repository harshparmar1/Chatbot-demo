import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Trash2, Shield, User, Bot, Sparkles, Clock, History } from "lucide-react";

// Helper to parse simple markdown (**bold**, - lists, ### headers, \n newlines)
function parseMarkdown(text) {
  if (!text) return "";
  
  const lines = text.split("\n");
  return lines.map((line, idx) => {
    let content = line;
    
    // Check for Headers
    if (content.startsWith("### ")) {
      return (
        <h4 key={idx} className="text-sm font-bold text-slate-800 dark:text-white mt-3 mb-1 first:mt-0 uppercase tracking-wider">
          {parseInline(content.slice(4))}
        </h4>
      );
    }
    
    // Check for Bullet Points
    if (content.startsWith("- ")) {
      return (
        <li key={idx} className="ml-4 list-disc text-xs md:text-sm my-0.5 leading-relaxed">
          {parseInline(content.slice(2))}
        </li>
      );
    }
    
    // Standard Paragraph
    if (content.trim() === "") {
      return <div key={idx} className="h-2" />;
    }
    
    return (
      <p key={idx} className="text-xs md:text-sm my-1 leading-relaxed">
        {parseInline(content)}
      </p>
    );
  });
}

// Helper for inline markdown like **bold**
function parseInline(text) {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="font-bold text-slate-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I am the **Reallist AI Audit Assistant**. I run local calculations on the hospital audit CSV logs. Ask me anything about risk, compliance, audits, staff performance, or escalations!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [pastQueries, setPastQueries] = useState([]);
  
  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    "Which location has highest risk?",
    "Show pending audits.",
    "Which checklist fails most?",
    "Who created most failed checklists?",
    "Show hospital summary.",
    "Which user performs best?",
    "Why is this location risky?",
    "Show today's audits.",
    "Show failed fire inspections."
  ];

  // Load conversation history from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem("reallist_chat_queries");
      if (stored) {
        setPastQueries(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
  }, []);

  // Save new query to history
  const saveQueryToHistory = (query) => {
    const cleanQuery = query.trim();
    if (!cleanQuery) return;
    
    setPastQueries(prev => {
      // Avoid duplicate entries in history list
      const filtered = prev.filter(q => q.toLowerCase() !== cleanQuery.toLowerCase());
      const updated = [cleanQuery, ...filtered].slice(0, 15); // limit to 15 entries
      localStorage.setItem("reallist_chat_queries", JSON.stringify(updated));
      return updated;
    });
  };

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isTyping, isOpen]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    // Add user message
    const userMsg = {
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput("");
    setIsTyping(true);
    setShowHistory(false); // Close history drawer if open

    // Save query in conversation history
    saveQueryToHistory(query);

    try {
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query })
      });
      
      const data = await response.json();
      
      setIsTyping(false);
      setMessages(prev => [
        ...prev,
        {
          sender: "bot",
          text: data.response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          intent: data.intent
        }
      ]);
    } catch (error) {
      setIsTyping(false);
      setMessages(prev => [
        ...prev,
        {
          sender: "bot",
          text: "I am having trouble reaching the analytics backend. Please make sure the Flask application is running on port 5000.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        sender: "bot",
        text: "Conversation cleared. Ready to start a new audit analysis session!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const clearHistory = (e) => {
    e.stopPropagation();
    localStorage.removeItem("reallist_chat_queries");
    setPastQueries([]);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Floating Action Button (FAB) */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="h-14 w-14 rounded-full bg-hospital-600 hover:bg-hospital-700 text-white flex items-center justify-center shadow-2xl transition-colors duration-200 focus:outline-none relative"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <X className="h-6 w-6" />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <MessageSquare className="h-6 w-6" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Chat window panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            transition={{ type: "spring", damping: 20 }}
            className="absolute bottom-18 right-0 w-[360px] sm:w-[440px] h-[490px] sm:h-[560px] rounded-3xl overflow-hidden glass shadow-2xl flex flex-col border border-white/20 dark:border-white/5"
          >
            {/* Header */}
            <div className="p-4 bg-gradient-to-r from-hospital-700 to-hospital-900 text-white flex items-center justify-between border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center border border-white/25">
                    <Shield className="h-5.5 w-5.5 text-hospital-300" />
                  </div>
                  <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 border-2 border-hospital-800"></span>
                </div>
                <div>
                  <h4 className="text-sm font-bold tracking-tight">Reallist AI Audit</h4>
                  <p className="text-[10px] text-hospital-300 font-medium">Dynamic Local Analytics Engine</p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {/* History Toggle Button */}
                <button 
                  onClick={() => setShowHistory(!showHistory)}
                  title="Search History"
                  className={`p-1.5 rounded-lg transition-colors ${showHistory ? 'bg-white/15 text-white' : 'text-hospital-200 hover:text-white hover:bg-white/10'}`}
                >
                  <History className="h-4 w-4" />
                </button>
                <button 
                  onClick={clearChat}
                  title="Clear Chat messages"
                  className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-hospital-200 hover:text-white"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-hospital-200 hover:text-white"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Main Content Area (Messages OR History Overlay) */}
            <div className="flex-grow relative overflow-hidden flex flex-col bg-slate-50/50 dark:bg-slate-900/30">
              {/* History Panel Drawer */}
              <AnimatePresence>
                {showHistory && (
                  <motion.div
                    initial={{ x: "-100%" }}
                    animate={{ x: 0 }}
                    exit={{ x: "-100%" }}
                    transition={{ type: "tween", duration: 0.25 }}
                    className="absolute inset-0 z-30 bg-white/95 dark:bg-slate-950/95 backdrop-blur-md p-4 flex flex-col"
                  >
                    <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800 pb-2 mb-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                        <Clock className="h-4 w-4 text-hospital-500" />
                        Conversation History
                      </h4>
                      {pastQueries.length > 0 && (
                        <button
                          onClick={clearHistory}
                          className="text-[10px] text-red-500 hover:underline font-bold uppercase tracking-wide"
                        >
                          Clear All
                        </button>
                      )}
                    </div>
                    
                    <div className="flex-grow overflow-y-auto space-y-2 pr-1">
                      {pastQueries.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-48 text-center text-slate-400 dark:text-slate-500">
                          <History className="h-8 w-8 mb-2 opacity-50" />
                          <p className="text-xs font-semibold">No past questions recorded yet.</p>
                          <p className="text-[10px] mt-0.5">Your questions will appear here for quick access.</p>
                        </div>
                      ) : (
                        pastQueries.map((q, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSendMessage(q)}
                            className="w-full text-left p-3 rounded-xl border border-slate-200/40 dark:border-slate-800 bg-white/40 dark:bg-slate-900/40 hover:bg-hospital-50/50 dark:hover:bg-hospital-950/20 hover:border-hospital-300 dark:hover:border-hospital-800 text-xs text-slate-700 dark:text-slate-300 font-semibold transition-all line-clamp-2"
                          >
                            {q}
                          </button>
                        ))
                      )}
                    </div>
                    
                    <button
                      onClick={() => setShowHistory(false)}
                      className="mt-4 w-full py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-300 rounded-xl transition-all"
                    >
                      Back to Chat
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Chat Messages */}
              <div className="flex-grow overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                  <div 
                    key={idx}
                    className={`flex gap-3 max-w-[88%] ${
                      msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                    }`}
                  >
                    {/* Avatar */}
                    <div className={`h-8 w-8 rounded-lg shrink-0 flex items-center justify-center text-xs font-bold ${
                      msg.sender === "user" 
                        ? "bg-hospital-100 text-hospital-700 border border-hospital-200/50" 
                        : "bg-hospital-600 text-white shadow-sm"
                    }`}>
                      {msg.sender === "user" ? <User className="h-4.5 w-4.5" /> : <Bot className="h-4.5 w-4.5" />}
                    </div>
                    {/* Bubble */}
                    <div className="space-y-1">
                      <div className={`p-3 rounded-2xl shadow-sm border ${
                        msg.sender === "user"
                          ? "bg-hospital-600 text-white border-hospital-700 rounded-tr-none"
                          : "bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border-slate-200/50 dark:border-slate-800 rounded-tl-none"
                      }`}>
                        {msg.sender === "user" ? (
                          <p className="text-xs md:text-sm leading-relaxed">{msg.text}</p>
                        ) : (
                          parseMarkdown(msg.text)
                        )}
                      </div>
                      {/* Timestamp & Tag */}
                      <div className={`flex items-center gap-1.5 text-[10px] text-slate-400 font-medium ${
                        msg.sender === "user" ? "justify-end" : "justify-start"
                      }`}>
                        <span>{msg.timestamp}</span>
                        {msg.intent && msg.intent !== "greeting" && msg.intent !== "fallback" && (
                          <>
                            <span>•</span>
                            <span className="text-hospital-600 dark:text-hospital-400 uppercase font-bold tracking-wide">{msg.intent.replace(/_/g, " ")}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex gap-3 max-w-[80%] mr-auto">
                    <div className="h-8 w-8 rounded-lg bg-hospital-600 text-white flex items-center justify-center shrink-0">
                      <Bot className="h-4.5 w-4.5" />
                    </div>
                    <div className="p-3 bg-white dark:bg-slate-800 border border-slate-200/50 dark:border-slate-800 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-1">
                      <span className="h-2 w-2 bg-hospital-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                      <span className="h-2 w-2 bg-hospital-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                      <span className="h-2 w-2 bg-hospital-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Quick Suggestions */}
            <div className="px-4 py-2 border-t border-slate-100 dark:border-slate-800 bg-white/20 dark:bg-slate-900/10">
              <p className="text-[10px] text-slate-400 font-bold mb-1.5 flex items-center gap-1 uppercase tracking-wide">
                <Sparkles className="h-3 w-3 text-amber-500 animate-pulse" /> Suggested queries
              </p>
              <div className="flex gap-1.5 overflow-x-auto pb-1.5 pr-2 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
                {suggestedQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(q)}
                    disabled={isTyping}
                    className="shrink-0 text-xs px-2.5 py-1 bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-800 hover:border-hospital-400 dark:hover:border-hospital-500 rounded-full text-slate-600 dark:text-slate-300 hover:text-hospital-600 dark:hover:text-hospital-400 transition-all font-semibold shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Bar */}
            <div className="p-4 border-t border-slate-200/40 dark:border-slate-800/50 bg-white dark:bg-slate-950 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask about risk, compliance, failures..."
                disabled={isTyping}
                className="flex-grow text-xs md:text-sm px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-hospital-500 font-medium"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={isTyping || !input.trim()}
                className="h-10 w-10 rounded-xl bg-hospital-600 hover:bg-hospital-700 disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white flex items-center justify-center shadow-md hover:shadow-hospital-500/10 transition-all"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
