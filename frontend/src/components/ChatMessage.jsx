/**
 * ChatMessage component — Renders user or assistant messages.
 */

import SourceChip from './SourceChip';
import ReactMarkdown from 'react-markdown';
import { HiOutlineUser, HiOutlineSparkles } from 'react-icons/hi2';
import './ChatMessage.css';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'} ${isError ? 'error' : ''} animate-fade-in`}>
      <div className="message-avatar">
        {isUser ? (
          <HiOutlineUser />
        ) : (
          <HiOutlineSparkles />
        )}
      </div>

      <div className="message-body">
        <div className="message-header">
          <span className="message-role">{isUser ? 'You' : 'PhysioMind'}</span>
        </div>

        <div className="message-content">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Source Attribution */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <span className="sources-label">Sources:</span>
            <div className="sources-list">
              {message.sources.map((source, idx) => (
                <SourceChip
                  key={idx}
                  fileName={source.file_name}
                  pageNumber={source.page_number}
                  relevanceScore={source.relevance_score || 0}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
