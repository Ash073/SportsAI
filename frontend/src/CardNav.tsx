import React, { useLayoutEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
// Using lucide-react icons which are available in the project
import { ArrowUpRight } from 'lucide-react';
import './CardNav.css';

type CardNavLink = {
  label: string;
  href: string;
  ariaLabel: string;
};

export type CardNavItem = {
  label: string;
  bgColor: string;
  textColor: string;
  links: CardNavLink[];
};

export interface CardNavProps {
  logo: string;
  logoAlt?: string;
  items: CardNavItem[];
  className?: string;
  ease?: string;
  baseColor?: string;
  menuColor?: string;
  buttonBgColor?: string;
  buttonTextColor?: string;
}

const CardNav: React.FC<CardNavProps> = ({
  logo,
  logoAlt = 'Logo',
  items,
  className = '',
  ease = 'power3.out',
  baseColor = '#fff',
  menuColor,
  buttonBgColor,
  buttonTextColor
}) => {
  const [isHamburgerOpen, setIsHamburgerOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);
  const navRef = useRef<HTMLDivElement | null>(null);
  const cardsRef = useRef<HTMLDivElement[]>([]);
  const tlRef = useRef<gsap.core.Timeline | null>(null);
  const backgroundRef = useRef<HTMLDivElement | null>(null);

  const calculateHeight = () => {
    const navEl = navRef.current;
    if (!navEl) return 280;

    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    if (isMobile) {
      const contentEl = navEl.querySelector('.card-nav-content') as HTMLElement;
      if (contentEl) {
        const wasVisible = contentEl.style.visibility;
        const wasPointerEvents = contentEl.style.pointerEvents;
        const wasPosition = contentEl.style.position;
        const wasHeight = contentEl.style.height;

        contentEl.style.visibility = 'visible';
        contentEl.style.pointerEvents = 'auto';
        contentEl.style.position = 'static';
        contentEl.style.height = 'auto';

        contentEl.offsetHeight;

        const topBar = 70;
        const padding = 20;
        const contentHeight = contentEl.scrollHeight;

        contentEl.style.visibility = wasVisible;
        contentEl.style.pointerEvents = wasPointerEvents;
        contentEl.style.position = wasPosition;
        contentEl.style.height = wasHeight;

        return topBar + contentHeight + padding;
      }
    }
    return 280;
  };

  const createTimeline = () => {
    const navEl = navRef.current;
    if (!navEl) return null;

    // Set initial states
    gsap.set(navEl, { height: 70, overflow: 'hidden' });
    gsap.set(cardsRef.current, { y: 60, opacity: 0, scale: 0.9, rotationX: -15 });
    gsap.set(backgroundRef.current, { opacity: 0, scale: 0.95 });

    const tl = gsap.timeline({ paused: true });

    // Animate container height with elastic ease
    tl.to(navEl, {
      height: calculateHeight,
      duration: 0.6,
      ease: 'power3.out'
    });

    // Animate background glow
    tl.to(backgroundRef.current, {
      opacity: 1,
      scale: 1,
      duration: 0.4,
      ease: 'back.out(1.2)'
    }, '-=0.3');

    // Animate cards with stagger and 3D transforms
    tl.to(cardsRef.current, {
      y: 0,
      opacity: 1,
      scale: 1,
      rotationX: 0,
      duration: 0.5,
      ease: 'back.out(1.4)',
      stagger: {
        amount: 0.2,
        from: 'start'
      }
    }, '-=0.2');

    // Add subtle bounce to cards
    tl.to(cardsRef.current, {
      y: -5,
      duration: 0.15,
      ease: 'power2.out',
      stagger: 0.05
    }, '-=0.1')
    .to(cardsRef.current, {
      y: 0,
      duration: 0.2,
      ease: 'bounce.out',
      stagger: 0.05
    });

    return tl;
  };

  useLayoutEffect(() => {
    const tl = createTimeline();
    tlRef.current = tl;

    // Set up hover animations for cards
    cardsRef.current.forEach((card, index) => {
      if (card) {
        const onEnter = () => {
          gsap.to(card, {
            y: -8,
            scale: 1.03,
            rotationY: 5,
            duration: 0.3,
            ease: 'power2.out'
          });
          
          // Animate card overlay
          const overlay = card.querySelector('.nav-card-overlay');
          gsap.to(overlay, {
            opacity: 1,
            duration: 0.3,
            ease: 'power2.out'
          });
        };

        const onLeave = () => {
          gsap.to(card, {
            y: 0,
            scale: 1,
            rotationY: 0,
            duration: 0.3,
            ease: 'power2.out'
          });
          
          // Reset card overlay
          const overlay = card.querySelector('.nav-card-overlay');
          gsap.to(overlay, {
            opacity: 0,
            duration: 0.3,
            ease: 'power2.out'
          });
        };

        card.addEventListener('mouseenter', onEnter);
        card.addEventListener('mouseleave', onLeave);
      }
    });

    // Add entrance animation for logo
    const logoWrapper = document.querySelector('.logo-wrapper');
    if (logoWrapper) {
      gsap.set(logoWrapper, { scale: 0, rotation: -180 });
      gsap.to(logoWrapper, {
        scale: 1,
        rotation: 0,
        duration: 0.8,
        ease: 'back.out(1.7)',
        delay: 0.2
      });
    }

    // Add button entrance animation
    const ctaButton = document.querySelector('.card-nav-cta-button');
    if (ctaButton) {
      gsap.set(ctaButton, { scale: 0, opacity: 0 });
      gsap.to(ctaButton, {
        scale: 1,
        opacity: 1,
        duration: 0.5,
        ease: 'back.out(1.4)',
        delay: 0.4
      });
    }

    return () => {
      tl?.kill();
      tlRef.current = null;
    };
  }, [ease, items]);

  useLayoutEffect(() => {
    const handleResize = () => {
      if (!tlRef.current) return;

      if (isExpanded) {
        const newHeight = calculateHeight();
        gsap.set(navRef.current, { height: newHeight });

        tlRef.current.kill();
        const newTl = createTimeline();
        if (newTl) {
          newTl.progress(1);
          tlRef.current = newTl;
        }
      } else {
        tlRef.current.kill();
        const newTl = createTimeline();
        if (newTl) {
          tlRef.current = newTl;
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isExpanded]);

  const toggleMenu = () => {
    const tl = tlRef.current;
    if (!tl) return;
    
    if (!isExpanded) {
      setIsHamburgerOpen(true);
      setIsExpanded(true);
      tl.play();
      
      // Add entrance animation for hamburger lines
      const lines = document.querySelectorAll('.hamburger-line');
      gsap.to(lines, {
        scale: 1.1,
        duration: 0.1,
        ease: 'power2.out',
        yoyo: true,
        repeat: 1
      });
    } else {
      setIsHamburgerOpen(false);
      tl.eventCallback('onReverseComplete', () => setIsExpanded(false));
      tl.reverse();
    }
  };

  const setCardRef = (i: number) => (el: HTMLDivElement | null) => {
    if (el) cardsRef.current[i] = el;
  };

  const handleCardHover = (index: number) => {
    setHoveredCard(index);
    
    // Animate card links on hover
    const card = cardsRef.current[index];
    if (card) {
      const links = card.querySelectorAll('.nav-card-link');
      gsap.to(links, {
        x: 8,
        duration: 0.3,
        ease: 'power2.out',
        stagger: 0.05
      });
      
      // Animate the underline
      const underline = card.querySelector('.nav-card-label-underline');
      gsap.to(underline, {
        width: '100%',
        duration: 0.4,
        ease: 'power2.out'
      });
      
      // Animate link icons
      const icons = card.querySelectorAll('.nav-card-link-icon');
      gsap.to(icons, {
        x: 4,
        y: -4,
        scale: 1.1,
        rotation: 15,
        duration: 0.3,
        ease: 'back.out(1.4)',
        stagger: 0.05
      });
    }
  };

  const handleCardLeave = (index: number) => {
    setHoveredCard(null);
    
    // Reset card links animation
    const card = cardsRef.current[index];
    if (card) {
      const links = card.querySelectorAll('.nav-card-link');
      gsap.to(links, {
        x: 0,
        duration: 0.3,
        ease: 'power2.out',
        stagger: 0.05
      });
      
      // Reset the underline
      const underline = card.querySelector('.nav-card-label-underline');
      gsap.to(underline, {
        width: 0,
        duration: 0.3,
        ease: 'power2.out'
      });
      
      // Reset link icons
      const icons = card.querySelectorAll('.nav-card-link-icon');
      gsap.to(icons, {
        x: 0,
        y: 0,
        scale: 1,
        rotation: 0,
        duration: 0.3,
        ease: 'power2.out',
        stagger: 0.05
      });
    }
  };

  return (
    <div className={`card-nav-container ${className}`}>
      <div className="card-nav-background" ref={backgroundRef}></div>
      <nav 
        ref={navRef} 
        className={`card-nav ${isExpanded ? 'open' : ''}`} 
        style={{ backgroundColor: baseColor }}
      >
        <div className="card-nav-glow"></div>
        
        <div className="card-nav-top">
          <div
            className={`hamburger-menu ${isHamburgerOpen ? 'open' : ''}`}
            onClick={toggleMenu}
            role="button"
            aria-label={isExpanded ? 'Close menu' : 'Open menu'}
            tabIndex={0}
            style={{ color: menuColor || '#000' }}
          >
            <div className="hamburger-line" />
            <div className="hamburger-line" />
            <div className="hamburger-line" />
          </div>

          <div className="logo-container">
            <div className="logo-wrapper">
              <img src={logo} alt={logoAlt} className="logo" />
            </div>
          </div>

          <button
            type="button"
            className="card-nav-cta-button"
            style={{ backgroundColor: buttonBgColor, color: buttonTextColor }}
            onMouseEnter={() => {
              gsap.to('.card-nav-cta-button', {
                scale: 1.05,
                y: -2,
                duration: 0.3,
                ease: 'power2.out'
              });
              
              // Animate button shine
              gsap.to('.button-shine', {
                x: '200%',
                duration: 0.6,
                ease: 'power2.out'
              });
            }}
            onMouseLeave={() => {
              gsap.to('.card-nav-cta-button', {
                scale: 1,
                y: 0,
                duration: 0.3,
                ease: 'power2.out'
              });
              
              // Reset button shine
              gsap.set('.button-shine', { x: '-100%' });
            }}
          >
            <span>Get Started</span>
            <div className="button-shine"></div>
            <div className="button-shine"></div>
          </button>
        </div>

        <div className="card-nav-content" aria-hidden={!isExpanded}>
          {(items || []).slice(0, 3).map((item, idx) => (
            <div
              key={`${item.label}-${idx}`}
              className={`nav-card ${hoveredCard === idx ? 'hovered' : ''}`}
              ref={setCardRef(idx)}
              style={{ backgroundColor: item.bgColor, color: item.textColor }}
              onMouseEnter={() => handleCardHover(idx)}
              onMouseLeave={() => handleCardLeave(idx)}
            >
              <div className="nav-card-overlay"></div>
              <div className="nav-card-content">
                <div className="nav-card-label">
                  <span>{item.label}</span>
                  <div className="nav-card-label-underline"></div>
                </div>
                <div className="nav-card-links">
                  {item.links?.map((lnk, i) => (
                    <a 
                      key={`${lnk.label}-${i}`} 
                      className="nav-card-link" 
                      href={lnk.href} 
                      aria-label={lnk.ariaLabel}
                    >
                      <span className="nav-card-link-text">{lnk.label}</span>
                      <ArrowUpRight className="nav-card-link-icon" aria-hidden="true" />
                    </a>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </nav>
    </div>
  );
};

export default CardNav;