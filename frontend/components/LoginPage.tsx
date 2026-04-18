import React, { useState } from 'react';

interface LoginPageProps {
    onSwitchToRegister: () => void;
    onLogin: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
}

const officials = [
    { name: 'Hon. Sanjiv Khanna', title: 'Chief Justice of India', img: '/cji.png' },
    { name: 'Smt. Droupadi Murmu', title: 'President of India', img: '/president.png' },
    { name: 'Shri Narendra Modi', title: 'Prime Minister of India', img: '/pm.png' },
    { name: 'Shri Arjun Ram Meghwal', title: 'Law Minister of India', img: '/lawminister.png' },
];

export default function LoginPage({ onSwitchToRegister, onLogin }: LoginPageProps) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        const result = await onLogin(email, password);
        if (!result.success) {
            setError(result.error || 'Login failed');
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex flex-col" style={{ background: '#f0f4f8', fontFamily: "'Segoe UI', Arial, sans-serif" }}>

            {/* ── Top Government Header Bar ── */}
            <header style={{ background: '#1a3a6b', borderBottom: '3px solid #c9a84c' }}>
                <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
                    {/* Left: Emblem + Title */}
                    <div className="flex items-center gap-4">
                        <img src="/emblem.png" alt="National Emblem" style={{ height: '56px' }} />
                        <div>
                            <p style={{ color: '#c9a84c', fontSize: '10px', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '1px' }}>
                                Government of India
                            </p>
                            <h1 style={{ color: '#ffffff', fontSize: '20px', fontWeight: 700, letterSpacing: '0.02em', lineHeight: 1.2 }}>
                                Court Automation Suite
                            </h1>
                            <p style={{ color: '#a8c0e0', fontSize: '11px', letterSpacing: '0.05em' }}>
                                Ministry of Law &amp; Justice
                            </p>
                        </div>
                    </div>
                    {/* Right: Ministry Logo + Satyamev */}
                    <div className="flex items-center gap-5">
                        <img
                            src="/ministry-law.png"
                            alt="Ministry of Law and Justice"
                            style={{ height: '52px', objectFit: 'contain' }}
                        />
                        <div className="text-right hidden sm:block" style={{ borderLeft: '1px solid rgba(201,168,76,0.5)', paddingLeft: '16px' }}>
                            <p style={{ color: '#c9a84c', fontSize: '18px', fontFamily: "'Noto Sans Devanagari', sans-serif" }}>
                                सत्यमेव जयते
                            </p>
                            <p style={{ color: '#a8c0e0', fontSize: '9px', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                                Truth Alone Triumphs
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* ── Blue nav stripe (decorative, like government sites) ── */}
            <div style={{ background: '#1e50a2', height: '6px' }} />

            {/* ── Main Body ── */}
            <main className="flex-1" style={{ background: 'linear-gradient(135deg, #e8edf5 0%, #f5f7fb 60%, #dce6f0 100%)' }}>
                <div className="max-w-7xl mx-auto px-4 py-8">

                    {/* Layout: Officials panel left, Login right */}
                    <div className="flex flex-col lg:flex-row gap-6 items-start justify-center">

                        {/* ── LEFT: Officials Portrait Gallery + SC Image ── */}
                        <div className="w-full lg:w-3/5">

                            {/* Supreme Court Image */}
                            <div style={{
                                borderRadius: '8px',
                                overflow: 'hidden',
                                border: '2px solid #c9a84c',
                                boxShadow: '0 4px 20px rgba(0,0,0,0.18)',
                                marginBottom: '20px',
                                position: 'relative',
                            }}>
                                <img
                                    src="/supreme-court-bg.png"
                                    alt="Supreme Court of India"
                                    style={{ width: '100%', height: '260px', objectFit: 'cover', display: 'block' }}
                                />
                                <div style={{
                                    position: 'absolute', bottom: 0, left: 0, right: 0,
                                    background: 'linear-gradient(transparent, rgba(10,25,60,0.88))',
                                    padding: '20px 18px 14px',
                                }}>
                                    <p style={{ color: '#ffffff', fontSize: '17px', fontWeight: 600, fontFamily: "'Noto Sans Devanagari', sans-serif" }}>
                                        यतो धर्मस्ततो जयः
                                    </p>
                                    <p style={{ color: '#c9a84c', fontSize: '10px', letterSpacing: '0.15em', textTransform: 'uppercase', marginTop: '2px' }}>
                                        Supreme Court of India
                                    </p>
                                </div>
                            </div>

                            {/* Officials Portrait Grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                                {officials.map((o, i) => (
                                    <div key={i} style={{
                                        background: '#ffffff',
                                        borderRadius: '8px',
                                        padding: '12px 8px 14px',
                                        border: '1px solid #d0daea',
                                        borderTop: '3px solid #1a3a6b',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                                        textAlign: 'center',
                                    }}>
                                        {/* Portrait photo */}
                                        <div style={{
                                            width: '100%',
                                            aspectRatio: '3/4',
                                            borderRadius: '6px',
                                            overflow: 'hidden',
                                            marginBottom: '10px',
                                            border: '2px solid #c9a84c',
                                            background: '#e8edf5',
                                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                                        }}>
                                            <img
                                                src={o.img}
                                                alt={o.name}
                                                style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top center' }}
                                            />
                                        </div>
                                        <p style={{ color: '#1a3a6b', fontSize: '11px', fontWeight: 700, lineHeight: 1.3, marginBottom: '3px' }}>
                                            {o.name}
                                        </p>
                                        <p style={{ color: '#5f7a99', fontSize: '9.5px', lineHeight: 1.3, letterSpacing: '0.02em' }}>
                                            {o.title}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* ── RIGHT: Login Box ── */}
                        <div className="w-full lg:w-2/5 flex justify-center" style={{ paddingTop: '4px' }}>
                            <div style={{
                                background: '#ffffff',
                                borderRadius: '8px',
                                border: '1px solid #c9a84c',
                                borderTop: '4px solid #1a3a6b',
                                boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
                                width: '100%',
                                maxWidth: '360px',
                                padding: '28px 28px 24px',
                            }}>
                                {/* Login header */}
                                <div style={{ textAlign: 'center', marginBottom: '22px', borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' }}>
                                    <img src="/emblem.png" alt="Emblem" style={{ height: '44px', margin: '0 auto 8px', display: 'block' }} />
                                    <h2 style={{ color: '#1a3a6b', fontSize: '17px', fontWeight: 700, letterSpacing: '0.02em', marginBottom: '2px' }}>
                                        User Login
                                    </h2>
                                    <p style={{ color: '#5f7a99', fontSize: '11px' }}>Court Automation Suite</p>
                                </div>

                                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                                    {/* Error */}
                                    {error && (
                                        <div style={{
                                            padding: '8px 12px', borderRadius: '4px',
                                            background: '#fff0f0', border: '1px solid #fca5a5',
                                            color: '#b91c1c', fontSize: '12px'
                                        }}>
                                            {error}
                                        </div>
                                    )}

                                    {/* Email */}
                                    <div>
                                        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#1a3a6b', marginBottom: '5px' }}>
                                            Email Address / User ID
                                        </label>
                                        <div style={{ position: 'relative' }}>
                                            <svg style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', width: '15px', height: '15px', color: '#8aa0bc' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                                                <rect x="2" y="4" width="20" height="16" rx="2" /><path d="M22 4L12 13 2 4" />
                                            </svg>
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                required
                                                autoComplete="email"
                                                placeholder="Enter your email"
                                                style={{
                                                    width: '100%', padding: '9px 12px 9px 34px',
                                                    border: '1px solid #b8c9dd', borderRadius: '4px',
                                                    fontSize: '13px', color: '#1a2f4e', outline: 'none',
                                                    background: '#f8fafc', boxSizing: 'border-box',
                                                    transition: 'border-color 0.2s',
                                                }}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'}
                                            />
                                        </div>
                                    </div>

                                    {/* Password */}
                                    <div>
                                        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#1a3a6b', marginBottom: '5px' }}>
                                            Password
                                        </label>
                                        <div style={{ position: 'relative' }}>
                                            <svg style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', width: '15px', height: '15px', color: '#8aa0bc' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                                                <rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                                            </svg>
                                            <input
                                                type={showPassword ? 'text' : 'password'}
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                required
                                                autoComplete="current-password"
                                                placeholder="Enter your password"
                                                style={{
                                                    width: '100%', padding: '9px 36px 9px 34px',
                                                    border: '1px solid #b8c9dd', borderRadius: '4px',
                                                    fontSize: '13px', color: '#1a2f4e', outline: 'none',
                                                    background: '#f8fafc', boxSizing: 'border-box',
                                                    transition: 'border-color 0.2s',
                                                }}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'}
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowPassword(!showPassword)}
                                                style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#8aa0bc', padding: 0 }}
                                            >
                                                {showPassword ? (
                                                    <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                                                        <line x1="1" y1="1" x2="23" y2="23" />
                                                    </svg>
                                                ) : (
                                                    <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
                                                    </svg>
                                                )}
                                            </button>
                                        </div>
                                    </div>

                                    {/* Submit */}
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        style={{
                                            width: '100%', padding: '10px',
                                            background: loading ? '#5f7a99' : '#1a3a6b',
                                            color: '#ffffff', border: 'none', borderRadius: '4px',
                                            fontSize: '13px', fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
                                            letterSpacing: '0.06em', textTransform: 'uppercase',
                                            transition: 'background 0.2s',
                                            boxShadow: '0 2px 6px rgba(26,58,107,0.3)',
                                            marginTop: '4px',
                                        }}
                                        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.background = '#122c55'; }}
                                        onMouseLeave={(e) => { if (!loading) e.currentTarget.style.background = '#1a3a6b'; }}
                                    >
                                        {loading ? 'Signing in...' : '→ Sign In'}
                                    </button>

                                    {/* Divider */}
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', margin: '4px 0' }}>
                                        <div style={{ flex: 1, height: '1px', background: '#dde5ef' }} />
                                        <span style={{ color: '#8aa0bc', fontSize: '11px' }}>OR</span>
                                        <div style={{ flex: 1, height: '1px', background: '#dde5ef' }} />
                                    </div>

                                    {/* Register */}
                                    <button
                                        type="button"
                                        onClick={onSwitchToRegister}
                                        style={{
                                            width: '100%', padding: '9px',
                                            background: 'transparent', color: '#1a3a6b',
                                            border: '1px solid #1a3a6b', borderRadius: '4px',
                                            fontSize: '12px', fontWeight: 600, cursor: 'pointer',
                                            letterSpacing: '0.04em',
                                            transition: 'background 0.2s, color 0.2s',
                                        }}
                                        onMouseEnter={(e) => { e.currentTarget.style.background = '#1a3a6b'; e.currentTarget.style.color = '#ffffff'; }}
                                        onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#1a3a6b'; }}
                                    >
                                        Create New Account
                                    </button>
                                </form>

                                {/* Ministry of Law logo at bottom of login box */}
                                <div style={{ textAlign: 'center', marginTop: '18px', paddingTop: '14px', borderTop: '1px solid #e2e8f0' }}>
                                    <img
                                        src="/ministry-law.png"
                                        alt="Ministry of Law and Justice"
                                        style={{ height: '36px', objectFit: 'contain', marginBottom: '6px' }}
                                    />
                                    <p style={{ color: '#8aa0bc', fontSize: '9.5px', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                                        Ministry of Law &amp; Justice · Govt. of India
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* ── Footer ── */}
            <footer style={{ background: '#1a3a6b', borderTop: '3px solid #c9a84c', padding: '12px 24px' }}>
                <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2">
                    <p style={{ color: '#a8c0e0', fontSize: '10.5px', letterSpacing: '0.04em' }}>
                        © Government of India · Ministry of Law &amp; Justice · Court Automation Suite
                    </p>
                    <p style={{ color: '#7a9abf', fontSize: '10px' }}>
                        Secured by JWT Authentication · 256-bit Encryption
                    </p>
                </div>
            </footer>
        </div>
    );
}
