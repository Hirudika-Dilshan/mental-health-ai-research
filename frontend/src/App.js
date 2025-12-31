import React, { useState } from 'react';

function App() {
  // We use this 'state' variable to store the reply from Python
  const [reply, setReply] = useState("");

  // This is the function I gave you earlier, now inside the Component
  const sendMessage = async () => {
    try {
      console.log("Sending message to backend...");
      
      // 1. Send data to Python Backend (FastAPI running on port 8000)
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: "I am feeling a bit anxious today." }),
      });

      // 2. Get the response from Python
      const data = await response.json();
      console.log("Response from Python:", data);

      // 3. Show the result on the screen
      setReply(data.reply); // This updates the 'reply' state
      
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setReply("Error connecting to backend. Is Python running?");
    }
  };

  // This is the UI (HTML) that React renders
  return (
    <div style={{ padding: "50px", textAlign: "center" }}>
      <h1>Mental Health AI Research</h1>
      
      <p>Click the button below to test the connection to Python.</p>
      
      <button 
        onClick={sendMessage}
        style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}
      >
        Send Test Message
      </button>

      {/* This section displays the reply from Python */}
      <div style={{ marginTop: "20px", color: "blue", fontWeight: "bold" }}>
        {reply && <p>Backend says: {reply}</p>}
      </div>
    </div>
  );
}

export default App;