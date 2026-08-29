import React, { useState, useEffect } from 'react';
import '../style.css'; // Ensure her CSS file is in the same directory

export default function AuthPage() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [userType, setUserType] = useState<'citizen' | 'official'>('citizen');
  const [activeTab, setActiveTab] = useState<'login' | 'signup' | 'forgot'>('login');
  const [loginStep, setLoginStep] = useState<1 | 2>(1);
  const [signupStep, setSignupStep] = useState<1 | 2>(1);
  const [showPassword, setShowPassword] = useState(false);

  // Initialize theme based on localStorage or system preference
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

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginStep === 1) setLoginStep(2);
    // Add actual API authentication here
  };

  const handleSignupSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userType === 'citizen' && signupStep === 1) {
      setSignupStep(2);
    } else {
      // Official signup or final citizen verification API call here
    }
  };

  return (
    <div className="page-wrapper">
      <div className="aurora" aria-hidden="true">
        <span className="aurora__blob aurora__blob--one"></span>
        <span className="aurora__blob aurora__blob--two"></span>
        <span className="aurora__blob aurora__blob--three"></span>
        <span className="aurora__grid"></span>
      </div>

      <main className="page">
        <div className="auth-card" id="authCard" data-user-type={userType}>
          
          {/* Header & Controls */}
          <div className="brand">
            <a className="brand__link" href="/" aria-label="Home">
              <span className="brand__mark" aria-hidden="true">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L21 7V17L12 22L3 17V7L12 2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
                  <path d="M12 2V22M3 7L12 12L21 7M3 17L12 12L21 17" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" opacity="0.55"/>
                </svg>
              </span>
              <span className="brand__name">TerraSentry</span>
            </a>

            <div className="brand__actions">
              <button type="button" className="theme-toggle" onClick={toggleTheme} aria-label="Switch theme">
                <span className="theme-toggle__icon theme-toggle__moon" aria-hidden={theme === 'dark'}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
                  </svg>
                </span>
                <span className="theme-toggle__icon theme-toggle__sun" aria-hidden={theme === 'light'}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.6"/>
                    <path d="M12 2.5V5M12 19V21.5M21.5 12H19M5 12H2.5M18.4 5.6L16.6 7.4M7.4 16.6L5.6 18.4M18.4 18.4L16.6 16.6M7.4 7.4L5.6 5.6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                  </svg>
                </span>
              </button>
              
              <label className="lang-select" htmlFor="languageSelect">
                <span className="sr-only">Interface language</span>
                <select id="languageSelect" defaultValue="en">
                  <option value="en">English</option>
                  <option value="hi">हिन्दी</option>
                </select>
              </label>
            </div>
          </div>

          {/* User Type Toggles */}
          {activeTab !== 'forgot' && (
            <div className="user-type" role="tablist">
              <button 
                type="button" 
                className={`user-type__btn ${userType === 'citizen' ? 'is-active' : ''}`} 
                onClick={() => setUserType('citizen')}
              >
                Public / Citizen
              </button>
              <button 
                type="button" 
                className={`user-type__btn ${userType === 'official' ? 'is-active' : ''}`} 
                onClick={() => setUserType('official')}
              >
                Official / Institutional
              </button>
            </div>
          )}

          {/* Login/Signup Tabs */}
          {activeTab !== 'forgot' && (
            <div className="tabs" role="tablist">
              <button 
                type="button" 
                className={`tabs__btn ${activeTab === 'login' ? 'is-active' : ''}`} 
                onClick={() => { setActiveTab('login'); setLoginStep(1); }}
              >
                Log In
              </button>
              <button 
                type="button" 
                className={`tabs__btn ${activeTab === 'signup' ? 'is-active' : ''}`} 
                onClick={() => { setActiveTab('signup'); setSignupStep(1); }}
              >
                Sign Up
              </button>
            </div>
          )}

          {/* Viewport for Forms */}
          <div className="viewport">
            <div className="track">

              {/* LOG IN PANEL */}
              {activeTab === 'login' && (
                <section className="panel">
                  <form className="form" onSubmit={handleLoginSubmit} noValidate>
                    <h1 className="form__title">Welcome back</h1>
                    <p className="form__subtitle">
                      {userType === 'citizen' ? "No password needed — we'll text you a one-time code." : "Log in with your official credentials."}
                    </p>

                    {loginStep === 1 && (
                      <div className="form-step">
                        {userType === 'citizen' ? (
                          <div className="field">
                            <label htmlFor="citizenLoginMobile">Mobile number</label>
                            <div className="input-shell input-shell--prefix">
                              <span className="input-prefix">+91</span>
                              <input type="tel" id="citizenLoginMobile" name="mobile" inputMode="numeric" autoComplete="tel" placeholder="98XXX XXXXX" maxLength={10} required />
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="field">
                              <label htmlFor="officialLoginIdentifier">Official email or username</label>
                              <div className="input-shell">
                                <input type="text" id="officialLoginIdentifier" name="identifier" autoComplete="username" placeholder="you@nic.in" required />
                              </div>
                            </div>
                            <div className="field">
                              <label htmlFor="officialLoginPassword">Password</label>
                              <div className="input-shell">
                                <input type={showPassword ? "text" : "password"} id="officialLoginPassword" name="password" autoComplete="current-password" placeholder="Enter your password" required />
                                <button type="button" className="eye-toggle" onClick={() => setShowPassword(!showPassword)}>
                                  {showPassword ? "Hide" : "Show"}
                                </button>
                              </div>
                            </div>
                            <div className="form__row">
                              <label className="checkbox">
                                <input type="checkbox" name="rememberMe" />
                                <span className="checkbox__box" aria-hidden="true"></span>
                                <span>Remember me</span>
                              </label>
                              <button type="button" className="link-btn" onClick={() => setActiveTab('forgot')}>Forgot password?</button>
                            </div>
                          </>
                        )}
                        <button type="submit" className="submit-btn">Send OTP</button>
                      </div>
                    )}

                    {loginStep === 2 && (
                      <div className="form-step">
                        <p className="otp-info">
                          {userType === 'citizen' ? "Enter the 6-digit code sent to your mobile." : "Multi-factor authentication is required."}
                        </p>
                        <div className="field">
                          <label htmlFor="loginOtp">One-time code</label>
                          <div className="input-shell">
                            <input type="text" id="loginOtp" inputMode="numeric" maxLength={6} placeholder="••••••" required />
                          </div>
                        </div>
                        <p className="resend-row">
                          <button type="button" className="link-btn" onClick={() => setLoginStep(1)}>← Back</button>
                        </p>
                        <button type="submit" className="submit-btn">Verify & Log In</button>
                      </div>
                    )}

                    <p className="form__switch">
                      <span>Don't have an account? </span>
                      <button type="button" className="link-btn link-btn--accent" onClick={() => { setActiveTab('signup'); setSignupStep(1); }}>Create one</button>
                    </p>
                  </form>
                </section>
              )}

              {/* SIGN UP PANEL */}
              {activeTab === 'signup' && (
                <section className="panel">
                  <form className="form" onSubmit={handleSignupSubmit} noValidate>
                    <h1 className="form__title">{userType === 'citizen' ? "Create your account" : "Register your official account"}</h1>
                    
                    {signupStep === 1 && (
                      <div className="form-step">
                        {userType === 'citizen' ? (
                          <>
                            <div className="field">
                              <label htmlFor="citizenSignupMobile">Mobile number</label>
                              <div className="input-shell input-shell--prefix">
                                <span className="input-prefix">+91</span>
                                <input type="tel" id="citizenSignupMobile" maxLength={10} required />
                              </div>
                            </div>
                            <div className="field">
                              <label htmlFor="citizenSignupName">Name (optional)</label>
                              <div className="input-shell">
                                <input type="text" id="citizenSignupName" />
                              </div>
                            </div>
                            <div className="field">
                              <label htmlFor="citizenSignupPincode">Home location (PIN code)</label>
                              <div className="input-shell">
                                <input type="text" id="citizenSignupPincode" maxLength={6} required />
                              </div>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="field">
                              <label htmlFor="officialSignupName">Full name</label>
                              <div className="input-shell">
                                <input type="text" id="officialSignupName" required />
                              </div>
                            </div>
                            <div className="field">
                              <label htmlFor="officialSignupEmail">Official email address</label>
                              <div className="input-shell">
                                <input type="email" id="officialSignupEmail" required />
                              </div>
                            </div>
                            <div className="field">
                              <label htmlFor="officialSignupPassword">Password</label>
                              <div className="input-shell">
                                <input type={showPassword ? "text" : "password"} id="officialSignupPassword" required />
                              </div>
                            </div>
                          </>
                        )}
                        <button type="submit" className="submit-btn">Continue</button>
                      </div>
                    )}

                    {signupStep === 2 && userType === 'citizen' && (
                      <div className="form-step">
                        <p className="otp-info">Enter the verification code.</p>
                        <div className="field">
                          <label htmlFor="citizenSignupOtp">One-time code</label>
                          <div className="input-shell">
                            <input type="text" id="citizenSignupOtp" maxLength={6} required />
                          </div>
                        </div>
                        <p className="resend-row">
                          <button type="button" className="link-btn" onClick={() => setSignupStep(1)}>← Back</button>
                        </p>
                        <button type="submit" className="submit-btn">Verify & Create Account</button>
                      </div>
                    )}

                    <p className="form__switch">
                      <span>Already have an account? </span>
                      <button type="button" className="link-btn link-btn--accent" onClick={() => { setActiveTab('login'); setLoginStep(1); }}>Log in</button>
                    </p>
                  </form>
                </section>
              )}

              {/* FORGOT PASSWORD PANEL */}
              {activeTab === 'forgot' && (
                <section className="panel">
                  <form className="form" onSubmit={(e) => e.preventDefault()} noValidate>
                    <h1 className="form__title">Reset your password</h1>
                    <p className="form__subtitle">For official accounts. Enter your official email to reset.</p>
                    <div className="field">
                      <label htmlFor="forgotEmail">Official email address</label>
                      <div className="input-shell">
                        <input type="email" id="forgotEmail" required />
                      </div>
                    </div>
                    <button type="submit" className="submit-btn">Send Reset Link</button>
                    <p className="form__switch">
                      <button type="button" className="link-btn link-btn--accent" onClick={() => setActiveTab('login')}>← Back to log in</button>
                    </p>
                  </form>
                </section>
              )}

            </div>
          </div>
        </div>
      </main>
    </div>
  );
}