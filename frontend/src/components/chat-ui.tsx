"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, User } from "lucide-react";
import { sendMessage } from "../app/api/chat";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

const formatTime = (date?: Date) => {
  if (!date) return '';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export default function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    const message = input.trim();
    if (!message || loading) return;

    setInput("");
    setLoading(true);
    
    // Add user message
    setMessages(prev => [...prev, { 
      role: "user", 
      content: message,
      timestamp: new Date() 
    }]);

    try {
      // Get AI response
      const response = await sendMessage(message);
      const responseContent = typeof response === 'object' 
        ? response.response 
        : response;
      
      // Add AI message
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: typeof responseContent === 'string' 
          ? responseContent 
          : JSON.stringify(responseContent),
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error('API Error:', err);
      let errorMessage = 'Service unavailable';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        errorMessage = JSON.stringify(err);
      }

      setMessages(prev => [...prev, {
        role: "assistant",
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex-1 flex flex-col max-w-4xl w-full mx-auto p-4">
        {/* Messages container */}
        <div className="flex-1 overflow-y-auto mb-4 rounded-lg bg-white dark:bg-gray-800 shadow-sm p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                  <Bot className="h-5 w-5 text-primary-foreground" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === "user" 
                  ? "ml-auto bg-blue-500 text-white" 
                  : "bg-gray-100 dark:bg-gray-700"
              }`}>
                <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                <div className={`text-xs mt-2 ${
                  msg.role === "user" ? "text-blue-100" : "text-gray-500 dark:text-gray-400"
                }`}>
                  {formatTime(msg.timestamp)}
                </div>
              </div>
              {msg.role === "user" && (
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-accent flex items-center justify-center">
                  <User className="h-5 w-5 text-accent-foreground" />
                </div>
              )}
            </div>
          ))}
          
          {/* Loading indicator */}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="bg-muted text-muted-foreground rounded-lg px-4 py-2">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"></div>
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce delay-100"></div>
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 border p-2 rounded-full dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading}
              className="px-4 py-2 rounded-full bg-blue-500 hover:bg-blue-600 text-white disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
