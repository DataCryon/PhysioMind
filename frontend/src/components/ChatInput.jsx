/**
 * ChatInput component — Message input with system prompt toggle.
 */

import { useState, useRef } from 'react';
import { HiOutlinePaperAirplane, HiOutlineAdjustmentsHorizontal, HiOutlineXMark } from 'react-icons/hi2';
import './ChatInput.css';

export default function ChatInput({ onSend, loading, disabled }) {
  const [question, setQuestion] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    onSend(trimmed, systemPrompt.trim() || null);
    setQuestion('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-wrapper">
      {/* System Prompt Panel */}
      {showSystemPrompt && (
        <div className="system-prompt-panel animate-slide-up">
          <div className="system-prompt-header">
            <span className="system-prompt-label">
              <HiOutlineAdjustmentsHorizontal />
              Custom Instruction
            </span>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setShowSystemPrompt(false)}
              id="close-system-prompt"
            >
              <HiOutlineXMark />
            </button>
          </div>
          <textarea
            className="input system-prompt-input"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="e.g., Answer in bullet points and keep responses under 200 words..."
            rows={3}
            id="system-prompt-textarea"
          />
        </div>
      )}

      {/* Main Input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <button
          type="button"
          className={`btn btn-ghost system-prompt-toggle ${showSystemPrompt ? 'active' : ''} ${systemPrompt ? 'has-value' : ''}`}
          onClick={() => setShowSystemPrompt(!showSystemPrompt)}
          title="Custom instruction"
          id="toggle-system-prompt"
        >
          <HiOutlineAdjustmentsHorizontal />
        </button>

        <input
          ref={inputRef}
          type="text"
          className="input chat-text-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Upload documents first to start chatting...' : 'Ask a question about your documents...'}
          disabled={loading || disabled}
          id="chat-question-input"
        />

        <button
          type="submit"
          className="btn btn-primary send-btn"
          disabled={!question.trim() || loading || disabled}
          id="send-question-btn"
        >
          {loading ? (
            <div className="send-spinner" />
          ) : (
            <HiOutlinePaperAirplane />
          )}
        </button>
      </form>
    </div>
  );
}
