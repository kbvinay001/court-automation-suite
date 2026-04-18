import React, { useState } from 'react';

interface RegisterPageProps {
    onSwitchToLogin: () => void;
    onRegister: (data: RegisterData) => Promise<{ success: boolean; error?: string }>;
}

interface RegisterData {
    email: string;
    full_name: string;
    password: string;
    phone?: string;
    role?: string;
    bar_council_id?: string;
}

const officials = [
    { name: 'Hon. Sanjiv Khanna', title: 'Chief Justice of India', img: '/cji.png' },
    { name: 'Smt. Droupadi Murmu', title: 'President of India', img: '/president.png' },
    { name: 'Shri Narendra Modi', title: 'Prime Minister of India', img: '/pm.png' },
    { name: 'Shri Arjun Ram Meghwal', title: 'Law Minister of India', img: '/lawminister.png' },
];

const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '8px 10px',
    border: '1px solid #b8c9dd',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#1a2f4e',
    outline: 'none',
    background: '#f8fafc',
    boxSizing: 'border-box',
    transition: 'border-color 0.2s',
};

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '11px',
    fontWeight: 600,
    color: '#1a3a6b',
    marginBottom: '4px',
};

export default function RegisterPage({ onSwitchToLogin, onRegister }: RegisterPageProps) {
    const [form, setForm] = useState({
        email: '',
        full_name: '',
        password: '',
        confirmPassword: '',
        phone: '',
        role: 'advocate',
        bar_council_id: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const updateField = (field: string, value: string) => {
        setForm((prev) => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        if (form.password !== form.confirmPassword) { setError('Passwords do not match'); return; }
        if (form.password.length < 8) { setError('Password must be at least 8 characters'); return; }
        setLoading(true);
        const result = await onRegister({
            email: form.email,
            full_name: form.full_name,
            password: form.password,
            phone: form.phone || undefined,
            role: form.role,
            bar_council_id: form.bar_council_id || undefined,
        });
        if (!result.success) setError(result.error || 'Registration failed');
        setLoading(false);
    };

    const roles = [
        { value: 'advocate', label: 'Advocate', icon: '⚖️' },
        { value: 'litigant', label: 'Litigant', icon: '👤' },
        { value: 'clerk', label: 'Clerk', icon: '📋' },
    ];

    return (
        <div className="min-h-screen flex flex-col" style={{ background: '#f0f4f8', fontFamily: "'Segoe UI', Arial, sans-serif" }}>

            {/* ── Top Government Header Bar ── */}
            <header style={{ background: '#1a3a6b', borderBottom: '3px solid #c9a84c' }}>
                <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
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
                    <div className="flex items-center gap-5">
                        <img src="/ministry-law.png" alt="Ministry of Law and Justice" style={{ height: '52px', objectFit: 'contain' }} />
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

            {/* Blue nav stripe */}
            <div style={{ background: '#1e50a2', height: '6px' }} />

            {/* ── Main Body ── */}
            <main className="flex-1" style={{ background: 'linear-gradient(135deg, #e8edf5 0%, #f5f7fb 60%, #dce6f0 100%)' }}>
                <div className="max-w-7xl mx-auto px-4 py-8">
                    <div className="flex flex-col lg:flex-row gap-6 items-start justify-center">

                        {/* ── LEFT: Officials + Supreme Court ── */}
                        <div className="w-full lg:w-3/5">
                            {/* Supreme Court Image */}
                            <div style={{
                                borderRadius: '8px', overflow: 'hidden',
                                border: '2px solid #c9a84c',
                                boxShadow: '0 4px 20px rgba(0,0,0,0.18)',
                                marginBottom: '20px', position: 'relative',
                            }}>
                                <img src="/supreme-court-bg.png" alt="Supreme Court of India"
                                    style={{ width: '100%', height: '260px', objectFit: 'cover', display: 'block' }} />
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
                                        background: '#ffffff', borderRadius: '8px',
                                        padding: '12px 8px 14px',
                                        border: '1px solid #d0daea', borderTop: '3px solid #1a3a6b',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.08)', textAlign: 'center',
                                    }}>
                                        <div style={{
                                            width: '100%', aspectRatio: '3/4', borderRadius: '6px',
                                            overflow: 'hidden', marginBottom: '10px',
                                            border: '2px solid #c9a84c', background: '#e8edf5',
                                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                                        }}>
                                            <img src={o.img} alt={o.name}
                                                style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top center' }} />
                                        </div>
                                        <p style={{ color: '#1a3a6b', fontSize: '11px', fontWeight: 700, lineHeight: 1.3, marginBottom: '3px' }}>
                                            {o.name}
                                        </p>
                                        <p style={{ color: '#5f7a99', fontSize: '9.5px', lineHeight: 1.3 }}>
                                            {o.title}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* ── RIGHT: Registration Form ── */}
                        <div className="w-full lg:w-2/5 flex justify-center">
                            <div style={{
                                background: '#ffffff', borderRadius: '8px',
                                border: '1px solid #c9a84c', borderTop: '4px solid #1a3a6b',
                                boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
                                width: '100%', maxWidth: '380px',
                                padding: '24px 24px 20px',
                            }}>
                                {/* Header */}
                                <div style={{ textAlign: 'center', marginBottom: '18px', borderBottom: '1px solid #e2e8f0', paddingBottom: '14px' }}>
                                    <img src="/emblem.png" alt="Emblem"
                                        style={{ height: '40px', margin: '0 auto 8px', display: 'block' }} />
                                    <h2 style={{ color: '#1a3a6b', fontSize: '16px', fontWeight: 700, marginBottom: '2px' }}>
                                        New User Registration
                                    </h2>
                                    <p style={{ color: '#5f7a99', fontSize: '10.5px' }}>Court Automation Suite · Govt. of India</p>
                                </div>

                                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '11px' }}>
                                    {error && (
                                        <div style={{
                                            padding: '7px 10px', borderRadius: '4px',
                                            background: '#fff0f0', border: '1px solid #fca5a5',
                                            color: '#b91c1c', fontSize: '11px'
                                        }}>
                                            {error}
                                        </div>
                                    )}

                                    {/* Name + Email side by side */}
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                        <div>
                                            <label style={labelStyle}>Full Name *</label>
                                            <input type="text" value={form.full_name} required
                                                onChange={(e) => updateField('full_name', e.target.value)}
                                                placeholder="Rajesh Kumar" style={inputStyle}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'} />
                                        </div>
                                        <div>
                                            <label style={labelStyle}>Email Address *</label>
                                            <input type="email" value={form.email} required
                                                onChange={(e) => updateField('email', e.target.value)}
                                                placeholder="advocate@example.com" style={inputStyle}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'} />
                                        </div>
                                    </div>

                                    {/* Phone + Bar Council */}
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                        <div>
                                            <label style={labelStyle}>Phone Number</label>
                                            <input type="tel" value={form.phone}
                                                onChange={(e) => updateField('phone', e.target.value)}
                                                placeholder="+91 98765 43210" style={inputStyle}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'} />
                                        </div>
                                        <div>
                                            <label style={labelStyle}>Bar Council ID</label>
                                            <input type="text" value={form.bar_council_id}
                                                onChange={(e) => updateField('bar_council_id', e.target.value)}
                                                placeholder="DL/1234/2020" style={inputStyle}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'} />
                                        </div>
                                    </div>

                                    {/* Role selector */}
                                    <div>
                                        <label style={labelStyle}>User Category *</label>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
                                            {roles.map((r) => (
                                                <button key={r.value} type="button"
                                                    onClick={() => updateField('role', r.value)}
                                                    style={{
                                                        padding: '8px 4px', borderRadius: '4px', textAlign: 'center',
                                                        fontSize: '11px', fontWeight: 600, cursor: 'pointer',
                                                        border: form.role === r.value ? '2px solid #1a3a6b' : '1px solid #b8c9dd',
                                                        background: form.role === r.value ? '#e8edf8' : '#f8fafc',
                                                        color: form.role === r.value ? '#1a3a6b' : '#5f7a99',
                                                        transition: 'all 0.15s',
                                                    }}>
                                                    <div style={{ fontSize: '16px', marginBottom: '2px' }}>{r.icon}</div>
                                                    {r.label}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Password + Confirm */}
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                        <div>
                                            <label style={labelStyle}>Password *</label>
                                            <div style={{ position: 'relative' }}>
                                                <input
                                                    type={showPassword ? 'text' : 'password'}
                                                    value={form.password} required minLength={8}
                                                    onChange={(e) => updateField('password', e.target.value)}
                                                    placeholder="Min 8 chars"
                                                    style={{ ...inputStyle, paddingRight: '32px' }}
                                                    onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                    onBlur={(e) => e.target.style.borderColor = '#b8c9dd'} />
                                                <button type="button" onClick={() => setShowPassword(!showPassword)}
                                                    style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#8aa0bc', padding: 0, fontSize: '13px' }}>
                                                    {showPassword ? '🙈' : '👁'}
                                                </button>
                                            </div>
                                        </div>
                                        <div>
                                            <label style={labelStyle}>Confirm Password *</label>
                                            <input type="password" value={form.confirmPassword} required minLength={8}
                                                onChange={(e) => updateField('confirmPassword', e.target.value)}
                                                placeholder="Repeat password" style={inputStyle}
                                                onFocus={(e) => e.target.style.borderColor = '#1a3a6b'}
                                                onBlur={(e) => e.target.style.borderColor = '#b8c9dd'} />
                                        </div>
                                    </div>

                                    {/* Password strength */}
                                    {form.password && (
                                        <div>
                                            <div style={{ display: 'flex', gap: '4px', marginBottom: '3px' }}>
                                                {[1, 2, 3, 4].map((level) => (
                                                    <div key={level} style={{
                                                        flex: 1, height: '3px', borderRadius: '2px',
                                                        background: form.password.length >= level * 3
                                                            ? (form.password.length >= 12 ? '#16a34a' : form.password.length >= 8 ? '#ca8a04' : '#dc2626')
                                                            : '#dde5ef',
                                                        transition: 'background 0.2s'
                                                    }} />
                                                ))}
                                            </div>
                                            <p style={{ fontSize: '10px', color: '#8aa0bc' }}>
                                                {form.password.length < 8 ? 'Too short' : form.password.length < 10 ? 'Fair' : form.password.length < 14 ? 'Good' : 'Strong'} password
                                            </p>
                                        </div>
                                    )}

                                    {/* Submit */}
                                    <button type="submit" disabled={loading}
                                        style={{
                                            width: '100%', padding: '10px',
                                            background: loading ? '#5f7a99' : '#1a3a6b',
                                            color: '#ffffff', border: 'none', borderRadius: '4px',
                                            fontSize: '12px', fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
                                            letterSpacing: '0.06em', textTransform: 'uppercase',
                                            transition: 'background 0.2s',
                                            boxShadow: '0 2px 6px rgba(26,58,107,0.3)',
                                            marginTop: '2px',
                                        }}
                                        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.background = '#122c55'; }}
                                        onMouseLeave={(e) => { if (!loading) e.currentTarget.style.background = '#1a3a6b'; }}>
                                        {loading ? 'Registering...' : '✓ Register Account'}
                                    </button>

                                    {/* Divider */}
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', margin: '2px 0' }}>
                                        <div style={{ flex: 1, height: '1px', background: '#dde5ef' }} />
                                        <span style={{ color: '#8aa0bc', fontSize: '10px' }}>ALREADY REGISTERED?</span>
                                        <div style={{ flex: 1, height: '1px', background: '#dde5ef' }} />
                                    </div>

                                    {/* Sign In */}
                                    <button type="button" onClick={onSwitchToLogin}
                                        style={{
                                            width: '100%', padding: '8px',
                                            background: 'transparent', color: '#1a3a6b',
                                            border: '1px solid #1a3a6b', borderRadius: '4px',
                                            fontSize: '11px', fontWeight: 600, cursor: 'pointer',
                                            letterSpacing: '0.04em', transition: 'background 0.2s, color 0.2s',
                                        }}
                                        onMouseEnter={(e) => { e.currentTarget.style.background = '#1a3a6b'; e.currentTarget.style.color = '#ffffff'; }}
                                        onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#1a3a6b'; }}>
                                        ← Sign In to Existing Account
                                    </button>
                                </form>

                                {/* Ministry footer */}
                                <div style={{ textAlign: 'center', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #e2e8f0' }}>
                                    <img src="/ministry-law.png" alt="Ministry of Law and Justice"
                                        style={{ height: '32px', objectFit: 'contain', marginBottom: '5px' }} />
                                    <p style={{ color: '#8aa0bc', fontSize: '9px', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
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
