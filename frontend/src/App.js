import { useState, useEffect } from 'react';
import ChatUI from './components/ChatUI';
import Login from './components/Login';
import { supabase } from './config/supabase';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  if (loading) {
    return <div className="App">Loading...</div>;
  }

  return (
    <div className="App">
      {user ? (
        <div>
          <div style={{ padding: '1rem', background: '#f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Logged in as: {user.email}</span>
            <button onClick={handleLogout} style={{ padding: '0.5rem 1rem', cursor: 'pointer' }}>
              Logout
            </button>
          </div>
          <ChatUI userId={user.id} />
        </div>
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;