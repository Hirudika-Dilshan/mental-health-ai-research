import React, { useState } from 'react';
import './ChatHistory.css';

export default function ChatHistory({ 
  sessions, 
  currentSessionId, 
  onSelectSession, 
  onNewChat, 
  onDeleteSession 
}) {
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const handleDelete = (sessionId, e) => {
    e.stopPropagation();
    if (deleteConfirm === sessionId) {
      onDeleteSession(sessionId);
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(sessionId);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      return date.toLocaleDateString();
    } catch (error) {
      return 'Unknown';
    }
  };

  // Safety check: ensure sessions is an array
  const sessionList = Array.isArray(sessions) ? sessions : [];

  return (
    <div className="chat-history">
      <div className="chat-history-header">
        <h3>Chats</h3>
        <button onClick={onNewChat} className="new-chat-btn">
          + New Chat
        </button>
      </div>
      
      <div className="chat-list">
        {sessionList.length === 0 ? (
          <div className="no-chats">
            No chats yet.<br/>Start a conversation!
          </div>
        ) : (
          sessionList.map(session => (
            <div
              key={session.id}
              className={`chat-item ${session.id === currentSessionId ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
            >
              <div className="chat-item-content">
                <div className="chat-title">{session.title || 'Untitled Chat'}</div>
                <div className="chat-info">
                  {session.message_count || 0} msgs • {formatDate(session.updated_at)}
                </div>
              </div>
              <button
                className="delete-btn"
                onClick={(e) => handleDelete(session.id, e)}
                title={deleteConfirm === session.id ? "Click again to confirm" : "Delete chat"}
              >
                {deleteConfirm === session.id ? '✓' : '×'}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}