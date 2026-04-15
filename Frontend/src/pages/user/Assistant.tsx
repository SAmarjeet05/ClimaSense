import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader, MessageSquare, Settings } from 'lucide-react';
import { api } from '../../services/api';
import { loggerService } from '../../services/logger';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

// Rotating border animation
const styles = `
  @keyframes rotateBorderGradient {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }

  @keyframes streamingCursor {
    0%, 49% {
      opacity: 1;
    }
    50%, 100% {
      opacity: 0;
    }
  }

  .streaming-cursor::after {
    content: '▌';
    animation: streamingCursor 0.7s infinite;
    margin-left: 2px;
  }

  .rotating-border-input {
    position: relative;
    display: flex;
    align-items: center;
    border-radius: 1rem;
    background: linear-gradient(90deg, #3b82f6, #6366f1, #8b5cf6, #ec4899, #f59e0b, #3b82f6);
    background-size: 200% 100%;
    animation: rotateBorderGradient 4s linear infinite;
    padding: 3px;
  }

  .rotating-border-input input {
    width: 100%;
    border-radius: 0.875rem;
    background: #1a1a2e;
  }

  .markdown-content h2 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-top: 0.75rem;
    margin-bottom: 0.5rem;
    color: inherit;
  }

  .markdown-content h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
    color: inherit;
  }

  .markdown-content p {
    margin-bottom: 0.5rem;
    line-height: 1.6;
  }

  .markdown-content ul,
  .markdown-content ol {
    margin-left: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .markdown-content li {
    margin-bottom: 0.25rem;
  }

  .markdown-content strong {
    font-weight: 600;
    color: inherit;
  }

  .markdown-content em {
    font-style: italic;
  }

  .markdown-content code {
    background-color: rgba(0, 0, 0, 0.2);
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.875em;
  }

`;

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
  data?: any;
  suggestedAction?: string;
  actionUrl?: string;
  mapMode?: string;
  scenarioMode?: string;
  cities?: string[];
  isStreaming?: boolean;
}

interface SuggestedQuery {
  text: string;
  icon: string;
}

