import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/useAuthStore';

export default function LoginPage() {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    // React State for UI
    const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
    const [showPassword, setShowPassword] = useState(false);

    // React State for Form Data
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleLoginSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Calls the Axios service built earlier
            const data = await authService.login({ email, password });
            setAuth(data.accessToken, data.refreshToken, data.role);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.message || 'Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="page">
            <div className="auth-card">

                {/* Brand & Language Selector */}
                <div className="brand">
                    <span className="brand__mark" aria-hidden="true">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L21 7V17L12 22L3 17V7L12 2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
                            <path d="M12 2V22M3 7L12 12L21 7M3 17L12 12L21 17" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" opacity="0.55" />
                        </svg>
                    </span>
                    <span className="brand__name">Coder's Hideout</span>

                    <label className="lang-select" htmlFor="languageSelect">
                        <span className="sr-only">Language</span>
                        {/* Wired up to i18n engine */}
                        <select
                            id="languageSelect"
                            value={i18n.language}
                            onChange={(e) => i18n.changeLanguage(e.target.value)}
                        >
                            <option value="en">English</option>
                            <option value="hi">हिन्दी</option>
                        </select>
                    </label>
                </div>

                {/* Tab Toggle */}
                <div className="tabs" role="tablist">
                    <button
                        type="button"
                        className={`tabs__btn ${activeTab === 'login' ? 'is-active' : ''}`}
                        onClick={() => setActiveTab('login')}
                    >
                        Log In
                    </button>
                    <button
                        type="button"
                        className={`tabs__btn ${activeTab === 'signup' ? 'is-active' : ''}`}
                        onClick={() => setActiveTab('signup')}
                    >
                        Sign Up
                    </button>
                    <span className={`tabs__indicator ${activeTab === 'signup' ? 'is-signup' : ''}`} aria-hidden="true"></span>
                </div>

                {/* Sliding Viewport */}
                <div className="viewport">
                    <div
                        className="track"
                        style={{ transform: `translateX(${activeTab === 'login' ? '0%' : '-33.333%'})` }}
                    >

                        {/* LOG IN PANEL */}
                        <section className="panel">
                            <form className="form" onSubmit={handleLoginSubmit}>
                                <h1 className="form__title">Welcome back</h1>
                                <p className="form__subtitle">Log in to access your dashboard.</p>

                                <div className="field">
                                    <label htmlFor="loginEmail">Email address</label>
                                    <div className={`input-shell ${error ? 'is-invalid' : ''}`}>
                                        <input
                                            type="email"
                                            id="loginEmail"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="you@email.com"
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="field">
                                    <label htmlFor="loginPassword">Password</label>
                                    <div className="input-shell">
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            id="loginPassword"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Enter your password"
                                            required
                                        />
                                        <button
                                            type="button"
                                            className="eye-toggle"
                                            onClick={() => setShowPassword(!showPassword)}
                                        >
                                            {/* SVGs truncated for brevity - paste the eye SVGs here, ensuring stroke-width is strokeWidth */}
                                            {showPassword ? "Hide" : "Show"}
                                        </button>
                                    </div>
                                    {error && <p className="field__error is-visible" style={{ color: 'var(--danger)' }}>{error}</p>}
                                </div>

                                <button type="submit" className={`submit-btn ${loading ? 'is-loading' : ''}`} disabled={loading}>
                                    <span className="submit-btn__label">Log In</span>
                                    <span className="submit-btn__spinner" aria-hidden="true"></span>
                                </button>
                            </form>
                        </section>

                        {/* SIGN UP PANEL (Placeholder for now) */}
                        <section className="panel">
                            <form className="form">
                                <h1 className="form__title">Create your account</h1>
                                <p className="form__subtitle">Registration endpoints coming soon.</p>
                            </form>
                        </section>

                    </div>
                </div>
            </div>
        </main>
    );
}