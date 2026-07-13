import React, { useEffect, useState } from 'react';
import { UploadIcon, VideoIcon, ZapIcon } from './icons';
import { videoLibrary, VideoData } from './videoLibrary';
import WorkoutVideoWidget from './WorkoutVideoWidget';

interface HomePageProps {
  onNavigate: (route: string, data?: any) => void;
  username: string;
  userId?: number;
}

interface LatestWorkout {
  pushup_count: number;
  form_score: number;
}

function HomePage({ onNavigate, username, userId }: HomePageProps) {
  const [latestWorkout, setLatestWorkout] = useState<LatestWorkout | null>(null);
  const [heroVideo, setHeroVideo] = useState<VideoData | null>(null);

  useEffect(() => {
    // 1. Fetch latest workout if logged in
    const fetchLatest = async () => {
      if (userId) {
        try {
          const res = await fetch(`http://localhost:8004/workouts/${userId}?limit=1`);
          if (res.ok) {
            const data = await res.json();
            if (data.workouts && data.workouts.length > 0) {
              setLatestWorkout({
                pushup_count: data.workouts[0].pushup_count,
                form_score: data.workouts[0].form_score
              });
              // We have a workout, but we still want a hero video in the background
            }
          }
        } catch (e) {
          console.error("Failed to fetch latest workout", e);
        }
      }
      
      // 2. If no workout found, pick a random hero video
      const lastId = sessionStorage.getItem('lastShownWorkoutVideoId');
      const available = videoLibrary.filter(v => v.id !== lastId);
      
      // Fallback to full library if somehow available is empty
      const pool = available.length > 0 ? available : videoLibrary;
      const randomVid = pool[Math.floor(Math.random() * pool.length)];
      
      setHeroVideo(randomVid);
      sessionStorage.setItem('lastShownWorkoutVideoId', randomVid.id);
    };

    fetchLatest();
  }, [userId]);

  return (
    <div className="home-container">
      <header className="home-header">
        <div className="home-header-content">
          <div className="logo">
            <span className="logo-icon">🏃‍♂️</span>
            <span className="logo-text">Athlete's Edge AI</span>
          </div>
          <div className="welcome">
            <span className="welcome-text">Welcome, <strong>{username}</strong></span>
            <button className="logout-btn" onClick={() => onNavigate('logout')}>Logout</button>
            <button className="profile-btn" onClick={() => onNavigate('profile')}>Profile</button>
          </div>
        </div>
      </header>

      <section className="analysis-section">
        <div className="analysis-card">
          <div className="analysis-text">
            <h1>Analyze Your Workout</h1>
            <p>
              Upload a video and get instant AI-powered feedback on form, rep count, and performance.
            </p>
            <div className="analysis-actions">
              <button className="cta-button" onClick={() => onNavigate('record')}>
                <UploadIcon size={18} />
                Upload & Analyze
              </button>
              <button className="cta-button secondary" onClick={() => onNavigate('record')}>
                <VideoIcon size={18} />
                Record New Session
              </button>
            </div>
          </div>
          <div className="analysis-visual">
            {heroVideo ? (
              <div style={{ position: 'relative', width: '100%', height: '100%' }}>
                <WorkoutVideoWidget video={heroVideo} />
                {latestWorkout && (
                  <div className="demo-overlay">
                    <div className="demo-stats">
                      <div className="stat">
                        <span className="stat-number">{latestWorkout.pushup_count}</span>
                        <span className="stat-label">Latest Reps</span>
                      </div>
                      <div className="stat">
                        <span className="stat-number">{latestWorkout.form_score.toFixed(1)}</span>
                        <span className="stat-label">Form Score</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
               <div className="demo-video-placeholder">
                 <div className="loading-spinner" />
               </div>
            )}
          </div>
        </div>
      </section>

      <section className="tutorials-section">
        <div className="section-header">
          <h2>Exercise Tutorials</h2>
          <p>Learn correct form with these short guides</p>
        </div>
        <div className="tutorials-grid">
          {videoLibrary.map(t => (
            <div key={t.id} className="tutorial-card">
              <WorkoutVideoWidget video={t} />
            </div>
          ))}
        </div>
      </section>

      <section className="cta-bottom">
        <button className="cta-button large" onClick={() => onNavigate('record')}>
          <ZapIcon size={22} />
          Start Analysis
        </button>
      </section>
    </div>
  );
}

export default HomePage;
