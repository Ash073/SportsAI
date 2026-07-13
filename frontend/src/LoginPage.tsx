import React, { useState } from 'react';
import { UserIcon, LockIcon, EyeIcon, EyeOffIcon } from './icons';

interface LoginPageProps {
  onLogin: (username: string, userId: number) => void;
  onNavigate: (route: string) => void;
}

function LoginPage({ onLogin, onNavigate }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      alert('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    
    try {
      // Make actual API call to login
      const response = await fetch('http://localhost:8004/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password
        }),
      });
      
      if (response.ok) {
        const userData = await response.json();
        // Persist token and user info for session continuity
        try {
          localStorage.setItem('ae_token', userData.access_token);
          localStorage.setItem('ae_user', JSON.stringify({
            userId: userData.user_id,
            username: userData.username
          }));
        } catch {}
        setIsLoading(false);
        onLogin(username.trim(), userData.user_id);
      } else {
        const errorData = await response.json();
        setIsLoading(false);
        alert(errorData.detail || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      setIsLoading(false);
      console.error('Login error:', error);
      alert('Network error. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            <div className="logo-icon">🏃‍♂️</div>
            <h1>Athlete's Edge AI</h1>
          </div>
          <p className="login-subtitle">Advanced Motion Analysis Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              <UserIcon size={16} />
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="form-input"
              placeholder="Enter your username"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              <LockIcon size={16} />
              Password
            </label>
            <div className="password-input-container">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="Enter your password"
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? <EyeOffIcon size={16} /> : <EyeIcon size={16} />}
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="loading-spinner" />
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="login-footer">
          <div className="auth-links">
            <p>Don't have an account?</p>
            <button 
              type="button" 
              className="link-button"
              onClick={() => onNavigate('signup')}
            >
              Create Account
            </button>
          </div>
          
          <button 
            type="button" 
            className="back-to-landing"
            onClick={() => onNavigate('landing')}
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;