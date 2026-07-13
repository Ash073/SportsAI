import React from 'react';
import { TargetIcon, TrendingUpIcon, StarIcon, ShieldIcon, ZapIcon, BarChart3Icon } from './icons';

interface LandingPageProps {
  username: string;
  onGetStarted: () => void;
  onNavigate: (route: string) => void;
  isAuthenticated: boolean;
}

function LandingPage({ username, onGetStarted, onNavigate, isAuthenticated }: LandingPageProps) {
  return (
    <div className="landing-container">
      {/* Header */}
      <header className="landing-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🏃‍♂️</span>
            <span className="logo-text">Athlete's Edge AI</span>
          </div>
          <div className="header-actions">
            {isAuthenticated ? (
              <div className="user-welcome">
                Welcome back, <strong>{username}</strong>!
                <button className="logout-btn" onClick={() => onNavigate('logout')}>Logout</button>
                <button className="profile-btn" onClick={() => onNavigate('profile')}>Profile</button>
              </div>
            ) : (
              <div className="auth-buttons">
                <button className="auth-btn" onClick={() => onNavigate('login')}>Sign In</button>
                <button className="auth-btn signup-btn" onClick={() => onNavigate('signup')}>Sign Up</button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Transform Your <span className="highlight">Athletic Performance</span> with AI
          </h1>
          <p className="hero-subtitle">
            Advanced computer vision and machine learning technology to analyze your exercise form, 
            count repetitions, and provide personalized feedback for optimal training results.
          </p>
          <button className="cta-button" onClick={onGetStarted}>
            <ZapIcon size={20} />
            {isAuthenticated ? 'Start Analyzing Now' : 'Get Started Free'}
          </button>
        </div>
        <div className="hero-visual">
          <div className="demo-video-placeholder">
            <div className="play-button">
              <span>▶</span>
            </div>
            <div className="demo-overlay">
              <div className="demo-stats">
                <div className="stat">
                  <span className="stat-number">15</span>
                  <span className="stat-label">Push-ups</span>
                </div>
                <div className="stat">
                  <span className="stat-number">8.7</span>
                  <span className="stat-label">Form Score</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>Why Choose Athlete's Edge AI?</h2>
          <p>Professional-grade analysis powered by cutting-edge technology</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <TargetIcon size={32} />
            </div>
            <h3>Precision Analysis</h3>
            <p>
              Our AI uses advanced pose detection to track body landmarks in real-time, 
              providing accurate form analysis and rep counting.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <TrendingUpIcon size={32} />
            </div>
            <h3>Performance Tracking</h3>
            <p>
              Monitor your progress over time with detailed metrics including form scores, 
              rep counts, workout duration, and personalized improvement recommendations.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <StarIcon size={32} />
            </div>
            <h3>Personalized Feedback</h3>
            <p>
              Get specific, actionable feedback on your exercise form. Our AI identifies 
              areas for improvement and provides targeted suggestions for better results.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <ShieldIcon size={32} />
            </div>
            <h3>Injury Prevention</h3>
            <p>
              Maintain proper form to reduce injury risk. Our system alerts you to 
              form deviations that could lead to strain or injury.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <ZapIcon size={32} />
            </div>
            <h3>Real-time Analysis</h3>
            <p>
              Upload your workout video and get instant analysis. No waiting, no complex setup - 
              just immediate, actionable insights for your training.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <BarChart3Icon size={32} />
            </div>
            <h3>Data-Driven Insights</h3>
            <p>
              Make informed decisions about your training with comprehensive analytics, 
              progress charts, and performance trends over time.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Simple, fast, and scientifically accurate</p>
        </div>
        
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Upload Your Video</h3>
            <p>Simply upload a video of your exercise routine. Our system supports all common video formats.</p>
          </div>
          
          <div className="step-arrow">→</div>
          
          <div className="step">
            <div className="step-number">2</div>
            <h3>AI Analysis</h3>
            <p>Our advanced AI analyzes your movement patterns, counts reps, and evaluates form quality.</p>
          </div>
          
          <div className="step-arrow">→</div>
          
          <div className="step">
            <div className="step-number">3</div>
            <h3>Get Results</h3>
            <p>Receive detailed feedback, performance metrics, and personalized recommendations for improvement.</p>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="technology-section">
        <div className="tech-content">
          <div className="tech-text">
            <h2>Powered by Advanced AI</h2>
            <p>
              Athlete's Edge AI leverages state-of-the-art computer vision and machine learning technologies:
            </p>
            <ul className="tech-list">
              <li><strong>MediaPipe Pose Detection:</strong> Real-time body landmark tracking</li>
              <li><strong>Random Forest Classification:</strong> Intelligent form quality assessment</li>
              <li><strong>Motion Pattern Analysis:</strong> Accurate repetition counting</li>
              <li><strong>Biomechanics Evaluation:</strong> Joint angle and movement analysis</li>
            </ul>
          </div>
          <div className="tech-stats">
            <div className="stat-card">
              <div className="stat-number">Real-time</div>
              <div className="stat-label">Analysis</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">Fast</div>
              <div className="stat-label">Processing</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">33</div>
              <div className="stat-label">Body Points</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="final-cta-section">
        <div className="cta-content">
          <h2>Ready to Optimize Your Training?</h2>
          <p>Join thousands of athletes who trust Athlete's Edge AI for their performance analysis</p>
          <button className="cta-button large" onClick={onGetStarted}>
            <ZapIcon size={24} />
            {isAuthenticated ? 'Start Your Analysis' : 'Join Athlete\'s Edge AI Today'}
          </button>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;