import { useState, useRef, useEffect, useCallback } from 'react';
import ChatHistory from './ChatHistory';
import '../ChatUI.css';

export default function ChatUI({ userId, onLogout }) {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showCrisisWarning, setShowCrisisWarning] = useState(false);
  const messagesEndRef = useRef(null);

  const API_URL = process.env.REACT_APP_API_URL || '/api';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadSessions = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/sessions/${userId}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      setSessions(data.sessions || []);
      
      if (!currentSessionId && data.sessions && data.sessions.length > 0) {
        setCurrentSessionId(data.sessions[0].id);
      }
    } catch (error) {
      console.error("Error loading sessions:", error);
      setSessions([]);
    }
  }, [API_URL, userId, currentSessionId]);

  const loadProtocolState = useCallback(async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      // Protocol state loaded but not currently used in UI
      // Can be used for future features
      console.log('Protocol state:', data.protocol_state);
    } catch (error) {
      console.error("Error loading protocol state:", error);
    }
  }, [API_URL]);

  const loadSessionMessages = useCallback(async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      
      if (data.messages) {
        const formattedMessages = data.messages.map(msg => ({
          id: msg.id,
          text: msg.message,
          sender: msg.sender === 'user' ? 'user' : 'backend',
          timestamp: msg.created_at
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error loading messages:", error);
      setMessages([]);
    }
  }, [API_URL]);

  useEffect(() => {
    if (userId) {
      loadSessions();
    }
  }, [userId, loadSessions]);

  useEffect(() => {
    if (currentSessionId) {
      loadSessionMessages(currentSessionId);
      loadProtocolState(currentSessionId);
    } else {
      setMessages([]);
    }
  }, [currentSessionId, loadSessionMessages, loadProtocolState]);

  const handleNewChat = async () => {
    try {
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
      
      setSessions(prev => [data.session, ...prev]);
      setCurrentSessionId(data.session.id);
      setMessages([]);
      setShowCrisisWarning(false);
      
      // Automatically send first message to start protocol
      setTimeout(() => {
        sendInitialMessage(data.session.id);
      }, 500);
    } catch (error) {
      console.error("Error creating new chat:", error);
      alert(`Failed to create new chat: ${error.message}`);
    }
  };

  const sendInitialMessage = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: "Hello", 
          user_id: userId,
          session_id: sessionId 
        }),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      
      const backendMessage = {
        id: Date.now(),
        text: data.response,
        sender: "backend"
      };
      
      setMessages([backendMessage]);
      await loadSessions();
    } catch (error) {
      console.error("Error sending initial message:", error);
    }
  };

  const handleSelectSession = (sessionId) => {
    setCurrentSessionId(sessionId);
    setShowCrisisWarning(false);
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      
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
    if (!inputText.trim() || isLoading) return;
    
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
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      
      // Check for crisis
      if (data.crisis) {
        setShowCrisisWarning(true);
      }
      
      // If this was a new chat, update session ID
      if (!currentSessionId && data.session_id) {
        setCurrentSessionId(data.session_id);
      }
      
      const backendMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: "backend"
      };
      
      setMessages(prev => [...prev, backendMessage]);
      await loadSessions();
    } catch (error) {
      console.error("Error sending message:", error);
      
      // Show error message in chat
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, there was an error processing your message. Please try again.",
        sender: "backend"
      };
      setMessages(prev => [...prev, errorMessage]);
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
          <div>
            <h2>GAD-7 Mental Health Screening</h2>
            <p className="subtitle">Conversational AI for Anxiety Assessment</p>
          </div>
          <button onClick={onLogout} className="logout-btn">
            Logout
          </button>
        </div>

        {showCrisisWarning && (
          <div className="crisis-banner">
            <strong>⚠️ Crisis Resources Available</strong>
            <p>If you're in crisis, please contact: 1926 (24/7) or 070 2211311</p>
          </div>
        )}

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h2>Welcome to GAD-7 Screening</h2>
              <p>Click "New Chat" to begin a new anxiety assessment</p>
              <div className="info-box">
                <h3>What is GAD-7?</h3>
                <p>The GAD-7 is a validated screening tool for generalized anxiety disorder. This conversational version will ask you 7 questions about your experiences over the past 2 weeks.</p>
                <p><strong>Remember:</strong> This is a screening tool, not a diagnosis. Only a healthcare professional can provide a proper assessment.</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message-wrapper ${message.sender}`}
                >
                  <div className={`message-bubble ${message.sender}`}>
                    {message.text.split('\n').map((line, i) => (
                      <span key={i}>
                        {line}
                        {i < message.text.split('\n').length - 1 && <br />}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </>
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
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your response..."
              className="message-input"
              disabled={isLoading}
              rows="2"
            />
            <button 
              onClick={handleSend} 
              className="send-button"
              disabled={!inputText.trim() || isLoading}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          <div className="input-footer">
            <small>Press Enter to send, Shift+Enter for new line</small>
          </div>
        </div>
      </div>
    </div>
  );
}