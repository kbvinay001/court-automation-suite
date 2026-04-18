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

interface TrendData { date: string; filings: number; disposals: number; }
interface CourtPerformance { court_name: string; disposal_rate: number; pendency: number; avg_duration_days: number; }
interface CaseTypeData { case_type: string; count: number; percentage: number; }

const PERIODS = [
    { label: '7 Days', value: '7' },
    { label: '30 Days', value: '30' },
    { label: '90 Days', value: '90' },
    { label: '1 Year', value: '365' },
];

const ALL_COURTS = [
    'Supreme Court of India', 'Allahabad High Court', 'Andhra Pradesh High Court',
    'Bombay High Court', 'Calcutta High Court', 'Chhattisgarh High Court',
    'Delhi High Court', 'Gauhati High Court', 'Gujarat High Court',
    'Himachal Pradesh High Court', 'Jammu & Kashmir and Ladakh High Court',
    'Jharkhand High Court', 'Karnataka High Court', 'Kerala High Court',
    'Madhya Pradesh High Court', 'Madras High Court', 'Manipur High Court',
    'Meghalaya High Court', 'Orissa High Court', 'Patna High Court',
    'Punjab & Haryana High Court', 'Rajasthan High Court', 'Sikkim High Court',
    'Telangana High Court', 'Tripura High Court', 'Uttarakhand High Court',
];

