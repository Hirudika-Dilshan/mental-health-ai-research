import { useState, useRef, useEffect } from 'react';
import '../ChatUI.css';

export default function ChatUI({ userId }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history on mount
  useEffect(() => {
    if (userId) {
      loadChatHistory();
    }
  }, [userId]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/chat/history/${userId}`);
      const data = await response.json();
      if (data.messages) {
        const formattedMessages = data.messages.map(msg => ({
          id: msg.id,
          text: msg.message,
          sender: msg.sender === 'user' ? 'user' : 'backend'
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    }
  };

  const handleSend = async () => {
    if (inputText.trim() && userId) {
      const newMessage = {
        id: Date.now(),
        text: inputText,
        sender: "user"
      };
      setMessages([...messages, newMessage]);
      const currentInput = inputText;
      setInputText("");

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: currentInput, user_id: userId }),
        });
        
        const data = await response.json();
        
        const backendMessage = {
          id: Date.now() + 1,
          text: data.response,
          sender: "backend"
        };
        setMessages(prev => [...prev, backendMessage]);
      } catch (error) {
        console.error("Error calling backend:", error);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-wrapper ${message.sender === 'user' ? 'user' : 'backend'}`}
          >
            <div className={`message-bubble ${message.sender}`}>
              {message.text}
            </div>
          </div>
        ))}
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
          />
          <button onClick={handleSend} className="send-button">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}