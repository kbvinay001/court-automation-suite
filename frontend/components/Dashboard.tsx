import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const GOV = {
    navy: '#1a3a6b',
    navyDark: '#112655',
    gold: '#c9a84c',
    white: '#ffffff',
    offWhite: '#f4f6fb',
    border: '#cdd8e8',
    textDark: '#1a2f4e',
    textGrey: '#5a6a7e',
    green: '#2d7d46',
    amber: '#b86e00',
    red: '#c0392b',
};

const sectionCard: React.CSSProperties = {
    background: GOV.white,
    border: `1px solid ${GOV.border}`,
    borderRadius: '6px',
    overflow: 'hidden',
    marginBottom: '20px',
};

const sectionHeader: React.CSSProperties = {
    background: GOV.navy,
    color: GOV.white,
    padding: '10px 18px',
    fontSize: '13px',
    fontWeight: 700,
    letterSpacing: '0.5px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
};

interface UpcomingHearing { case_number: string; court_name: string; date: string; status: string; }

interface DashboardProps { onNavigate?: (tab: 'dashboard' | 'cases' | 'causelist' | 'analytics') => void; }

const NOTICES = [
    { date: '22-02-2026', text: 'Supreme Court: Constitution Bench sittings scheduled for the week of 24-28 Feb 2026.', type: 'urgent' },
    { date: '20-02-2026', text: 'Delhi High Court: Special Lok Adalat to be held on 01-03-2026. Eligible cases may be forwarded.', type: 'info' },
    { date: '18-02-2026', text: 'eCourts Portal: Maintenance window on 23-02-2026 from 02:00 to 04:00 IST. Services may be unavailable.', type: 'warning' },
    { date: '15-02-2026', text: 'Allahabad High Court: New e-filing system now live for Writ Petitions. Login to eFiling portal to access.', type: 'info' },
];

const QUICK_LINKS = [
    { label: 'eCourts Portal', url: 'https://ecourts.gov.in', icon: '🏛' },
    { label: 'Supreme Court Website', url: 'https://main.sci.gov.in', icon: '⚖️' },
    { label: 'National Judicial Data Grid', url: 'https://njdg.ecourts.gov.in', icon: '📊' },
    { label: 'eFiling Portal', url: 'https://filing.ecourts.gov.in', icon: '📂' },
    { label: 'High Court Services', url: 'https://hcservices.ecourts.gov.in', icon: '📋' },
    { label: 'National Legal Services', url: 'https://nalsa.gov.in', icon: '🤝' },
];

