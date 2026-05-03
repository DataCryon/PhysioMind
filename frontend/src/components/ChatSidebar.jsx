import { HiOutlinePlus, HiOutlineChatBubbleLeft, HiOutlineTrash, HiOutlineXMark } from 'react-icons/hi2';
import './ChatSidebar.css';

export default function ChatSidebar({ sessions, currentSessionId, onSelect, onNew, onDelete, onClose, isOpen }) {
  return (
    <div className={`chat-sidebar glass ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header mobile-only">
        <span className="sidebar-title">Chat History</span>
        <button className="btn btn-ghost close-sidebar-btn" onClick={onClose}>
          <HiOutlineXMark />
        </button>
      </div>

      <button className="btn btn-primary new-chat-btn" onClick={onNew}>
        <HiOutlinePlus />
        New Chat
      </button>

      <div className="sessions-list">
        <span className="sidebar-label">Recent Chats</span>
        {sessions.map((session) => (
          <div 
            key={session.id} 
            className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
            onClick={() => onSelect(session.id)}
          >
            <HiOutlineChatBubbleLeft className="session-icon" />
            <span className="session-title">{session.title}</span>
            <button 
              className="delete-session-btn" 
              onClick={(e) => {
                e.stopPropagation();
                onDelete(session.id);
              }}
            >
              <HiOutlineTrash />
            </button>
          </div>
        ))}

        {sessions.length === 0 && (
          <div className="no-sessions">No recent chats</div>
        )}
      </div>
    </div>
  );
}
