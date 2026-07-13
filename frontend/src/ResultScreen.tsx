import React from 'react';
import { BarChart3Icon, ClockIcon, TargetIcon, ZapIcon, CheckCircleIcon, RotateCcwIcon } from './icons';

interface ResultScreenProps {
  result: any;
  onNavigate: (route: string) => void;
  userId?: number;
  username?: string;
}

export default function ResultScreen({ result, onNavigate, userId, username }: ResultScreenProps) {
  const renderMetricCard = (icon: React.ReactNode, label: string, value: string | number, unit?: string) => (
    <div className="result-item">
      <div className="result-label">
        {icon}
        {label}
      </div>
      <div className="result-value">
        {value}{unit && <span style={{ fontSize: '1rem', color: '#64748b' }}> {unit}</span>}
      </div>
    </div>
  );

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <h2 className="title">Analysis Complete</h2>
          <p className="subtitle">Here are your performance insights</p>
        </div>
        
        {result && (
          <>
            <div className="result-grid">
              {result.pushup_count !== undefined && renderMetricCard(
                <TargetIcon size={16} />,
                'Push-ups Completed',
                result.pushup_count
              )}
              
              {result.duration_sec !== undefined && renderMetricCard(
                <ClockIcon size={16} />,
                'Duration',
                result.duration_sec,
                'seconds'
              )}
              
              {result.avg_speed !== undefined && renderMetricCard(
                <ZapIcon size={16} />,
                'Average Speed',
                result.avg_speed,
                'reps/min'
              )}
              
              {result.form_score !== undefined && renderMetricCard(
                <BarChart3Icon size={16} />,
                'Form Score',
                `${result.form_score}/10`
              )}
            </div>
            
            {result.analysis_notes && result.analysis_notes.length > 0 && (
              <div className="result-notes">
                <div className="result-notes-title">
                  <CheckCircleIcon size={16} />
                  Analysis Notes
                </div>
                <ul className="result-notes-list">
                  {result.analysis_notes.map((note: string, index: number) => (
                    <li key={index}>
                      <CheckCircleIcon size={12} />
                      {note}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {userId && username && (
              <div className="result-notes">
                <div className="result-notes-title">
                  <CheckCircleIcon size={16} />
                  Workout Saved
                </div>
                <p style={{ color: '#166534', margin: '0.5rem 0 0 0' }}>
                  Your workout has been automatically saved to your profile, {username}!
                </p>
              </div>
            )}
          </>
        )}
        
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button 
            className="btn" 
            onClick={() => onNavigate('record')}
          >
            <RotateCcwIcon size={16} />
            Analyze Another Video
          </button>
          
          <button 
            className="btn btn-secondary" 
            onClick={() => onNavigate('landing')}
          >
            <TargetIcon size={16} />
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}