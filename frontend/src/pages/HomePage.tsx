import React, { useEffect, useState } from 'react';
import './style.css';
import './home.css';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('theme');
    const defaultTheme = stored || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    setTheme(defaultTheme as 'light' | 'dark');
    document.documentElement.setAttribute('data-theme', defaultTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  return (
    <div className="home">
      <a className="skip-link" href="#main">Skip to content</a>
      <div className="aurora" aria-hidden="true">
        <span className="aurora__blob aurora__blob--one"></span>
        <span className="aurora__blob aurora__blob--two"></span>
        <span className="aurora__blob aurora__blob--three"></span>
        <span className="aurora__grid"></span>
      </div>

      <header className="site-nav">
        <div className="site-nav__inner">
          <Link className="brand__link" to="/">
            <span className="brand__mark" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L21 7V17L12 22L3 17V7L12 2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
                <path d="M12 2V22M3 7L12 12L21 7M3 17L12 12L21 17" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" opacity="0.55" />
              </svg>
            </span>
            <span className="brand__name">TerraSentry</span>
          </Link>

          <nav className={`site-nav__links ${navOpen ? 'is-open' : ''}`} id="navLinks">
            <a href="#about">About</a>
            <a href="#rooms">Rooms</a>
            <a href="#updates">Updates</a>
            <div className="mobile-nav-actions">
              <Link className="ghost-btn" to="/login">Log in</Link>
              <Link className="cta-btn" to="/login">Create your account</Link>
            </div>
          </nav>

          <div className="site-nav__actions">
            <button type="button" className="theme-toggle" onClick={toggleTheme}>
              <span className="theme-toggle__icon theme-toggle__moon" aria-hidden={theme === 'dark'}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
                </svg>
              </span>
              <span className="theme-toggle__icon theme-toggle__sun" aria-hidden={theme === 'light'}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.6" />
                  <path d="M12 2.5V5M12 19V21.5M21.5 12H19M5 12H2.5M18.4 5.6L16.6 7.4M7.4 16.6L5.6 18.4M18.4 18.4L16.6 16.6M7.4 7.4L5.6 5.6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
              </span>
            </button>
            <Link className="ghost-btn desktop-login" to="/login">Log in</Link>
            <Link className="cta-btn cta-btn--nav desktop-signup" to="/login">Create your account</Link>
            <button type="button" className="nav-toggle" onClick={() => setNavOpen(!navOpen)}>
              <span></span><span></span><span></span>
            </button>
          </div>
        </div>
      </header>

      <main id="main">
        <section className="hero">
          <div className="hero__copy">
            <p className="eyebrow">early warning system</p>
            <h1 className="hero__title">Disaster Management and landslide early warning system</h1>
            <p className="hero__subtitle">Real-time geospatial analytics and predictive intelligence for terrains.</p>
            <div className="hero__actions">
              <Link className="cta-btn" to="/login">Create your account</Link>
              <Link className="ghost-btn ghost-btn--lg" to="/login">I already have a key →</Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}