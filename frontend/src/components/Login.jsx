import { useState } from 'react';
import { supabase } from '../config/supabase';
import './Login.css';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.REACT_APP_API_URL || '/api';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let response;
      if (isRegistering) {
        // Register
        response = await fetch(`${API_URL}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
      } else {
        // Login
        response = await fetch(`${API_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      // For registration, try to sign in immediately
      // For login, the backend already authenticated, so sign in with Supabase client
      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) {
        // If email confirmation is required, show helpful message
        const errorMsg = authError.message || '';
        if (errorMsg.includes('Email not confirmed') || 
            errorMsg.includes('email_not_confirmed') || 
            errorMsg.includes('not confirmed') ||
            errorMsg.includes('Invalid login credentials')) {
          throw new Error('Email confirmation required. Go to Supabase Dashboard → Authentication → Providers → Email → Uncheck "Confirm email" to disable. Or check your email for confirmation link.');
        }
        throw authError;
      }

      if (authData?.user) {
        onLogin(authData.user);
      } else {
        throw new Error('Login failed - no user data received');
      }
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>{isRegistering ? 'Register' : 'Login'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              minLength={6}
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Loading...' : (isRegistering ? 'Register' : 'Login')}
          </button>
        </form>
        <button
          type="button"
          onClick={() => setIsRegistering(!isRegistering)}
          className="toggle-button"
        >
          {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
        </button>
      </div>
    </div>
  );
}