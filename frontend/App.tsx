import React, { useEffect, useState } from 'react';
import LoginPage from './src/LoginPage';
import SignupPage from './src/SignupPage';
import LandingPage from './src/LandingPage';
import ProfilePage from './src/ProfilePage';
import RecordScreen from './src/RecordScreen';
import ResultScreen from './src/ResultScreen';
import HomePage from './src/HomePage';

function App() {
  const [currentScreen, setCurrentScreen] = useState('landing');
  const [resultData, setResultData] = useState(null);
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState<number | null>(null); // Fixed: Initialize as null, not 1
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = async (user: string, userIdFromLogin: number) => {
    setUsername(user);
    setUserId(userIdFromLogin);
    setIsAuthenticated(true);
    setCurrentScreen('home');
  };

  const handleSignup = async (user: string, userIdFromSignup: number) => {
    setUsername(user);
    setUserId(userIdFromSignup);
    setIsAuthenticated(true);
    setCurrentScreen('home');
  };

  const handleGetStarted = () => {
    if (isAuthenticated) {
      setCurrentScreen('home');
    } else {
      setCurrentScreen('login');
    }
  };

  const handleNavigate = (route: string, data?: any) => {
    if (route === 'result' && data) {
      setResultData(data.result);
      setCurrentScreen('result');
    } else if (route === 'record') {
      if (isAuthenticated) {
        setCurrentScreen('record');
        setResultData(null);
      } else {
        setCurrentScreen('login');
      }
    } else if (route === 'home') {
      if (isAuthenticated) {
        setCurrentScreen('home');
      } else {
        setCurrentScreen('login');
      }
    } else if (route === 'landing') {
      setCurrentScreen(isAuthenticated ? 'home' : 'landing');
    } else if (route === 'login') {
      setCurrentScreen('login');
    } else if (route === 'signup') {
      setCurrentScreen('signup');
    } else if (route === 'profile') {
      if (isAuthenticated) {
        setCurrentScreen('profile');
      } else {
        setCurrentScreen('login');
      }
    } else if (route === 'logout') {
      setCurrentScreen('landing');
      setUsername('');
      setUserId(null);
      setIsAuthenticated(false);
    }
  };

  // Rehydrate auth from localStorage on first load
  useEffect(() => {
    try {
      const token = localStorage.getItem('ae_token');
      const userRaw = localStorage.getItem('ae_user');
      if (token && userRaw) {
        const parsed = JSON.parse(userRaw);
        if (parsed?.userId && parsed?.username) {
          setUsername(parsed.username);
          setUserId(parsed.userId);
          setIsAuthenticated(true);
          setCurrentScreen((prev) => (prev === 'landing' ? 'home' : prev));
        }
      }
    } catch {}
  }, []);

  return (
    <div className="App">
      {currentScreen === 'landing' && (
        <LandingPage username={username} onGetStarted={handleGetStarted} onNavigate={handleNavigate} isAuthenticated={isAuthenticated} />
      )}
      {currentScreen === 'home' && (
        <HomePage onNavigate={handleNavigate} username={username} userId={userId || undefined} />
      )}
      {currentScreen === 'login' && (
        <LoginPage onLogin={handleLogin} onNavigate={handleNavigate} />
      )}
      {currentScreen === 'signup' && (
        <SignupPage onSignup={handleSignup} onNavigate={handleNavigate} />
      )}
      {currentScreen === 'profile' && userId && (
        <ProfilePage username={username} userId={userId} onNavigate={handleNavigate} />
      )}
      {currentScreen === 'record' && (
        <RecordScreen onNavigate={handleNavigate} userId={userId || undefined} isAuthenticated={isAuthenticated} />
      )}
      {currentScreen === 'result' && (
        <ResultScreen result={resultData} onNavigate={handleNavigate} userId={userId || undefined} username={username} />
      )}
    </div>
  );
}

export default App;