export const Assistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Load suggested queries on mount
  useEffect(() => {
    loadSuggestedQueries();
    // Add welcome message
    setMessages([
      {
        id: 'welcome',
        type: 'assistant',
        content: '👋 Welcome to the Climate Intelligence Assistant! I can help you explore weather patterns, compare cities, analyze climate risks, and answer questions about climate change in India.',
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSuggestedQueries = async () => {
    try {
      const response = await fetch('https://climasense-production.up.railway.app/api/assistant/suggested-queries');
      const data = await response.json();
      if (data.status === 'success') {
        setSuggestedQueries(data.suggested_queries);
      }
    } catch (err) {
      console.error('Failed to load suggested queries:', err);
      setSuggestedQueries([
        'Will Delhi become hotter?',
        'Compare Mumbai and Bangalore temperature',
        'What cities have high climate risk?',
        'Show historical trends for rainfall',
      ]);
    }
  };

  const handleSendMessage = async (query?: string) => {
    const messageText = query || inputValue.trim();
    
    if (!messageText) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Log user action
      loggerService.logAction(
        'assistant_query',
        { query: messageText.substring(0, 100) }
      );

      // Call assistant API
      const response = await fetch('https://climasense-production.up.railway.app/api/assistant/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: messageText,
          user_id: null,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();

      if (result.status === 'success') {
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          type: 'assistant',
          content: '',  // Start with empty content, will be filled by streaming
          timestamp: result.timestamp,
          intent: result.intent,
          data: result.data,
          suggestedAction: result.suggested_action,
          actionUrl: result.action_url,
          mapMode: result.map_mode,
          scenarioMode: result.scenario_mode,
          cities: result.cities,
          isStreaming: true,  // Mark as streaming
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // Stream the response word by word
        await streamResponse(assistantMessage.id, result.answer);
      } else {
        throw new Error(result.error || 'Unknown error');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      
      const errorAssistantMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `❌ ${errorMessage}. Please make sure the backend server is running.`,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const streamResponse = async (messageId: string, fullText: string) => {
    // Split text into words while preserving newlines and formatting
    // Matches either words or newline sequences to preserve markdown structure
    const tokens = fullText.match(/\S+|(?:\n\s*)+/g) || [];
    let displayedContent = '';
    
    // Stream tokens with slight delay for visual effect
    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i];
      // Add space before word tokens, but not before newlines
      if (i === 0) {
        displayedContent = token;
      } else if (token.includes('\n')) {
        displayedContent += token;
      } else {
        displayedContent += ' ' + token;
      }
      
      // Update message content
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? {
                ...msg,
                content: displayedContent,
                isStreaming: i < tokens.length - 1,
              }
            : msg
        )
      );
      
      // Add delay between tokens (30ms for smooth streaming)
      await new Promise(resolve => setTimeout(resolve, 30));
    }
  };

  const handleSuggestedQuery = (query: string) => {
    handleSendMessage(query);
  };

  const handleNavigate = (url: string, mapMode?: string, cities?: string[], scenarioMode?: string) => {
    // Handle comparison navigation
    if (url.includes('/insights-comparison')) {
      navigate(url.split('?')[0], { state: { cities } });
    }
    // Handle map navigation (including scenario)
    else if (url.includes('/map')) {
      const modeParam = new URLSearchParams(url.split('?')[1]).get('mode');
      const scenarioParam = new URLSearchParams(url.split('?')[1]).get('scenario');
      const mode = mapMode || modeParam;
      const scenario = scenarioMode || scenarioParam;
      navigate(url.split('?')[0], { state: { mode, scenario } });
    }
    // Default navigation
    else {
      navigate(url);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      <style>{styles}</style>
      
      {/* Header - NOT scrollable */}
      <div className="border-b border-border/10 bg-background/95 backdrop-blur-md shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Climate Assistant</h1>
              <p className="text-sm text-muted-foreground">AI-Powered Climate Intelligence</p>
            </div>
          </div>
        </div>
      </div>

      {/* Scrollable Messages Container - ONLY THIS SCROLLS */}
      <div className="flex-1 overflow-y-auto bg-background">
        <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground text-lg">No messages yet. Start a conversation!</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl px-6 py-4 rounded-lg glass ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-br-none border-2 border-blue-400/50'
                      : 'rounded-bl-none border-2 border-cyan-500/40'
                  }`}
                >
                  {message.type === 'user' ? (
                    <p className="leading-relaxed">{message.content}</p>
                  ) : (
                    <div className={`markdown-content ${message.isStreaming ? 'streaming-cursor' : ''}`}>
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  )}
                  
                  {/* Suggested Action Button */}
                  {message.type === 'assistant' && message.suggestedAction && message.actionUrl && !message.isStreaming && (
                    <button
                      onClick={() => handleNavigate(message.actionUrl!, message.mapMode, message.cities, message.scenarioMode)}
                      className="mt-3 px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg text-sm font-medium hover:shadow-lg transition-shadow hover:from-blue-500 hover:to-indigo-500"
                    >
                      {message.suggestedAction} →
                    </button>
                  )}
                  
                  <p className="text-xs opacity-60 mt-2">
                    {message.intent && `Intent: ${message.intent}`}
                    {message.isStreaming && ' • Streaming...'}
                  </p>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="glass border border-border/20 rounded-lg rounded-bl-none px-6 py-4">
                <div className="flex items-center gap-3">
                  <Loader className="w-5 h-5 animate-spin text-blue-500" />
                  <p className="text-foreground">Thinking...</p>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggested Queries (Only shown when chat is empty) */}
      {messages.length <= 1 && suggestedQueries.length > 0 && !isLoading && (
        <div className="border-t border-border/10 bg-background/95 backdrop-blur-md px-6 py-4">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm font-semibold text-foreground mb-3">Try asking:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {suggestedQueries.slice(0, 4).map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedQuery(query)}
                  className="text-left px-4 py-3 glass border-2 border-indigo-500/40 rounded-lg hover:bg-card/50 hover:border-indigo-500/60 transition-all text-sm text-foreground hover:text-foreground font-medium"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Fixed Input Area at Bottom - NOT scrollable */}
      <div className="border-t border-border/10 bg-background/95 backdrop-blur-md shadow-lg">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-3"
          >
            <div className="flex-1 rotating-border-input rounded-2xl">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask me about climate, weather, or trends..."
                className="w-full px-4 py-3 glass rounded-2xl focus:outline-none focus:border-transparent bg-card/30 text-foreground placeholder-muted-foreground"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl font-medium hover:shadow-lg hover:from-blue-500 hover:to-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>
          {error && (
            <p className="text-sm text-destructive mt-2">⚠️ {error}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Assistant;
