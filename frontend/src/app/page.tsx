'use client';

import { useState, useRef, useEffect } from 'react';
import { sendMessage } from './api/chat'; // Ensure sendMessage returns ApiResponse
import { Bot, User, Moon, Sun, RefreshCw } from 'lucide-react';

interface Message {
  sender: string;
  text: string;
  timestamp?: Date;
  error?: boolean;
  id: string;
  source?: string;
}

interface ApiResponse {
  response: string | { message?: string; source?: string; [key: string]: any };
  final_answer?: string;
  source?: string;
}

const formatTime = (date?: Date) => {
  if (!date) return '';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [messages, darkMode]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (retryMessage?: Message) => {
    const message = retryMessage ? retryMessage.text : input.trim();
    if (!message) return;

    setInput('');
    setLoading(true);
    
    const userMsg = { 
      sender: 'You', 
      text: message,
      timestamp: new Date(),
      id: `user-${Date.now()}`
    };
    
    setMessages(prev => [...prev, userMsg]);

    try {
      const apiResponse = await sendMessage(message);
      let responseText = '';
      
      if (typeof apiResponse.response === 'string') {
        responseText = apiResponse.response;
      } else {
        const responseObj = apiResponse.response;
        responseText = responseObj.message || 
                     (responseObj as any).final_answer || 
                     JSON.stringify(responseObj);
      }

      const aiMsg = {
        sender: 'AI',
        text: responseText,
        timestamp: new Date(),
        id: `ai-${Date.now()}`,
        source: apiResponse.source || 'assistant'
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = { 
        sender: 'AI', 
        text: `⚠️ Error: ${err instanceof Error ? err.message : 'Service unavailable'}`,
        timestamp: new Date(),
        error: true,
        id: `error-${Date.now()}`
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = (message: Message) => {
    handleSend(message);
    setMessages(prev => prev.filter(m => m.id !== message.id));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      handleSend();
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`flex flex-col h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex-1 flex flex-col max-w-4xl w-full mx-auto p-4 bg-gray-50 dark:bg-gray-900">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-xl font-bold dark:text-white">Chat</h1>
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto mb-4 rounded-lg bg-white dark:bg-gray-800 shadow-sm p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.sender === "You" ? "justify-end" : "justify-start"}`}>
              {msg.sender === "AI" && (
                <div key={`icon-${msg.id}`} className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                  <Bot className="h-5 w-5 text-primary-foreground" />
                </div>
              )}
              <div key={`bubble-${msg.id}`} className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.sender === "You" 
                  ? "ml-auto bg-blue-500 text-white" 
                  : msg.error 
                    ? "bg-red-100 dark:bg-red-900/50" 
                    : "bg-gray-100 dark:bg-gray-700"
              }`}>
                <div className="whitespace-pre-wrap text-sm">{msg.text}</div>
                {msg.error && (
                  <button 
                    key={`retry-${msg.id}`}
                    onClick={() => handleRetry(msg)}
                    className="mt-2 flex items-center gap-1 text-xs text-red-600 dark:text-red-300 hover:underline"
                  >
                    <RefreshCw className="h-3 w-3" />
                    Try again
                  </button>
                )}
                <div className={`text-xs mt-2 ${
                  msg.sender === "You" 
                    ? "text-blue-100" 
                    : msg.error
                      ? "text-red-500 dark:text-red-300"
                      : "text-gray-500 dark:text-gray-400"
                }`}>
                  {formatTime(msg.timestamp)}
                </div>
              </div>
              {msg.sender === "You" && (
                <div key={`user-icon-${msg.id}`} className="flex-shrink-0 h-8 w-8 rounded-full bg-accent flex items-center justify-center">
                  <User className="h-5 w-5 text-accent-foreground" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div key={`loading-${Date.now()}`} className="flex gap-3 justify-start">
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
          <div key="end-ref" ref={messagesEndRef} />
        </div>

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
              onClick={() => handleSend()}
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