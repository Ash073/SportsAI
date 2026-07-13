import React, { useState, useEffect } from 'react';
import { UserIcon, TargetIcon, TrendingUpIcon, BarChart3Icon, ClockIcon, ZapIcon, StarIcon, CheckCircleIcon, SettingsIcon } from './icons';

interface ProfilePageProps {
  username: string;
  userId: number;
  onNavigate: (route: string) => void;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  total_workouts: number;
  total_pushups: number;
  best_form_score: number;
  avg_form_score: number;
  created_at: string;
}

interface WorkoutStats {
  total_workouts: number;
  total_pushups: number;
  avg_form_score: number;
  best_form_score: number;
  total_time: number;
  avg_workout_time: number;
  days_active: number;
  daily_breakdown: Array<{
    date: string;
    workouts: number;
    pushups: number;
    avg_form: number;
    total_time: number;
  }>;
}

interface Workout {
  id: number;
  exercise_type: string;
  pushup_count: number;
  duration_sec: number;
  form_score: number;
  avg_speed?: number;
  total_distance?: number;
  ai_confidence?: number;
  model_used?: string;
  video_filename?: string;
  analysis_notes?: string;
  created_at: string;
  processing_status: string;
}

function ProfilePage({ username, userId, onNavigate }: ProfilePageProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<WorkoutStats | null>(null);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // MonthLabels component with improved alignment
  const MonthLabels = () => {
    const today = new Date();
    const currentYear = today.getFullYear();
    
    // Calculate the start date (January 1st of current year)
    const startDate = new Date(currentYear, 0, 1);
    const startDayOfWeek = startDate.getDay(); // 0 = Sunday, 6 = Saturday
    
    // Array to store month positions
    const monthPositions: Array<{ month: string; weekIndex: number }> = [];
    
    // Calculate positions for each month
    for (let monthIndex = 0; monthIndex < 12; monthIndex++) {
      const monthStart = new Date(currentYear, monthIndex, 1);
      
      // Skip months that haven't started yet
      if (monthStart > today) continue;
      
      // Calculate the day offset from Jan 1st
      const daysFromStart = (monthStart.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000);
      
      // Adjust for the starting day of week (offset for Jan 1st's position in grid)
      const adjustedDaysFromStart = daysFromStart + startDayOfWeek;
      const weekIndex = Math.floor(adjustedDaysFromStart / 7);
      
      monthPositions.push({
        month: monthStart.toLocaleString('default', { month: 'short' }),
        weekIndex: Math.max(0, weekIndex)
      });
    }
    
    return (
      <div className="month-labels-container-new">
        {monthPositions.map((item, index) => (
          <div
            key={index}
            className="month-label-item"
            style={{ gridColumn: item.weekIndex + 1 }}
          >
            {item.month}
          </div>
        ))}
      </div>
    );
  };

  useEffect(() => {
    fetchProfileData();
  }, [userId]);

  const fetchProfileData = async () => {
    if (!userId) {
      console.error('No user ID available');
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      
      // Fetch profile, stats, and recent workouts
      const [profileRes, statsRes, workoutsRes] = await Promise.all([
        fetch(`https://sports-ai-a2xm.onrender.com/profile/${userId}`),
        fetch(`https://sports-ai-a2xm.onrender.com/stats/${userId}?days=30`),
        fetch(`https://sports-ai-a2xm.onrender.com/workouts/${userId}?limit=10`)
      ]);

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setProfile(profileData);
      } else {
        console.error('Failed to fetch profile:', await profileRes.text());
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData.statistics);
      } else {
        console.error('Failed to fetch stats:', await statsRes.text());
      }

      if (workoutsRes.ok) {
        const workoutsData = await workoutsRes.json();
        setWorkouts(workoutsData.workouts);
      } else {
        console.error('Failed to fetch workouts:', await workoutsRes.text());
      }

    } catch (error) {
      console.error('Error fetching profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-state">
          <div className="loading-spinner large" />
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      {/* Settings Modal */}
      {isSettingsOpen && (
        <div className="settings-modal-overlay" onClick={() => setIsSettingsOpen(false)}>
          <div className="settings-modal" onClick={e => e.stopPropagation()}>
            <div className="settings-header">
              <h2>Settings</h2>
              <button className="close-btn" onClick={() => setIsSettingsOpen(false)}>×</button>
            </div>
            <div className="settings-content">
              <button className="settings-option">Edit Profile</button>
              <button className="settings-option">Notification Preferences</button>
              <button className="settings-option">Privacy & Security</button>
            </div>
            <div className="settings-footer">
              <button className="btn logout-btn" onClick={() => onNavigate('logout')}>Logout</button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="profile-header-new">
        <button className="settings-trigger" onClick={() => setIsSettingsOpen(true)}>
          <SettingsIcon size={24} />
        </button>
        <div className="profile-info-new">
          <div className="avatar-new">
            <UserIcon size={48} />
          </div>
          <h1>{username}</h1>
        </div>
      </header>

      {/* Stats Overview */}
      <section className="stats-overview-new">
        <div className="stats-grid-new">
          <div className="stat-card-new">
            <div className="stat-label">Total Workouts</div>
            <div className="stat-number">{profile?.total_workouts || 0}</div>
          </div>
          <div className="stat-card-new">
            <div className="stat-label">Total Push-ups</div>
            <div className="stat-number">{profile?.total_pushups || 0}</div>
          </div>
          <div className="stat-card-new">
            <div className="stat-label">Best Form Score</div>
            <div className="stat-number">{profile?.best_form_score?.toFixed(1) || '0.0'}</div>
          </div>
          <div className="stat-card-new">
            <div className="stat-label">Average Score</div>
            <div className="stat-number">{profile?.avg_form_score?.toFixed(1) || '0.0'}</div>
          </div>
        </div>
      </section>

      {/* Tabs */}
      <section className="profile-tabs-new">
        <div className="tab-buttons-new">
          <button 
            className={`tab-button-new ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab-button-new ${activeTab === 'workouts' ? 'active' : ''}`}
            onClick={() => setActiveTab('workouts')}
          >
            Recent Workouts
          </button>
          <button 
            className={`tab-button-new ${activeTab === 'progress' ? 'active' : ''}`}
            onClick={() => setActiveTab('progress')}
          >
            Progress
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-tab">
              {stats && (
                <div className="overview-cards">
                  <div className="overview-card">
                    <h3>This Month</h3>
                    <div className="overview-stats">
                      <div className="overview-stat">
                        <span className="number">{stats.total_workouts}</span>
                        <span className="label">Workouts</span>
                      </div>
                      <div className="overview-stat">
                        <span className="number">{stats.total_pushups}</span>
                        <span className="label">Push-ups</span>
                      </div>
                      <div className="overview-stat">
                        <span className="number">{Math.round(stats.total_time / 60)}</span>
                        <span className="label">Minutes</span>
                      </div>
                      <div className="overview-stat">
                        <span className="number">{stats.days_active}</span>
                        <span className="label">Active Days</span>
                      </div>
                    </div>
                  </div>

                  <div className="overview-card">
                    <h3>Performance Metrics</h3>
                    <div className="metrics-list">
                      <div className="metric-item">
                        <span>Average Form Score</span>
                        <span className="metric-value">{stats.avg_form_score.toFixed(1)}/10</span>
                      </div>
                      <div className="metric-item">
                        <span>Best Form Score</span>
                        <span className="metric-value">{stats.best_form_score.toFixed(1)}/10</span>
                      </div>
                      <div className="metric-item">
                        <span>Average Workout Time</span>
                        <span className="metric-value">{formatDuration(stats.avg_workout_time)}</span>
                      </div>
                      <div className="metric-item">
                        <span>Total Training Time</span>
                        <span className="metric-value">{formatDuration(stats.total_time)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'workouts' && (
            <div className="workouts-tab">
              <div className="workouts-header">
                <h3>Recent Workouts</h3>
                <button className="btn" onClick={() => onNavigate('record')}>
                  <TargetIcon size={16} />
                  Start New Workout
                </button>
              </div>
              
              {workouts.length === 0 ? (
                <div className="empty-state">
                  <TargetIcon size={48} />
                  <h3>No workouts yet</h3>
                  <p>Start your first workout to see your progress here!</p>
                  <button className="btn" onClick={() => onNavigate('record')}>
                    <TargetIcon size={16} />
                    Start First Workout
                  </button>
                </div>
              ) : (
                <div className="workouts-list">
                  {workouts.map(workout => (
                    <div key={workout.id} className="workout-card">
                      <div className="workout-header">
                        <div className="workout-type">
                          <TargetIcon size={20} />
                          <span>{workout.exercise_type}</span>
                        </div>
                        <div className="workout-date">
                          {formatDate(workout.created_at)}
                        </div>
                      </div>
                      
                      <div className="workout-stats">
                        <div className="workout-stat">
                          <span className="stat-number">{workout.pushup_count}</span>
                          <span className="stat-label">Push-ups</span>
                        </div>
                        <div className="workout-stat">
                          <span className="stat-number">{workout.form_score.toFixed(1)}</span>
                          <span className="stat-label">Form Score</span>
                        </div>
                        <div className="workout-stat">
                          <span className="stat-number">{formatDuration(workout.duration_sec)}</span>
                          <span className="stat-label">Duration</span>
                        </div>
                        {workout.avg_speed && (
                          <div className="workout-stat">
                            <span className="stat-number">{workout.avg_speed.toFixed(1)}</span>
                            <span className="stat-label">Speed</span>
                          </div>
                        )}
                      </div>

                      {workout.model_used && (
                        <div className="workout-analysis">
                          <span className="analysis-badge">
                            <CheckCircleIcon size={12} />
                            Analyzed by {workout.model_used}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'progress' && (
            <div className="progress-tab">
              <div className="progress-charts">
                <div className="chart-section">
                  <div className="contribution-header">
                    <h3>Workout Activity</h3>
                    <div className="contribution-stats">
                      {stats ? `Workouts since January` : 'Loading...'}
                    </div>
                  </div>
                  <div className="github-heatmap">
                    <div className="heatmap-wrapper">
                      {/* Month labels - grid-based alignment */}
                      <MonthLabels />
                      
                      <div className="heatmap-container">
                        {/* Day labels */}
                        <div className="day-labels">
                          <div className="day-label">Sun</div>
                          <div className="day-label">Mon</div>
                          <div className="day-label">Tue</div>
                          <div className="day-label">Wed</div>
                          <div className="day-label">Thu</div>
                          <div className="day-label">Fri</div>
                          <div className="day-label">Sat</div>
                        </div>
                        
                        {/* Heatmap grid */}
                        <div className="contribution-grid">
                          {Array.from({ length: 52 }, (_, weekIndex) => {
                            // Start from January 1st of current year
                            const today = new Date();
                            const startDate = new Date(today.getFullYear(), 0, 1); // January 1st
                            const startDayOfWeek = startDate.getDay(); // Get the day of week for Jan 1st (0=Sunday, 1=Monday, etc.)
                            
                            return (
                              <div key={weekIndex} className="week-column">
                                {Array.from({ length: 7 }, (_, dayIndex) => {
                                  // Calculate the exact date for this cell
                                  const daysFromStart = (weekIndex * 7) + dayIndex - startDayOfWeek;
                                  const cellDate = new Date(startDate);
                                  cellDate.setDate(startDate.getDate() + daysFromStart);
                                  
                                  // Only show dates up to today and dates that are valid (not before Jan 1st)
                                  if (cellDate > today || daysFromStart < 0) {
                                    return (
                                      <div
                                        key={dayIndex}
                                        className="contribution-day level-0"
                                        style={{ opacity: 0.3 }}
                                      />
                                    );
                                  }
                                  
                                  const year = cellDate.getFullYear();
                                  const month = String(cellDate.getMonth() + 1).padStart(2, '0');
                                  const day = String(cellDate.getDate()).padStart(2, '0');
                                  const dateStr = `${year}-${month}-${day}`;
                                  const dayData = stats?.daily_breakdown?.find(d => d.date === dateStr);
                                  const workoutCount = dayData?.workouts || 0;
                                  
                                  // GitHub-style intensity levels (0-4)
                                  let level = 0;
                                  if (workoutCount >= 1) level = 1;
                                  if (workoutCount >= 2) level = 2;
                                  if (workoutCount >= 3) level = 3;
                                  if (workoutCount >= 4) level = 4;
                                  
                                  // Get the actual day of week for proper alignment
                                  const dayOfWeek = cellDate.getDay(); // 0 = Sunday, 1 = Monday, etc.
                                  
                                  return (
                                    <div
                                      key={dayIndex}
                                      className={`contribution-day level-${level} day-${dayOfWeek}`}
                                      data-date={dateStr}
                                      data-count={workoutCount}
                                      data-day-of-week={dayOfWeek}
                                      title={`${workoutCount} workouts on ${cellDate.toLocaleDateString('en-US', { 
                                        weekday: 'long', 
                                        year: 'numeric', 
                                        month: 'long', 
                                        day: 'numeric' 
                                      })}${dayData ? `\nPush-ups: ${dayData.pushups || 0}\nAvg form: ${dayData.avg_form?.toFixed(1) || 'N/A'}` : ''}`}
                                    />
                                  );
                                })}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                    
                    {/* Legend */}
                    <div className="contribution-legend">
                      <span className="legend-text">Less</span>
                      <div className="legend-squares">
                        <div className="legend-square level-0"></div>
                        <div className="legend-square level-1"></div>
                        <div className="legend-square level-2"></div>
                        <div className="legend-square level-3"></div>
                        <div className="legend-square level-4"></div>
                      </div>
                      <span className="legend-text">More</span>
                    </div>
                  </div>
                </div>

                <div className="chart-section">
                  <h3>Form Score Progress</h3>
                  <div className="form-progress-chart-large">
                    {stats?.daily_breakdown && stats.daily_breakdown.length > 0 ? (
                      <div className="line-chart-large">
                        <svg width="100%" height="400" viewBox="0 0 600 400">
                          <defs>
                            <linearGradient id="formGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="rgba(16, 185, 129, 0.3)" />
                              <stop offset="100%" stopColor="rgba(16, 185, 129, 0.1)" />
                            </linearGradient>
                          </defs>
                          
                          {/* Grid lines */}
                          {[0, 2, 4, 6, 8, 10].map(score => (
                            <line
                              key={score}
                              x1="60"
                              y1={360 - (score * 30)}
                              x2="540"
                              y2={360 - (score * 30)}
                              stroke="var(--border-primary)"
                              strokeWidth="1"
                              opacity="0.3"
                            />
                          ))}
                          
                          {/* Y-axis labels */}
                          {[0, 2, 4, 6, 8, 10].map(score => (
                            <text
                              key={score}
                              x="45"
                              y={365 - (score * 30)}
                              fontSize="12"
                              fill="var(--text-secondary)"
                              textAnchor="end"
                            >
                              {score}
                            </text>
                          ))}
                          
                          {/* Data visualization */}
                          {(() => {
                            // Filter and sort data with valid form scores
                            const validData = stats.daily_breakdown
                              .filter(d => d.avg_form > 0 && d.workouts > 0)
                              .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                              .slice(-30); // Show last 30 data points for better visibility
                            
                            if (validData.length < 2) {
                              return (
                                <text
                                  x="300"
                                  y="200"
                                  fontSize="14"
                                  fill="var(--text-muted)"
                                  textAnchor="middle"
                                >
                                  Need at least 2 workouts to show progress
                                </text>
                              );
                            }
                            
                            const chartWidth = 480; // 540 - 60
                            const stepX = chartWidth / (validData.length - 1);
                            
                            return (
                              <>
                                {/* Area fill */}
                                <path
                                  d={`M 60 360 ` +
                                     validData.map((d, i) => 
                                       `L ${60 + (i * stepX)} ${360 - (d.avg_form * 30)}`
                                     ).join(' ') + ` L ${60 + ((validData.length - 1) * stepX)} 360 Z`}
                                  fill="url(#formGradient)"
                                />
                                
                                {/* Main line */}
                                <path
                                  d={validData.map((d, i) => 
                                    `${i === 0 ? 'M' : 'L'} ${60 + (i * stepX)} ${360 - (d.avg_form * 30)}`
                                  ).join(' ')}
                                  fill="none"
                                  stroke="var(--accent-primary)"
                                  strokeWidth="3"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                />
                                
                                {/* Data points with hover */}
                                {validData.map((d, i) => {
                                  const x = 60 + (i * stepX);
                                  const y = 360 - (d.avg_form * 30);
                                  return (
                                    <g key={i}>
                                      {/* Larger invisible circle for easier hover */}
                                      <circle
                                        cx={x}
                                        cy={y}
                                        r="15"
                                        fill="transparent"
                                        className="chart-hover-area"
                                        style={{ cursor: 'pointer' }}
                                      >
                                        <title>
                                          {`Date: ${new Date(d.date).toLocaleDateString('en-US', {
                                            month: 'short',
                                            day: 'numeric',
                                            year: 'numeric'
                                          })}\nForm Score: ${d.avg_form.toFixed(1)}/10\nWorkouts: ${d.workouts}\nPush-ups: ${d.pushups || 0}`}
                                        </title>
                                      </circle>
                                      {/* Visible data point */}
                                      <circle
                                        cx={x}
                                        cy={y}
                                        r="4"
                                        fill="var(--accent-primary)"
                                        stroke="var(--bg-card)"
                                        strokeWidth="2"
                                        className="chart-data-point"
                                      />
                                    </g>
                                  );
                                })}
                                
                                {/* X-axis date labels */}
                                {validData.map((d, i) => {
                                  // Only show every 5th label to avoid crowding
                                  if (i % Math.ceil(validData.length / 6) !== 0) return null;
                                  
                                  const x = 60 + (i * stepX);
                                  return (
                                    <text
                                      key={i}
                                      x={x}
                                      y="385"
                                      fontSize="10"
                                      fill="var(--text-muted)"
                                      textAnchor="middle"
                                    >
                                      {new Date(d.date).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric'
                                      })}
                                    </text>
                                  );
                                })}
                              </>
                            );
                          })()}
                          
                          {/* Y-axis title */}
                          <text
                            x="20"
                            y="200"
                            fontSize="12"
                            fill="var(--text-secondary)"
                            textAnchor="middle"
                            transform="rotate(-90, 20, 200)"
                          >
                            Form Score
                          </text>
                          
                          {/* X-axis title */}
                          <text
                            x="300"
                            y="395"
                            fontSize="12"
                            fill="var(--text-secondary)"
                            textAnchor="middle"
                          >
                            Progress Timeline
                          </text>
                        </svg>
                        <div className="chart-legend">
                          <span>Hover over data points to see detailed progress information</span>
                        </div>
                      </div>
                    ) : (
                      <div className="chart-placeholder">
                        <TrendingUpIcon size={48} />
                        <p>Complete more workouts to see your form progress!</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default ProfilePage;