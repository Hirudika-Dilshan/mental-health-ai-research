import { useState, useRef, useEffect } from 'react';
import ChatHistory from './ChatHistory';
import '../ChatUI.css';

export default function ChatUI({ userId, onLogout }) {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const API_URL = 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load sessions on mount
  useEffect(() => {
    if (userId) {
      loadSessions();
    }
  }, [userId]);

  // Load messages when session changes
  useEffect(() => {
    if (currentSessionId) {
      loadSessionMessages(currentSessionId);
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  const loadSessions = async () => {
    try {
      console.log('Loading sessions for user:', userId);
      const response = await fetch(`${API_URL}/sessions/${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Loaded sessions:', data);
      
      setSessions(data.sessions || []);
      
      // If no current session and sessions exist, select the first one
      if (!currentSessionId && data.sessions && data.sessions.length > 0) {
        setCurrentSessionId(data.sessions[0].id);
      }
    } catch (error) {
      console.error("Error loading sessions:", error);
      setSessions([]);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      console.log('Loading messages for session:', sessionId);
      const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Loaded messages:', data);
      
      if (data.messages) {
        const formattedMessages = data.messages.map(msg => ({
          id: msg.id,
          text: msg.message,
          sender: msg.sender === 'user' ? 'user' : 'backend'
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error loading messages:", error);
      setMessages([]);
    }
  };

  const handleNewChat = async () => {
    try {
      console.log('Creating new chat for user:', userId);
      const response = await fetch(`${API_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Created session:', data);
      
      // Add new session to list and select it
      setSessions(prev => [data.session, ...prev]);
      setCurrentSessionId(data.session.id);
      setMessages([]);
    } catch (error) {
      console.error("Error creating new chat:", error);
      alert(`Failed to create new chat: ${error.message}`);
    }
  };

  const handleSelectSession = (sessionId) => {
    setCurrentSessionId(sessionId);
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Remove from list
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      
      // If deleted current session, switch to another
      if (sessionId === currentSessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId);
        if (remaining.length > 0) {
          setCurrentSessionId(remaining[0].id);
        } else {
          setCurrentSessionId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error("Error deleting session:", error);
      alert(`Failed to delete chat: ${error.message}`);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    const newMessage = {
      id: Date.now(),
      text: inputText,
      sender: "user"
    };
    
    setMessages(prev => [...prev, newMessage]);
    const currentInput = inputText;
    setInputText("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: currentInput, 
          user_id: userId,
          session_id: currentSessionId 
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // If this was a new chat (no session_id), update the current session
      if (!currentSessionId && data.session_id) {
        setCurrentSessionId(data.session_id);
      }
      
      const backendMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: "backend"
      };
      
      setMessages(prev => [...prev, backendMessage]);
      
      // Reload sessions to update metadata
      await loadSessions();
    } catch (error) {
      console.error("Error sending message:", error);
      alert(`Failed to send message: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app-container">
      <ChatHistory
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
      />
      
      <div className="chat-main">
        <div className="chat-header">
          <h2>Mental Health AI Chat</h2>
          <button onClick={onLogout} className="logout-btn">
            Logout
          </button>
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h2>Start a new conversation</h2>
              <p>Send a message to begin chatting</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message-wrapper ${message.sender}`}
              >
                <div className={`message-bubble ${message.sender}`}>
                  {message.text}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message-wrapper backend">
              <div className="message-bubble backend">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              className="message-input"
              disabled={isLoading}
            />
            <button 
              onClick={handleSend} 
              className="send-button"
              disabled={!inputText.trim() || isLoading}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}