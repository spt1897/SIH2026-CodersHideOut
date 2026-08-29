// src/components/auth/LoginForm.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/useAuthStore';

export default function LoginForm() {
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);

    const handleLoginSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
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
        <form onSubmit={handleLoginSubmit} className="flex flex-col gap-4 max-w-md mx-auto p-6 bg-white dark:bg-slate-50 shadow-md rounded-lg">
            <h2 className="text-xl font-bold text-blue-950 mb-4">Official Sign In</h2>
            
            {error && <p className="text-red-500 text-sm">{error}</p>}

            <label className="text-sm font-medium text-gray-700">Official Email</label>
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="officer@gov.in"
                className="p-2 border rounded"
                required
            />

            <label className="text-sm font-medium text-gray-700">Password</label>
            <div className="flex w-full border rounded bg-white">
                <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="p-2 flex-grow outline-none"
                    required
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="px-3 text-gray-500 text-sm">
                    {showPassword ? "Hide" : "Show"}
                </button>
            </div>

            <button type="submit" disabled={loading} className="bg-blue-900 text-white p-2 rounded hover:bg-blue-950 mt-2 disabled:opacity-50">
                {loading ? 'Authenticating...' : 'Secure Login'}
            </button>
        </form>
    );
}