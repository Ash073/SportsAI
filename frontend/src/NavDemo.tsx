import React, { useState } from 'react';
import CardNav from './CardNav';
import EnhancedApp from './EnhancedApp';
import './NavDemo.css';

const NavDemo = () => {
  const [showEnhanced, setShowEnhanced] = useState(false);

  if (showEnhanced) {
    return (
      <div>
        <button 
          className="demo-toggle"
          onClick={() => setShowEnhanced(false)}
        >
          ← Back to Demo
        </button>
        <EnhancedApp />
      </div>
    );
  }

  const items = [
    {
      label: "About",
      bgColor: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      textColor: "#fff",
      links: [
        { label: "Company", href: "/company", ariaLabel: "About Company" },
        { label: "Careers", href: "/careers", ariaLabel: "About Careers" }
      ]
    },
    {
      label: "Projects", 
      bgColor: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
      textColor: "#fff",
      links: [
        { label: "Featured", href: "/featured", ariaLabel: "Featured Projects" },
        { label: "Case Studies", href: "/case-studies", ariaLabel: "Project Case Studies" }
      ]
    },
    {
      label: "Contact",
      bgColor: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)", 
      textColor: "#fff",
      links: [
        { label: "Email", href: "/email", ariaLabel: "Email us" },
        { label: "Twitter", href: "/twitter", ariaLabel: "Twitter" },
        { label: "LinkedIn", href: "/linkedin", ariaLabel: "LinkedIn" }
      ]
    }
  ];

  // Create a demo logo
  const logoSvg = `data:image/svg+xml,${encodeURIComponent(`
    <svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="demoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#667eea"/>
          <stop offset="100%" stop-color="#764ba2"/>
        </linearGradient>
      </defs>
      <rect width="40" height="40" rx="8" fill="url(#demoGrad)"/>
      <text x="20" y="28" text-anchor="middle" fill="white" font-size="24" font-weight="bold">N</text>
    </svg>
  `)}`;

  return (
    <div className="nav-demo">
      <div className="demo-background">
        <div className="demo-grid"></div>
        <div className="demo-gradient-1"></div>
        <div className="demo-gradient-2"></div>
      </div>
      
      <CardNav
        logo={logoSvg}
        logoAlt="Demo Logo"
        items={items}
        baseColor="rgba(255, 255, 255, 0.95)"
        menuColor="#333"
        buttonBgColor="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        buttonTextColor="#fff"
        ease="power3.out"
      />
      
      <div className="demo-content">
        <div className="demo-hero">
          <h1 className="demo-title">
            Enhanced Navigation
            <span className="demo-subtitle">Beautiful, Modern & Interactive</span>
          </h1>
          
          <div className="demo-features">
            <div className="feature-card">
              <div className="feature-icon">✨</div>
              <h3>Glassmorphism Design</h3>
              <p>Modern glass-like effects with backdrop blur and transparency</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎮</div>
              <h3>Smooth Animations</h3>
              <p>Buttery smooth CSS animations with staggered card reveals</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Fully Responsive</h3>
              <p>Optimized for all device sizes with mobile-first approach</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Gradient Backgrounds</h3>
              <p>Beautiful gradient overlays and hover effects</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Micro-interactions</h3>
              <p>Delightful hover states and button animations</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Accessibility Focus</h3>
              <p>Keyboard navigation and screen reader friendly</p>
            </div>
          </div>
          
          <div className="demo-actions">
            <button 
              className="demo-primary-btn"
              onClick={() => setShowEnhanced(true)}
            >
              View Full Enhanced App
            </button>
            <button className="demo-secondary-btn">
              View Code
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavDemo;