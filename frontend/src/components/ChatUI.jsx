import { useState, useRef, useEffect } from 'react';
import '../ChatUI.css';

export default function ChatUI() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I help you?", sender: "backend" },
    { id: 2, text: "Hi there!", sender: "user" }
  ]);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (inputText.trim()) {
      const newMessage = {
        id: Date.now(),
        text: inputText,
        sender: "user"
      };
      setMessages([...messages, newMessage]);
      setInputText("");

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: inputText }),
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