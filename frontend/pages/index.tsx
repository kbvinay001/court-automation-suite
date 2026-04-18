import React, { useState } from 'react';
import { AuthProvider, useAuth } from '../components/AuthContext';
import LoginPage from '../components/LoginPage';
import RegisterPage from '../components/RegisterPage';
import Dashboard from '../components/Dashboard';
import CaseSearch from '../components/CaseSearch';
import CauseListMonitor from '../components/CauseListMonitor';
import Analytics from '../components/Analytics';

type Tab = 'dashboard' | 'cases' | 'causelist' | 'analytics';
type AuthView = 'login' | 'register';

const GOV = {
    navy: '#1a3a6b',
    navyDark: '#112655',
    gold: '#c9a84c',
    goldLight: '#f0e0a0',
    white: '#ffffff',
    offWhite: '#f4f6fb',
    border: '#cdd8e8',
    textDark: '#1a2f4e',
    textGrey: '#5a6a7e',
};

const navTabs: { key: Tab; label: string }[] = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'cases', label: 'Case Search & Tracking' },
    { key: 'causelist', label: 'Cause List Monitor' },
    { key: 'analytics', label: 'Analytics' },
];

function AppContent() {
    const { isAuthenticated, isLoading, user, login, register, logout } = useAuth();
    const [activeTab, setActiveTab] = useState<Tab>('dashboard');
    const [authView, setAuthView] = useState<AuthView>('login');

    if (isLoading) {
        return (
            <div style={{ minHeight: '100vh', background: GOV.navy, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: '"Segoe UI", system-ui, sans-serif' }}>
                <div style={{ textAlign: 'center', color: GOV.white }}>
                    <img src="/emblem.png" alt="Emblem" style={{ height: '64px', marginBottom: '20px', filter: 'brightness(0) invert(1) opacity(0.8)' }} />
                    <p style={{ color: GOV.goldLight, fontSize: '15px', letterSpacing: '1px' }}>Loading Court Automation Suite…</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        if (authView === 'register') {
            return <RegisterPage onSwitchToLogin={() => setAuthView('login')} onRegister={register} />;
        }
        return <LoginPage onSwitchToRegister={() => setAuthView('register')} onLogin={login} />;
    }

    const breadcrumb = navTabs.find(t => t.key === activeTab)?.label || 'Dashboard';

    return (
        <div style={{ minHeight: '100vh', background: GOV.offWhite, fontFamily: '"Segoe UI", system-ui, sans-serif', display: 'flex', flexDirection: 'column' }}>

            {/* ── Top Header ── */}
            <header style={{ background: GOV.navy, boxShadow: '0 2px 8px rgba(0,0,0,0.25)' }}>

                {/* Gold stripe */}
                <div style={{ height: '4px', background: `linear-gradient(90deg, ${GOV.gold}, #e8c96a, ${GOV.gold})` }} />

                {/* Logo Row */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 32px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <img src="/emblem.png" alt="Supreme Court of India" style={{ height: '48px', objectFit: 'contain' }} />
                        <div>
                            <div style={{ fontSize: '10px', color: GOV.goldLight, letterSpacing: '1.5px', textTransform: 'uppercase', fontWeight: 500 }}>
                                Government of India · Ministry of Law &amp; Justice
                            </div>
                            <div style={{ fontSize: '20px', fontWeight: 700, color: GOV.white, lineHeight: '1.2', letterSpacing: '0.3px' }}>
                                Court Automation Suite
                            </div>
                            <div style={{ fontSize: '11px', color: '#a8c0e0', marginTop: '1px' }}>
                                eCourts — Integrated Case Management Portal
                            </div>
                        </div>
                    </div>

                    {/* User section */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '12px', color: GOV.goldLight, fontWeight: 600 }}>
                                Welcome, {user?.full_name || 'User'}
                            </div>
                            <div style={{ fontSize: '11px', color: '#8aabcf', textTransform: 'capitalize' }}>
                                {user?.role} · {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.25)', color: GOV.white, padding: '6px 14px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', transition: 'background 0.2s' }}
                            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(201,168,76,0.25)')}
                            onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
                        >
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
                            Sign Out
                        </button>
                    </div>
                </div>

                {/* Navigation Tab Row */}
                <nav style={{ display: 'flex', alignItems: 'stretch', paddingLeft: '24px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    {navTabs.map(tab => (
                        <button
                            key={tab.key}
                            onClick={() => setActiveTab(tab.key)}
                            style={{
                                background: activeTab === tab.key ? 'rgba(201,168,76,0.18)' : 'transparent',
                                border: 'none',
                                borderBottom: activeTab === tab.key ? `3px solid ${GOV.gold}` : '3px solid transparent',
                                color: activeTab === tab.key ? GOV.gold : 'rgba(255,255,255,0.75)',
                                padding: '12px 22px',
                                fontSize: '13px',
                                fontWeight: activeTab === tab.key ? 700 : 500,
                                cursor: 'pointer',
                                letterSpacing: '0.3px',
                                transition: 'all 0.2s',
                                fontFamily: 'inherit',
                            }}
                            onMouseEnter={e => { if (activeTab !== tab.key) e.currentTarget.style.color = GOV.white; }}
                            onMouseLeave={e => { if (activeTab !== tab.key) e.currentTarget.style.color = 'rgba(255,255,255,0.75)'; }}
                        >
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </header>

            {/* ── Breadcrumb Bar ── */}
            <div style={{ background: GOV.white, borderBottom: `1px solid ${GOV.border}`, padding: '7px 32px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', color: GOV.textGrey }}>Home</span>
                <span style={{ fontSize: '12px', color: GOV.textGrey }}>›</span>
                <span style={{ fontSize: '12px', color: GOV.navy, fontWeight: 600 }}>{breadcrumb}</span>
            </div>

            {/* ── Page Content ── */}
            <main style={{ flex: 1, maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '28px 24px' }}>
                {activeTab === 'dashboard' && <Dashboard onNavigate={setActiveTab} />}
                {activeTab === 'cases' && <CaseSearch />}
                {activeTab === 'causelist' && <CauseListMonitor />}
                {activeTab === 'analytics' && <Analytics />}
            </main>

            {/* ── Footer ── */}
            <footer style={{ background: GOV.navy, borderTop: `3px solid ${GOV.gold}`, padding: '14px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <img src="/emblem.png" alt="Emblem" style={{ height: '28px', opacity: 0.7 }} />
                    <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '12px' }}>
                        Court Automation Suite © {new Date().getFullYear()} · Ministry of Law &amp; Justice, Govt. of India
                    </span>
                </div>
                <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '11px' }}>
                    🔒 Secure · Official Use Only
                </span>
            </footer>
        </div>
    );
}

export default function Home() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}