export default function Analytics() {
    const [courtName, setCourtName] = useState('');
    const [period, setPeriod] = useState('30');
    const [trends, setTrends] = useState<TrendData[]>([]);
    const [performance, setPerformance] = useState<CourtPerformance[]>([]);
    const [caseTypes, setCaseTypes] = useState<CaseTypeData[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'types' | 'performance'>('overview');

    useEffect(() => { fetchAnalytics(); }, [courtName, period]);

    const fetchAnalytics = async () => {
        setLoading(true);
        try {
            const cParam = courtName ? `&court_name=${encodeURIComponent(courtName)}` : '';
            const [trendsRes, perfRes, typesRes] = await Promise.all([
                fetch(`${API_BASE}/analytics/trends?period=${period}${cParam}`).catch(() => null),
                fetch(`${API_BASE}/analytics/court-performance?${cParam}`).catch(() => null),
                fetch(`${API_BASE}/analytics/case-types?${cParam}`).catch(() => null),
            ]);
            if (trendsRes?.ok) { const d = await trendsRes.json(); setTrends(d.data || []); }
            if (perfRes?.ok) { const d = await perfRes.json(); setPerformance(d.data || []); }
            if (typesRes?.ok) { const d = await typesRes.json(); setCaseTypes(d.data || []); }
        } catch { } finally { setLoading(false); }
    };

    const totalFilings = trends.reduce((s, t) => s + t.filings, 0);
    const totalDisposals = trends.reduce((s, t) => s + t.disposals, 0);
    const disposalRate = totalFilings > 0 ? Math.round((totalDisposals / totalFilings) * 100) : 0;
    const maxFiling = Math.max(...trends.map(t => t.filings), 1);
    const topCourt = performance.sort((a, b) => b.disposal_rate - a.disposal_rate)[0];

    const TAB_ITEMS = [
        { key: 'overview' as const, label: 'Overview' },
        { key: 'trends' as const, label: 'Filing Trends' },
        { key: 'types' as const, label: 'Case Types' },
        { key: 'performance' as const, label: 'Court Performance' },
    ];

    return (
        <div style={{ fontFamily: '"Segoe UI", system-ui, sans-serif' }}>

            {/* Page title + filters */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '18px', gap: '16px', flexWrap: 'wrap' }}>
                <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 800, color: GOV.navy, margin: '0 0 4px 0' }}>Analytics &amp; Insights</h2>
                    <p style={{ fontSize: '13px', color: GOV.textGrey, margin: 0 }}>Court performance metrics, filing trends and case type distribution</p>
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '10px', fontWeight: 700, color: GOV.textGrey, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>Period</label>
                        <div style={{ display: 'flex', border: `1px solid ${GOV.border}`, borderRadius: '4px', overflow: 'hidden' }}>
                            {PERIODS.map(p => (
                                <button key={p.value} onClick={() => setPeriod(p.value)} style={{ background: period === p.value ? GOV.navy : GOV.white, color: period === p.value ? GOV.white : GOV.textDark, border: 'none', padding: '6px 14px', fontSize: '12px', fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', borderRight: `1px solid ${GOV.border}` }}>
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '10px', fontWeight: 700, color: GOV.textGrey, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>Court</label>
                        <select value={courtName} onChange={e => setCourtName(e.target.value)} style={{ padding: '7px 12px', border: `1px solid ${GOV.border}`, borderRadius: '4px', fontSize: '12px', color: GOV.textDark, background: GOV.white, outline: 'none', fontFamily: 'inherit', minWidth: '220px' }}>
                            <option value="">All Courts</option>
                            {ALL_COURTS.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>
                </div>
            </div>

            {/* Overview KPI row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '20px' }}>
                {[
                    { label: `Total Filings (${PERIODS.find(p => p.value === period)?.label || ''})`, value: totalFilings.toLocaleString(), accent: GOV.navy },
                    { label: 'Total Disposals', value: totalDisposals.toLocaleString(), accent: GOV.green },
                    { label: 'Disposal Rate', value: `${disposalRate}%`, accent: disposalRate >= 80 ? GOV.green : disposalRate >= 60 ? GOV.amber : '#c0392b' },
                    { label: 'Case Types Tracked', value: caseTypes.length, accent: '#5e4fcb' },
                ].map((s, i) => (
                    <div key={i} style={{ background: GOV.white, border: `1px solid ${GOV.border}`, borderTop: `4px solid ${s.accent}`, borderRadius: '6px', padding: '14px 16px' }}>
                        <div style={{ fontSize: '10px', color: GOV.textGrey, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>{s.label}</div>
                        <div style={{ fontSize: '28px', fontWeight: 800, color: s.accent, lineHeight: 1 }}>{loading ? '—' : s.value}</div>
                    </div>
                ))}
            </div>

            {/* Sub-tab nav */}
            <div style={{ display: 'flex', borderBottom: `2px solid ${GOV.border}`, marginBottom: '20px' }}>
                {TAB_ITEMS.map(t => (
                    <button key={t.key} onClick={() => setActiveTab(t.key)} style={{ background: 'none', border: 'none', borderBottom: activeTab === t.key ? `2px solid ${GOV.navy}` : '2px solid transparent', marginBottom: '-2px', color: activeTab === t.key ? GOV.navy : GOV.textGrey, padding: '9px 20px', fontSize: '13px', fontWeight: activeTab === t.key ? 700 : 500, cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.15s' }}>
                        {t.label}
                    </button>
                ))}
            </div>

            {/* Case Type Distribution */}
            {(activeTab === 'overview' || activeTab === 'types') && (
                <div style={sectionCard}>
                    <div style={sectionHeader}>
                        <span>📊 Case Type Distribution</span>
                        {caseTypes.length > 0 && <span style={{ background: GOV.gold, color: GOV.navy, fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '12px' }}>{caseTypes.length} types</span>}
                    </div>
                    <div style={{ padding: '18px' }}>
                        {caseTypes.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                {caseTypes.map((ct, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <span style={{ fontSize: '12px', color: GOV.textDark, minWidth: '180px', fontWeight: 600 }}>{ct.case_type}</span>
                                        <div style={{ flex: 1, background: GOV.offWhite, borderRadius: '3px', height: '20px', overflow: 'hidden', border: `1px solid ${GOV.border}`, position: 'relative' }}>
                                            <div style={{ height: '100%', background: i % 2 === 0 ? GOV.navy : '#2a4f8a', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: '8px', width: `${Math.max(ct.percentage, 5)}%`, transition: 'width 0.7s ease' }}>
                                                <span style={{ fontSize: '11px', fontWeight: 700, color: GOV.white }}>{ct.percentage}%</span>
                                            </div>
                                        </div>
                                        <span style={{ fontSize: '12px', color: GOV.textGrey, minWidth: '60px', textAlign: 'right' }}>{ct.count.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', padding: '32px', color: GOV.textGrey }}>{loading ? 'Loading data…' : 'No data available'}</div>
                        )}
                    </div>
                </div>
            )}

            {/* Trend Chart */}
            {(activeTab === 'overview' || activeTab === 'trends') && (
                <div style={sectionCard}>
                    <div style={sectionHeader}>
                        <span>📈 Filing &amp; Disposal Trends</span>
                        <div style={{ display: 'flex', gap: '14px', fontSize: '11px', fontWeight: 400 }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><span style={{ display: 'inline-block', width: '10px', height: '10px', background: GOV.navy, borderRadius: '2px' }} /> Filings</span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><span style={{ display: 'inline-block', width: '10px', height: '10px', background: GOV.gold, borderRadius: '2px' }} /> Disposals</span>
                        </div>
                    </div>
                    <div style={{ padding: '18px' }}>
                        {trends.length > 0 ? (
                            <>
                                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '160px', overflowX: 'auto', paddingBottom: '8px' }}>
                                    {trends.map((t, i) => (
                                        <div key={i} title={`${t.date}: ${t.filings} filings, ${t.disposals} disposals`} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: '0 0 auto', minWidth: '18px' }}>
                                            <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1px', height: '140px' }}>
                                                <div style={{ width: '8px', background: GOV.navy, borderRadius: '2px 2px 0 0', height: `${(t.filings / maxFiling) * 100}%`, minHeight: '3px' }} />
                                                <div style={{ width: '8px', background: GOV.gold, borderRadius: '2px 2px 0 0', height: `${(t.disposals / maxFiling) * 100}%`, minHeight: '3px' }} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                {/* Trend summary row */}
                                <div style={{ display: 'flex', gap: '20px', borderTop: `1px solid ${GOV.border}`, paddingTop: '12px', fontSize: '12px', color: GOV.textGrey }}>
                                    <span>📅 Period: Last {period} days</span>
                                    <span>📤 Avg. daily filings: <strong style={{ color: GOV.navy }}>{Math.round(totalFilings / Math.max(trends.length, 1))}</strong></span>
                                    <span>📥 Avg. daily disposals: <strong style={{ color: GOV.green }}>{Math.round(totalDisposals / Math.max(trends.length, 1))}</strong></span>
                                </div>
                            </>
                        ) : (
                            <div style={{ textAlign: 'center', padding: '32px', color: GOV.textGrey }}>{loading ? 'Loading trends…' : 'No trend data available'}</div>
                        )}
                    </div>
                </div>
            )}

            {/* Court Performance */}
            {(activeTab === 'overview' || activeTab === 'performance') && (
                <div style={sectionCard}>
                    <div style={sectionHeader}>
                        <span>🏛 Court Performance</span>
                        {topCourt && <span style={{ fontSize: '11px', fontWeight: 400, color: '#a8c0e0' }}>Best: {topCourt.court_name} ({topCourt.disposal_rate}%)</span>}
                    </div>
                    {performance.length > 0 ? (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                            <thead>
                                <tr style={{ background: '#eef2f8' }}>
                                    {['#', 'Court', 'Disposal Rate', 'Pendency', 'Avg. Duration'].map((h, i) => (
                                        <th key={h} style={{ padding: '9px 14px', textAlign: 'left', fontWeight: 700, color: GOV.navy, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.4px', borderBottom: `1px solid ${GOV.border}`, width: i === 0 ? '38px' : undefined }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[...performance].sort((a, b) => b.disposal_rate - a.disposal_rate).map((p, i) => (
                                    <tr key={i} style={{ background: i % 2 === 0 ? GOV.white : '#fafcff', borderBottom: `1px solid ${GOV.border}` }}>
                                        <td style={{ padding: '9px 14px', color: GOV.textGrey, textAlign: 'center', fontSize: '12px' }}>{i + 1}</td>
                                        <td style={{ padding: '9px 14px', fontWeight: 700, color: GOV.textDark }}>{p.court_name}</td>
                                        <td style={{ padding: '9px 14px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                <div style={{ width: '100px', background: GOV.offWhite, borderRadius: '3px', height: '10px', overflow: 'hidden', border: `1px solid ${GOV.border}` }}>
                                                    <div style={{ height: '100%', background: p.disposal_rate >= 80 ? GOV.green : p.disposal_rate >= 60 ? GOV.amber : '#c0392b', width: `${p.disposal_rate}%`, transition: 'width 0.5s' }} />
                                                </div>
                                                <span style={{ fontSize: '13px', fontWeight: 700, color: p.disposal_rate >= 80 ? GOV.green : p.disposal_rate >= 60 ? GOV.amber : '#c0392b' }}>{p.disposal_rate}%</span>
                                            </div>
                                        </td>
                                        <td style={{ padding: '9px 14px', fontWeight: 600, color: GOV.amber }}>{p.pendency.toLocaleString()}</td>
                                        <td style={{ padding: '9px 14px', color: GOV.textGrey }}>{p.avg_duration_days} days</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div style={{ padding: '40px', textAlign: 'center', color: GOV.textGrey }}>{loading ? 'Loading performance data…' : 'No performance data available'}</div>
                    )}
                </div>
            )}
        </div>
    );
}
