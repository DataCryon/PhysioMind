import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { HiOutlineChatBubbleLeftRight, HiOutlineTrash, HiOutlineSparkles, HiOutlineDocumentText, HiOutlineClock } from 'react-icons/hi2';
import { useChat } from '../hooks/useChat';
import { useDocuments } from '../hooks/useDocuments';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import './Chat.css';

import ChatSidebar from '../components/ChatSidebar';

export default function Chat() {
  const { 
    messages, 
    sessions, 
    currentSessionId, 
    loading, 
    ask, 
    clearChat, 
    selectSession, 
    startNewSession, 
    deleteSession 
  } = useChat();
  const { documents, loading: docsLoading } = useDocuments();
  const [selectedFileId, setSelectedFileId] = useState('all');
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  const hasDocuments = documents.length > 0;

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Close sidebar when a session is selected on mobile
  const handleSelectSession = (id) => {
    selectSession(id);
    setShowSidebar(false);
  };

  const handleSend = (question, systemPrompt) => {
    const fileId = selectedFileId === 'all' ? null : selectedFileId;
    ask(question, fileId, systemPrompt);
  };

  return (
    <div className={`chat-container-layout ${showSidebar ? 'sidebar-open' : ''}`}>
      {/* Overlay for mobile sidebar */}
      <div 
        className="sidebar-overlay mobile-only" 
        onClick={() => setShowSidebar(false)}
      />

      <ChatSidebar 
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelect={handleSelectSession}
        onNew={() => {
          startNewSession();
          setShowSidebar(false);
        }}
        onDelete={deleteSession}
        onClose={() => setShowSidebar(false)}
        isOpen={showSidebar}
      />

      <div className="chat-page">
        {/* Header */}
        <div className="chat-header animate-fade-in">
          <div className="chat-header-left">
            <button 
              className="btn btn-ghost history-toggle mobile-only"
              onClick={() => setShowSidebar(true)}
              title="Chat history"
            >
              <HiOutlineClock />
            </button>

            <h1 className="page-title">
              <HiOutlineChatBubbleLeftRight className="header-icon desktop-only" />
              <span className="gradient-text">Chat</span>
            </h1>
            
            {hasDocuments && (
              <div className="chat-filter">
                <HiOutlineDocumentText className="filter-icon" />
                <select 
                  value={selectedFileId} 
                  onChange={(e) => setSelectedFileId(e.target.value)}
                  className="filter-select"
                  disabled={loading}
                >
                  <option value="all">All Documents</option>
                  {documents.map(doc => (
                    <option key={doc.id} value={doc.id}>
                      {doc.file_name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
          
          <div className="chat-header-actions">
            {messages.length > 0 && (
              <button
                className="btn btn-ghost"
                onClick={clearChat}
                id="clear-chat-btn"
              >
                <HiOutlineTrash />
                <span className="desktop-only">Clear</span>
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="chat-empty animate-fade-in">
              <div className="chat-empty-icon">
                <HiOutlineSparkles />
              </div>
              <h3>How can I help you?</h3>
              <p>
                {hasDocuments
                  ? 'Ask me anything about your uploaded documents.'
                  : 'Upload some PDF documents first, then come back to ask questions.'
                }
              </p>

              {hasDocuments && (
                <div className="suggestion-chips">
                  <button
                    className="suggestion-chip"
                    onClick={() => handleSend('Give me a summary of the uploaded documents.')}
                    disabled={loading}
                  >
                    📄 Summarize documents
                  </button>
                  <button
                    className="suggestion-chip"
                    onClick={() => handleSend('What are the key topics covered in the documents?')}
                    disabled={loading}
                  >
                    🔍 Key topics
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {/* Typing indicator */}
              {loading && (
                <div className="typing-indicator">
                  <div className="message-avatar assistant-avatar">
                    <HiOutlineSparkles />
                  </div>
                  <div className="typing-dots">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput
          onSend={handleSend}
          loading={loading}
          disabled={!hasDocuments}
        />
      </div>
    </div>
  );
}
