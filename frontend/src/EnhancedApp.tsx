import React from 'react';
import CardNav from './CardNav';
import './EnhancedApp.css';

const EnhancedApp = () => {
  const items = [
    {
      label: "Athlete's Edge AI",
      bgColor: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      textColor: "#fff",
      links: [
        { label: "Motion Analysis", href: "/motion", ariaLabel: "AI Motion Analysis" },
        { label: "Performance Tracking", href: "/performance", ariaLabel: "Performance Tracking" },
        { label: "Form Correction", href: "/form", ariaLabel: "Exercise Form Correction" }
      ]
    },
    {
      label: "Features", 
      bgColor: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
      textColor: "#fff",
      links: [
        { label: "Real-time Analysis", href: "/realtime", ariaLabel: "Real-time Analysis" },
        { label: "Progress Reports", href: "/reports", ariaLabel: "Progress Reports" },
        { label: "Workout Plans", href: "/plans", ariaLabel: "Workout Plans" }
      ]
    },
    {
      label: "Connect",
      bgColor: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)", 
      textColor: "#fff",
      links: [
        { label: "Join Community", href: "/community", ariaLabel: "Join Community" },
        { label: "Support", href: "/support", ariaLabel: "Get Support" },
        { label: "Feedback", href: "/feedback", ariaLabel: "Send Feedback" }
      ]
    }
  ];

  // Create a simple logo URL or use a placeholder
  const logoSvg = `data:image/svg+xml,${encodeURIComponent(`
    <svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#667eea"/>
          <stop offset="100%" stop-color="#764ba2"/>
        </linearGradient>
      </defs>
      <circle cx="20" cy="20" r="18" fill="url(#logoGrad)"/>
      <path d="M12 20 L18 26 L28 14" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `)}`;

  return (
    <div className="enhanced-app">
      <div className="app-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>
      
      <CardNav
        logo={logoSvg}
        logoAlt="Athlete's Edge AI Logo"
        items={items}
        baseColor="rgba(255, 255, 255, 0.95)"
        menuColor="#333"
        buttonBgColor="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        buttonTextColor="#fff"
        ease="power3.out"
      />
      
      <div className="app-content">
        <div className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">
              <span className="title-gradient">Athlete's Edge AI</span>
              <br />
              Performance Platform
            </h1>
            <p className="hero-subtitle">
              Transform your training with AI-powered motion analysis, 
              real-time feedback, and personalized workout recommendations.
            </p>
            <div className="hero-actions">
              <button className="primary-button">
                <span>Start Training</span>
                <div className="button-glow"></div>
              </button>
              <button className="secondary-button">
                <span>Watch Demo</span>
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="floating-card card-1">
              <div className="card-icon">🏃‍♂️</div>
              <div className="card-text">Motion Analysis</div>
            </div>
            <div className="floating-card card-2">
              <div className="card-icon">📊</div>
              <div className="card-text">Performance Metrics</div>
            </div>
            <div className="floating-card card-3">
              <div className="card-icon">🎯</div>
              <div className="card-text">Form Correction</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedApp;