import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

export default function LandingPage() {
  // Handle theme initialization (matching Shruti's script)
  useEffect(() => {
    try {
      const stored = localStorage.getItem("theme");
      const theme = stored || (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
      document.documentElement.setAttribute("data-theme", theme);
    } catch (e) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  }, []);

  return (
    <div className="home">
      <a className="skip-link" href="#main">Skip to content</a>

      {/* AMBIENT BACKGROUND */}
      <div className="aurora" aria-hidden="true">
        <span className="aurora__blob aurora__blob--one"></span>
        <span className="aurora__blob aurora__blob--two"></span>
        <span className="aurora__blob aurora__blob--three"></span>
        <span className="aurora__grid"></span>
      </div>

      {/* NAVIGATION BAR */}
      <header className="site-nav">
        <div className="site-nav__inner">
          {/* BRAND */}
          <a className="brand__link" href="/" aria-label="Coder's Hideout home">
            <span className="brand__mark" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L21 7V17L12 22L3 17V7L12 2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
                <path d="M12 2V22M3 7L12 12L21 7M3 17L12 12L21 17" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" opacity="0.55" />
              </svg>
            </span>
            <span className="brand__name">Coder's Hideout</span>
          </a>

          {/* MAIN NAVIGATION */}
          <nav className="site-nav__links" id="navLinks" aria-label="Primary">
            <a href="#about">About</a>
            <a href="#rooms">Rooms</a>
            <a href="#updates">Updates</a>
            <a href="#team">Team</a>
            <a href="#faqs">FAQs</a>
            <a href="#feedback">Feedback</a>
            <a href="#contact">Contact Us</a>
          </nav>

          {/* NAV ACTIONS */}
          <div className="site-nav__actions">
            {/* Theme Toggle */}
            <button type="button" className="theme-toggle" id="themeToggle" aria-label="Switch to light theme" aria-pressed="false">
              <span className="theme-toggle__icon theme-toggle__moon" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
                </svg>
              </span>
              <span className="theme-toggle__icon theme-toggle__sun" aria-hidden="true" style={{ display: 'none' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.6" />
                  <path d="M12 2.5V5M12 19V21.5M21.5 12H19M5 12H2.5M18.4 5.6L16.6 7.4M7.4 16.6L5.6 18.4M18.4 18.4L16.6 16.6M7.4 7.4L5.6 5.6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
              </span>
            </button>

            {/* Logged out buttons */}
            <div id="loggedOutActions" className="auth-actions">
              <Link className="ghost-btn" to="/login">Log in</Link>
              <Link className="cta-btn cta-btn--nav" to="/signup">Create your hideout</Link>
            </div>

            {/* Mobile menu */}
            <button type="button" className="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks">
              <span></span><span></span><span></span>
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main id="main">
        {/* HERO */}
        <section className="hero">
          <div className="hero__copy">
            <p className="eyebrow">Welcome to Coder's HideOut</p>
            <h1 className="hero__title">A quiet corner of the internet, built for shipping code.</h1>
            <p className="hero__subtitle">
              Coder's Hideout is a private space for the code you're not ready to show anyone — snippets, half-built ideas, and the projects you keep coming back to at night.
            </p>
            <div className="hero__actions">
              <Link className="cta-btn" to="/signup">Create your hideout</Link>
              <Link className="ghost-btn ghost-btn--lg" to="/login">I already have a key →</Link>
            </div>
            <p className="hero__note">Free to start. No credit card. Cancel by just closing the tab.</p>
          </div>

          {/* CODE WINDOW */}
          <div className="hero__visual" aria-hidden="true">
            <div className="window">
              <div className="window__glow"></div>
              <div className="window__bar">
                <span></span><span></span><span></span>
                <span className="window__bar-label">~/hideout</span>
              </div>
              <pre className="window__code"><code>
                <span className="c-muted">$</span> new feature 4681 added <span className="c-string">"you can now edit xyz"</span><br/>
                <span className="c-muted">$</span> new feature 4680 added<br/>
                <span className="c-success">✓</span> new feature 4679 added<br/>
                <span className="c-muted">$</span> <span className="cursor"></span>
              </code></pre>
            </div>
          </div>
        </section>

        {/* ABOUT */}
        <section className="about-section" id="about">
          <div className="section-head">
            <p className="eyebrow">About Coder's Hideout</p>
            <h2>Built for developers who love to build.</h2>
            <p className="section-sub">A focused digital space where ideas can grow before they are ready for the outside world.</p>
          </div>
          <div className="about-grid">
            <div className="about-card"><div className="about-icon">💡</div><h3>Think</h3><p>Capture ideas, experiment with concepts, and keep your unfinished thoughts in one place.</p></div>
            <div className="about-card"><div className="about-icon">💻</div><h3>Build</h3><p>Store snippets, projects and experiments without the pressure of making everything perfect.</p></div>
            <div className="about-card"><div className="about-icon">🚀</div><h3>Ship</h3><p>Track your progress and turn those late-night ideas into something real.</p></div>
          </div>
        </section>

        {/* ROOMS */}
        <section className="rooms" id="rooms">
          <div className="section-head">
            <p className="eyebrow">Inside the hideout</p>
            <h2>Everything you need is already inside.</h2>
            <p className="section-sub">Four rooms, no roommates required.</p>
          </div>
          <div className="rooms__grid">
            <article className="room-card is-visible"><span className="room-card__icon" aria-hidden="true">🔐</span><h3>Room 1</h3><p>Secure vault for your sensitive snippets and API keys.</p></article>
            <article className="room-card is-visible"><span className="room-card__icon" aria-hidden="true">⏱️</span><h3>Room 2</h3><p>Deep work timer and session analytics.</p></article>
            <article className="room-card is-visible"><span className="room-card__icon" aria-hidden="true">📝</span><h3>Room 3</h3><p>Scratchpad for architectural mapping.</p></article>
            <article className="room-card is-visible"><span className="room-card__icon" aria-hidden="true">👥</span><h3>Room 4</h3><p>Multiplayer cursor sharing for duo debugging.</p></article>
          </div>
        </section>

        {/* STATS */}
        <section className="stats">
          <div className="stats__grid">
            <div className="stat"><span className="stat__number">2100000</span><span className="stat__label">snippets saved</span></div>
            <div className="stat"><span className="stat__number">48000</span><span className="stat__label">late-night sessions logged</span></div>
            <div className="stat"><span className="stat__number">0</span><span className="stat__label">ads, ever</span></div>
          </div>
        </section>

        {/* UPDATES */}
        <section className="updates" id="updates">
          <div className="section-head"><p className="eyebrow">Updates</p><h2>Recently added to the hideout.</h2></div>
          <ul className="updates__list">
            <li><span className="updates__tag">New</span><p><strong>Focus timer sounds</strong> — rain, keyboard clatter, or silence. The Workbench remembers your pick.</p></li>
            <li><span className="updates__tag updates__tag--fix">Improved</span><p><strong>Faster Vault search</strong> — snippets now surface as you type, not after you finish typing.</p></li>
            <li><span className="updates__tag">New</span><p><strong>Ship Log streaks</strong> — see how many days in a row you've shown up.</p></li>
          </ul>
        </section>

        {/* TEAM */}
        <section className="team-section" id="team">
          <div className="section-head"><p className="eyebrow">Meet the team</p><h2>The people behind the hideout.</h2></div>
          <div className="team-grid flex justify-center gap-8">
            <article className="team-card"><div className="team-avatar">Frontend</div><h3>Srijan & Shruti</h3></article>
            <article className="team-card"><div className="team-avatar">Backend</div><h3>Souvik & Saptarshi</h3></article>
            <article className="team-card"><div className="team-avatar">AI/ML</div><h3>Kiran & Avik</h3></article>
          </div>
        </section>

        {/* FAQ */}
        <section className="faq-section" id="faqs">
          <div className="section-head"><p className="eyebrow">FAQs</p><h2>Questions? We've got answers.</h2></div>
          <div className="faq-list">
            <details className="faq-item"><summary>Is Coder's Hideout free?</summary><p>Yes. You can start using the core features without needing a credit card.</p></details>
            <details className="faq-item"><summary>Can I give feedback?</summary><p>Absolutely. Use the Feedback section below to tell us what you like, what can be improved, or what features you'd like to see.</p></details>
          </div>
        </section>

        {/* FEEDBACK */}
        <section className="feedback-section" id="feedback">
          <div className="section-head"><p className="eyebrow">Your voice matters</p><h2>Help us improve the hideout.</h2></div>
          <form className="feedback-form" id="feedbackForm">
            <div className="feedback-row flex gap-4">
              <div className="form-group"><label htmlFor="feedbackName">Name</label><input type="text" id="feedbackName" placeholder="Your name" required /></div>
              <div className="form-group"><label htmlFor="feedbackEmail">Email</label><input type="email" id="feedbackEmail" placeholder="you@example.com" required /></div>
            </div>
            <div className="form-group">
              <label htmlFor="feedbackType">Feedback type</label>
              <select id="feedbackType" required>
                <option value="">Select an option</option>
                <option value="suggestion">Feature suggestion</option>
                <option value="bug">Report a bug</option>
              </select>
            </div>
            <div className="form-group"><label htmlFor="feedbackMessage">Your feedback</label><textarea id="feedbackMessage" rows={5} placeholder="Tell us what you think..." required></textarea></div>
            <button type="submit" className="cta-btn">Send Feedback →</button>
          </form>
        </section>

        {/* FOOTER CTA */}
        <section className="footer-cta">
          <h2>Your hideout is one click away.</h2>
          <p>Build quietly. Ship boldly.</p>
          <Link className="cta-btn cta-btn--lg" to="/signup">Create your hideout</Link>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="site-footer">
        <div className="site-footer__inner">
          <a className="brand__link" href="/" aria-label="Coder's Hideout home">
            <span className="brand__name">Coder's Hideout</span>
          </a>
          <nav className="site-footer__links" aria-label="Footer">
            <a href="#about">About</a><a href="#rooms">Rooms</a><a href="#team">Team</a><a href="#contact">Contact Us</a>
          </nav>
        </div>
      </footer>
    </div>
  );
}