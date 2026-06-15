import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Trash2, Shield, User, Bot, Sparkles } from "lucide-react";

// Helper to parse simple markdown (**bold**, - lists, ### headers, \n newlines)
function parseMarkdown(text) {
  if (!text) return "";
  
  // Split into lines to identify lists and headers
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
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I am the **Reallist AI Audit Assistant**. I run local calculations on the hospital audit CSV logs. Ask me anything about risk, compliance, audits, staff performance, or escalations!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    "Which ward has highest risk?",
    "Show pending audits.",
    "Show open escalations.",
    "Best performing staff?",
    "Is ICU hygiene risk increasing?",
    "NABH compliance trend this week",
    "Predict future risk.",
    "Show recommendations."
  ];

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

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

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Floating Action Button (FAB) */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={`h-14 w-14 rounded-full bg-hospital-600 hover:bg-hospital-700 text-white flex items-center justify-center shadow-2xl pulse-ring-btn transition-colors duration-200 focus:outline-none`}
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
            className="absolute bottom-18 right-0 w-[360px] sm:w-[420px] h-[480px] sm:h-[540px] rounded-3xl overflow-hidden glass shadow-2xl flex flex-col border border-white/20 dark:border-white/5"
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
                <button 
                  onClick={clearChat}
                  title="Clear Conversation"
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

            {/* Chat Messages */}
            <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-slate-50/50 dark:bg-slate-900/30">
              {messages.map((msg, idx) => (
                <div 
                  key={idx}
                  className={`flex gap-3 max-w-[85%] ${
                    msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                  }`}
                >
                  {/* Avatar */}
                  <div className={`h-8 w-8 rounded-lg shrink-0 flex items-center justify-center text-xs font-bold ${
                    msg.sender === "user" 
                      ? "bg-hospital-100 text-hospital-700 border border-hospital-200/50" 
                      : "bg-hospital-600 text-white"
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
                      {msg.intent && msg.intent !== "greeting" && (
                        <>
                          <span>•</span>
                          <span className="text-hospital-600 dark:text-hospital-400 uppercase font-semibold">{msg.intent.replace(/_/g, " ")}</span>
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

            {/* Quick Suggestions */}
            <div className="px-4 py-2 border-t border-slate-100 dark:border-slate-800 bg-white/20 dark:bg-slate-900/10">
              <p className="text-[10px] text-slate-400 font-bold mb-1.5 flex items-center gap-1 uppercase tracking-wide">
                <Sparkles className="h-3 w-3 text-amber-500" /> Suggested queries
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
                placeholder="Ask about risk, compliance, failed audits..."
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
