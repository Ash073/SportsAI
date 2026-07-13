import React, { useState } from 'react';
import styles from './WorkoutVideoWidget.module.css';
import { VideoData } from './videoLibrary';

interface Props {
  video: VideoData;
}

const WorkoutVideoWidget: React.FC<Props> = ({ video }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  const handlePlayClick = () => {
    setIsLoaded(true);
  };

  return (
    <div className={styles.widgetContainer}>
      {!isLoaded ? (
        <div 
          className={styles.facade}
          style={{ backgroundImage: `url(https://img.youtube.com/vi/${video.id}/hqdefault.jpg)` }}
          onClick={handlePlayClick}
        >
          <button 
            className={styles.playButtonOverlay}
            onClick={handlePlayClick}
            aria-label={`Play ${video.title}`}
          >
            <svg 
              className={styles.playIcon}
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="currentColor"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </button>
          
          <div className={styles.metadata}>
            <h3 className={styles.title}>{video.title}</h3>
            <p className={styles.channel}>{video.channel}</p>
          </div>
        </div>
      ) : (
        <iframe
          className={styles.iframe}
          src={`https://www.youtube.com/embed/${video.id}?autoplay=1`}
          title={video.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      )}
    </div>
  );
};

export default WorkoutVideoWidget;
