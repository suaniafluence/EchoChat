import { useState, useRef, useEffect } from 'react';
import { Send, X, MessageCircle } from 'lucide-react';
import { chatAPI, ChatSource } from '@/lib/api';
import ReactMarkdown, { Components } from 'react-markdown';
import type { HTMLAttributes, ReactNode } from 'react';

type CodeProps = HTMLAttributes<HTMLElement> & {
  node?: unknown;
  inline?: boolean;
  className?: string;
  children?: ReactNode;
};

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
}

export default function Chat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    // Check loading state first to prevent duplicate submissions
    if (isLoading) return;
    if (!input.trim()) return;

    // Set loading immediately to prevent race conditions from rapid clicks
    setIsLoading(true);

    // Capture input value before clearing to avoid race conditions
    const messageText = input.trim();

    const userMessage: Message = {
      role: 'user',
      content: messageText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await chatAPI.sendMessage({
        message: messageText,
        conversation_history: conversationHistory,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: error.response?.data?.detail || 'Sorry, an error occurred. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const codeComponent = ({ inline, className, children, ...props }: CodeProps) => {
    if (inline) {
      return (
        <code
          className={`bg-gray-200 text-gray-900 rounded px-1 py-0.5 text-[0.85rem] ${className || ''}`.trim()}
          {...props}
        >
          {children}
        </code>
      );
    }

    return (
      <pre className="bg-gray-900 text-gray-100 rounded-md p-3 overflow-x-auto text-sm">
        <code className={className} {...props}>
          {children}
        </code>
      </pre>
    );
  };

  const markdownComponents: Components = {
    a: ({ node, ...props }) => (
      <a
        {...props}
        className="text-primary-700 hover:underline break-words"
        target="_blank"
        rel="noopener noreferrer"
      />
    ),
    p: ({ node, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed" {...props} />,
    ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1" {...props} />,
    ol: ({ node, ...props }) => <ol className="list-decimal list-inside space-y-1" {...props} />,
    code: codeComponent,
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 bg-primary-600 hover:bg-primary-700 text-white rounded-full p-3 sm:p-4 shadow-lg transition-all duration-200 z-50 touch-manipulation min-w-[56px] min-h-[56px] flex items-center justify-center"
          aria-label="Ouvrir le chat"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {isOpen && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-6 sm:right-6 w-full sm:max-w-md sm:w-96 h-full sm:h-[600px] max-h-screen sm:max-h-[80vh] bg-white sm:rounded-lg shadow-2xl flex flex-col z-50">
          <div className="bg-primary-600 text-white p-4 sm:rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold text-base sm:text-lg">Chat Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-primary-700 rounded p-1.5 sm:p-1 transition touch-manipulation"
              aria-label="Fermer le chat"
            >
              <X size={20} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <MessageCircle size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-sm">Ask me anything about the website!</p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] sm:max-w-[80%] rounded-lg p-3 sm:p-3 ${message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
                  <ReactMarkdown
                    className="text-sm sm:text-sm prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-900 prose-li:text-gray-900 prose-strong:text-gray-900 break-words"
                    components={markdownComponents}
                  >
                    {message.content}
                  </ReactMarkdown>
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-300 text-xs">
                      <p className="font-semibold mb-2">Sources:</p>
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="mb-2">
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-700 hover:underline"
                          >
                            {source.title}
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="p-3 sm:p-4 border-t bg-white">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Écrivez votre message..."
                className="flex-1 px-3 sm:px-4 py-2.5 sm:py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm sm:text-base text-gray-900 placeholder-gray-500 touch-manipulation"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="bg-primary-600 hover:bg-primary-700 text-white rounded-lg px-4 sm:px-4 py-2.5 sm:py-2 transition disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation min-w-[44px] min-h-[44px] flex items-center justify-center"
                aria-label="Envoyer le message"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