export default function Dashboard({ onNavigate }: DashboardProps) {
    const [stats, setStats] = useState([
        { label: 'Total Cases', value: '—', accent: GOV.navy, icon: '📋' },
        { label: 'Pending', value: '—', accent: GOV.amber, icon: '⏳' },
        { label: 'Disposed', value: '—', accent: GOV.green, icon: '✓' },
        { label: 'Upcoming Hearings', value: '—', accent: '#5e4fcb', icon: '🗓' },
    ]);
    const [hearings, setHearings] = useState<UpcomingHearing[]>([]);
    const [loading, setLoading] = useState(true);
    const [userName, setUserName] = useState('');
    const [userRole, setUserRole] = useState('');
    const [noticeExpanded, setNoticeExpanded] = useState<number | null>(null);

    useEffect(() => {
        try {
            const saved = localStorage.getItem('court_auth_user');
            if (saved) { const u = JSON.parse(saved); setUserName(u.full_name || 'User'); setUserRole(u.role || ''); }
        } catch { }
        fetchDashboard();
    }, []);

    const fetchDashboard = async () => {
        try {
            const res = await fetch(`${API_BASE}/analytics/dashboard`);
            if (res.ok) {
                const data = await res.json(); const d = data.data || {};
                setStats([
                    { label: 'Total Cases', value: (d.total_cases ?? 0).toLocaleString(), accent: GOV.navy, icon: '📋' },
                    { label: 'Pending', value: (d.pending_cases ?? 0).toLocaleString(), accent: GOV.amber, icon: '⏳' },
                    { label: 'Disposed', value: (d.disposed_cases ?? 0).toLocaleString(), accent: GOV.green, icon: '✓' },
                    { label: 'Upcoming Hearings', value: (d.upcoming_hearings ?? 0).toLocaleString(), accent: '#5e4fcb', icon: '🗓' },
                ]);
            }
            const hr = await fetch(`${API_BASE}/scraper/hearings/upcoming?days=7`);
            if (hr.ok) { const hd = await hr.json(); setHearings(hd.data || []); }
        } catch { } finally { setLoading(false); }
    };

    const hour = new Date().getHours();
    const greeting = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening';
    const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

    const noticeColor = (type: string) => ({
        urgent: { bg: '#fff5f5', border: '#e53e3e', dot: GOV.red },
        warning: { bg: '#fffbeb', border: '#d69e2e', dot: GOV.amber },
        info: { bg: '#ebf8ff', border: '#3182ce', dot: '#2b6cb0' },
    }[type] || { bg: GOV.offWhite, border: GOV.border, dot: GOV.navy });

    return (
        <div style={{ fontFamily: '"Segoe UI", system-ui, sans-serif' }}>

            {/* Welcome Banner */}
            <div style={{ background: `linear-gradient(135deg, ${GOV.navy} 0%, #2a4f8a 100%)`, borderRadius: '6px', padding: '20px 24px', marginBottom: '22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderLeft: `5px solid ${GOV.gold}` }}>
                <div>
                    <div style={{ color: '#a8c8e8', fontSize: '12px', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '4px' }}>{greeting}</div>
                    <div style={{ color: GOV.white, fontSize: '22px', fontWeight: 700 }}>{userName}</div>
                    <div style={{ color: '#8ab4d4', fontSize: '12px', marginTop: '3px', textTransform: 'capitalize' }}>{userRole} · {today}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ textAlign: 'right', color: '#a8c0d8' }}>
                        <div style={{ fontSize: '11px', letterSpacing: '1px', textTransform: 'uppercase' }}>eCourts Portal</div>
                        <div style={{ fontSize: '13px', fontWeight: 700, color: GOV.gold }}>यतो धर्मस्ततो जयः</div>
                    </div>
                    <img src="/emblem.png" alt="Emblem" style={{ height: '56px', opacity: 0.3 }} />
                </div>
            </div>

            {/* Stat Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '22px' }}>
                {stats.map((s, i) => (
                    <div key={i} style={{ background: GOV.white, border: `1px solid ${GOV.border}`, borderTop: `4px solid ${s.accent}`, borderRadius: '6px', padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ fontSize: '11px', color: GOV.textGrey, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{s.label}</div>
                        <div style={{ fontSize: '36px', fontWeight: 800, color: s.accent, lineHeight: 1 }}>{loading ? '—' : s.value}</div>
                    </div>
                ))}
            </div>

            {/* Bottom two-column layout */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
                <div>
                    {/* Upcoming Hearings */}
                    <div style={sectionCard}>
                        <div style={sectionHeader}>
                            <span>📋 Upcoming Hearings — Next 7 Days</span>
                            <span style={{ background: GOV.gold, color: GOV.navy, fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '12px' }}>{hearings.length} listed</span>
                        </div>
                        {loading ? (
                            <div style={{ padding: '40px', textAlign: 'center', color: GOV.textGrey }}>Loading hearings…</div>
                        ) : hearings.length > 0 ? (
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                                <thead>
                                    <tr style={{ background: '#eef2f8' }}>
                                        {['Case Number', 'Court', 'Date', 'Status'].map(h => (
                                            <th key={h} style={{ padding: '9px 14px', textAlign: 'left', fontWeight: 700, color: GOV.navy, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.4px', borderBottom: `1px solid ${GOV.border}` }}>{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {hearings.map((h, i) => (
                                        <tr key={i} style={{ borderBottom: `1px solid ${GOV.border}`, background: i % 2 === 0 ? GOV.white : '#fafcff' }}>
                                            <td style={{ padding: '9px 14px', fontFamily: 'monospace', color: GOV.navy, fontWeight: 700 }}>{h.case_number}</td>
                                            <td style={{ padding: '9px 14px', color: GOV.textDark, fontSize: '12px' }}>{h.court_name}</td>
                                            <td style={{ padding: '9px 14px', color: GOV.textDark }}>{h.date}</td>
                                            <td style={{ padding: '9px 14px' }}>
                                                <span style={{ background: h.status === 'pending' ? '#fff3cd' : '#d4edda', color: h.status === 'pending' ? '#856404' : '#155724', fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '3px', textTransform: 'uppercase' }}>{h.status}</span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div style={{ padding: '36px', textAlign: 'center' }}>
                                <div style={{ fontSize: '32px', marginBottom: '10px', opacity: 0.25 }}>📅</div>
                                <p style={{ color: GOV.textGrey, fontSize: '14px', margin: 0 }}>No upcoming hearings in next 7 days</p>
                                <button onClick={() => onNavigate?.('cases')} style={{ marginTop: '12px', background: GOV.navy, color: GOV.white, border: 'none', borderRadius: '4px', padding: '7px 18px', fontSize: '12px', cursor: 'pointer', fontFamily: 'inherit' }}>
                                    Start Tracking Cases
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Official Notices */}
                    <div style={sectionCard}>
                        <div style={sectionHeader}><span>📢 Official Notices &amp; Circulars</span></div>
                        {NOTICES.map((n, i) => {
                            const c = noticeColor(n.type);
                            return (
                                <div key={i} style={{ borderBottom: `1px solid ${GOV.border}`, background: noticeExpanded === i ? c.bg : GOV.white, borderLeft: noticeExpanded === i ? `4px solid ${c.border}` : '4px solid transparent', transition: 'all 0.2s' }}>
                                    <button
                                        onClick={() => setNoticeExpanded(noticeExpanded === i ? null : i)}
                                        style={{ width: '100%', background: 'none', border: 'none', padding: '12px 16px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', textAlign: 'left', fontFamily: 'inherit' }}
                                    >
                                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: c.dot, flexShrink: 0, display: 'inline-block' }} />
                                        <span style={{ fontSize: '12px', color: GOV.textGrey, minWidth: '90px' }}>{n.date}</span>
                                        <span style={{ fontSize: '13px', color: GOV.textDark, flex: 1 }}>{n.text.slice(0, 70)}{n.text.length > 70 ? '…' : ''}</span>
                                        <span style={{ color: GOV.textGrey, fontSize: '12px' }}>{noticeExpanded === i ? '▲' : '▼'}</span>
                                    </button>
                                    {noticeExpanded === i && (
                                        <div style={{ padding: '0 16px 14px 38px', fontSize: '13px', color: GOV.textDark, lineHeight: '1.6' }}>{n.text}</div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Right Column */}
                <div>
                    {/* Quick Actions */}
                    <div style={sectionCard}>
                        <div style={sectionHeader}><span>Quick Actions</span></div>
                        {[
                            { label: 'Case Search & Tracking', desc: 'Find cases by number or party', tab: 'cases' as const, icon: '🔍' },
                            { label: 'Cause List Monitor', desc: "Today's court listings", tab: 'causelist' as const, icon: '📅' },
                            { label: 'Analytics & Insights', desc: 'Court performance trends', tab: 'analytics' as const, icon: '📊' },
                        ].map((a, i) => (
                            <button key={i} onClick={() => onNavigate?.(a.tab)} style={{ width: '100%', background: 'none', border: 'none', borderBottom: `1px solid ${GOV.border}`, padding: '12px 16px', cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center', gap: '12px', transition: 'background 0.15s', fontFamily: 'inherit' }}
                                onMouseEnter={e => (e.currentTarget.style.background = GOV.offWhite)}
                                onMouseLeave={e => (e.currentTarget.style.background = 'none')}
                            >
                                <div style={{ width: '36px', height: '36px', background: GOV.navy, borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', flexShrink: 0 }}>{a.icon}</div>
                                <div>
                                    <div style={{ fontSize: '13px', fontWeight: 700, color: GOV.navy }}>{a.label}</div>
                                    <div style={{ fontSize: '11px', color: GOV.textGrey, marginTop: '1px' }}>{a.desc}</div>
                                </div>
                                <span style={{ marginLeft: 'auto', color: GOV.gold, fontSize: '18px' }}>›</span>
                            </button>
                        ))}
                    </div>

                    {/* Quick Links */}
                    <div style={sectionCard}>
                        <div style={sectionHeader}><span>🔗 External Links</span></div>
                        <div style={{ padding: '8px 0' }}>
                            {QUICK_LINKS.map((l, i) => (
                                <a key={i} href={l.url} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '9px 16px', textDecoration: 'none', borderBottom: `1px solid ${GOV.border}`, transition: 'background 0.15s', color: GOV.textDark }}
                                    onMouseEnter={e => (e.currentTarget.style.background = GOV.offWhite)}
                                    onMouseLeave={e => (e.currentTarget.style.background = 'none')}
                                >
                                    <span style={{ fontSize: '15px' }}>{l.icon}</span>
                                    <span style={{ fontSize: '12px', fontWeight: 600, color: '#2b6cb0', flex: 1 }}>{l.label}</span>
                                    <span style={{ fontSize: '10px', color: GOV.textGrey }}>↗</span>
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* System Status */}
                    <div style={sectionCard}>
                        <div style={sectionHeader}><span>⚙ System Status</span></div>
                        <div style={{ padding: '12px 16px' }}>
                            {[
                                { service: 'API Server', status: 'Online', ok: true },
                                { service: 'Case Database', status: 'Online', ok: true },
                                { service: 'Scraper Engine', status: 'Running', ok: true },
                                { service: 'Cache (Redis)', status: 'Unavailable', ok: false },
                            ].map((s, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: i < 3 ? `1px solid ${GOV.border}` : 'none' }}>
                                    <span style={{ fontSize: '12px', color: GOV.textDark }}>{s.service}</span>
                                    <span style={{ fontSize: '11px', fontWeight: 700, background: s.ok ? '#d4edda' : '#f8d7da', color: s.ok ? '#155724' : '#721c24', padding: '2px 8px', borderRadius: '3px' }}>{s.status}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
