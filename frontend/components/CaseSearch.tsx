import React, { useState } from 'react';

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

const inputStyle: React.CSSProperties = {
    padding: '8px 12px',
    border: `1px solid ${GOV.border}`,
    borderRadius: '4px',
    fontSize: '13px',
    color: GOV.textDark,
    background: GOV.white,
    outline: 'none',
    fontFamily: 'inherit',
    boxSizing: 'border-box',
};

const navyBtn: React.CSSProperties = {
    background: GOV.navy,
    color: GOV.white,
    border: 'none',
    borderRadius: '4px',
    padding: '8px 22px',
    fontSize: '13px',
    fontWeight: 700,
    cursor: 'pointer',
    fontFamily: 'inherit',
    transition: 'background 0.2s',
    whiteSpace: 'nowrap',
};

interface CaseDetail {
    case_number: string;
    court_type: string;
    court_name: string;
    petitioner: string;
    respondent: string;
    advocate_petitioner?: string;
    advocate_respondent?: string;
    status: string;
    filing_date?: string;
    next_hearing_date?: string;
    subject?: string;
    bench?: string;
    hearings?: { date: string; order_summary?: string }[];
}

const STATUS_STYLES: Record<string, React.CSSProperties> = {
    pending: { background: '#fff3cd', color: '#856404' },
    disposed: { background: '#d4edda', color: '#155724' },
    listed: { background: '#cce5ff', color: '#004085' },
    heard: { background: '#e2d9f3', color: '#4a2170' },
    adjourned: { background: '#ffe5d0', color: '#7d3b00' },
};
const statusBadge = (status: string): React.CSSProperties => ({
    ...(STATUS_STYLES[status?.toLowerCase()] || { background: '#e2e8f0', color: '#374151' }),
    fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '3px', textTransform: 'uppercase',
});

export default function CaseSearch() {
    const [query, setQuery] = useState('');
    const [courtType, setCourtType] = useState('');
    const [yearFilter, setYearFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [results, setResults] = useState<CaseDetail[]>([]);
    const [selectedCase, setSelectedCase] = useState<CaseDetail | null>(null);
    const [loading, setLoading] = useState(false);
    const [tracking, setTracking] = useState<Set<string>>(new Set());
    const [error, setError] = useState('');
    const [showFilters, setShowFilters] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) { setError('Please enter a case number or party name.'); return; }
        setLoading(true); setError(''); setSelectedCase(null);
        try {
            const params = new URLSearchParams({ query });
            if (courtType) params.set('court_type', courtType);
            if (yearFilter) params.set('year', yearFilter);
            if (statusFilter) params.set('status', statusFilter);
            const res = await fetch(`${API_BASE}/scraper/search?${params}`);
            const data = await res.json();
            setResults(data.data || []);
            if (!data.data?.length) setError('No cases found. Try adjusting your search terms or filters.');
        } catch { setError('Search failed. Please check your connection.'); }
        finally { setLoading(false); }
    };

    const trackCase = async (caseNumber: string) => {
        try {
            await fetch(`${API_BASE}/scraper/track/${encodeURIComponent(caseNumber)}`, { method: 'POST' });
            setTracking(prev => new Set([...prev, caseNumber]));
        } catch { }
    };

    const exportResults = () => {
        const csv = ['Case Number,Court,Petitioner,Respondent,Status,Filing Date,Next Hearing']
            .concat(results.map(c => `"${c.case_number}","${c.court_name}","${c.petitioner}","${c.respondent}","${c.status}","${c.filing_date || ''}","${c.next_hearing_date || ''}"`)
            ).join('\n');
        const a = document.createElement('a');
        a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
        a.download = `case-search-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
    };

    const years = Array.from({ length: 15 }, (_, i) => String(new Date().getFullYear() - i));

    return (
        <div style={{ fontFamily: '"Segoe UI", system-ui, sans-serif' }}>

            {/* Page Title */}
            <div style={{ marginBottom: '18px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 800, color: GOV.navy, margin: '0 0 4px 0' }}>Case Search &amp; Tracking</h2>
                <p style={{ fontSize: '13px', color: GOV.textGrey, margin: 0 }}>Search cases across all Indian courts by case number, party name, or advocate name</p>
            </div>

            {/* Search Form */}
            <div style={sectionCard}>
                <div style={sectionHeader}>
                    <span>🔍 Search Parameters</span>
                    <button
                        onClick={() => setShowFilters(v => !v)}
                        style={{ background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', color: GOV.white, padding: '3px 12px', borderRadius: '3px', fontSize: '11px', cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600 }}
                    >
                        {showFilters ? '▲ Hide Filters' : '▼ Advanced Filters'}
                    </button>
                </div>
                <form onSubmit={handleSearch} style={{ padding: '18px' }}>
                    {/* Primary row */}
                    <div style={{ display: 'flex', gap: '12px', marginBottom: showFilters ? '14px' : '0', flexWrap: 'wrap' }}>
                        <input
                            type="text"
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            placeholder="Case number (WP(C)/1234/2024) or party / advocate name…"
                            style={{ ...inputStyle, flex: 1, minWidth: '280px' }}
                        />
                        <select value={courtType} onChange={e => setCourtType(e.target.value)} style={{ ...inputStyle, width: '180px' }}>
                            <option value="">All Court Types</option>
                            <option value="supreme_court">Supreme Court of India</option>
                            <option value="high_court">High Court</option>
                            <option value="district_court">District Court</option>
                            <option value="tribunal">Tribunal / Commission</option>
                        </select>
                        <button type="submit" disabled={loading} style={{ ...navyBtn, opacity: loading ? 0.7 : 1 }}
                            onMouseEnter={e => (e.currentTarget.style.background = GOV.navyDark)}
                            onMouseLeave={e => (e.currentTarget.style.background = GOV.navy)}
                        >
                            {loading ? '⏳ Searching…' : '🔍  Search'}
                        </button>
                    </div>

                    {/* Advanced Filters */}
                    {showFilters && (
                        <div style={{ borderTop: `1px solid ${GOV.border}`, paddingTop: '14px', display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                            <div style={{ flex: 1, minWidth: '150px' }}>
                                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: GOV.navy, textTransform: 'uppercase', letterSpacing: '0.4px', marginBottom: '5px' }}>Filing Year</label>
                                <select value={yearFilter} onChange={e => setYearFilter(e.target.value)} style={{ ...inputStyle, width: '100%' }}>
                                    <option value="">All Years</option>
                                    {years.map(y => <option key={y} value={y}>{y}</option>)}
                                </select>
                            </div>
                            <div style={{ flex: 1, minWidth: '150px' }}>
                                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: GOV.navy, textTransform: 'uppercase', letterSpacing: '0.4px', marginBottom: '5px' }}>Case Status</label>
                                <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{ ...inputStyle, width: '100%' }}>
                                    <option value="">All Statuses</option>
                                    <option value="pending">Pending</option>
                                    <option value="listed">Listed</option>
                                    <option value="heard">Heard</option>
                                    <option value="adjourned">Adjourned</option>
                                    <option value="disposed">Disposed</option>
                                </select>
                            </div>
                            <button type="button" onClick={() => { setYearFilter(''); setStatusFilter(''); setCourtType(''); }}
                                style={{ background: GOV.white, color: GOV.textGrey, border: `1px solid ${GOV.border}`, borderRadius: '4px', padding: '8px 16px', fontSize: '12px', cursor: 'pointer', fontFamily: 'inherit' }}>
                                Reset Filters
                            </button>
                        </div>
                    )}
                </form>
            </div>

            {error && (
                <div style={{ background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px', padding: '10px 16px', marginBottom: '16px', color: '#856404', fontSize: '13px' }}>
                    ⚠ {error}
                </div>
            )}

            {/* Results header row */}
            {results.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div style={{ fontSize: '13px', color: GOV.textGrey }}>
                        Found <strong style={{ color: GOV.navy }}>{results.length}</strong> case{results.length !== 1 ? 's' : ''} — click a row to view details
                    </div>
                    <button onClick={exportResults} style={{ background: GOV.white, color: GOV.navy, border: `1px solid ${GOV.navy}`, borderRadius: '4px', padding: '6px 14px', fontSize: '12px', fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        ⬇ Export CSV
                    </button>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: results.length > 0 ? '1fr 2fr' : '1fr', gap: '20px' }}>

                {/* Results List */}
                {results.length > 0 && (
                    <div style={sectionCard}>
                        <div style={sectionHeader}>
                            <span>Search Results</span>
                            <span style={{ background: GOV.gold, color: GOV.navy, fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '12px' }}>{results.length}</span>
                        </div>
                        <div style={{ maxHeight: '480px', overflowY: 'auto' }}>
                            {results.map((c, i) => (
                                <button
                                    key={i}
                                    onClick={() => setSelectedCase(c)}
                                    style={{
                                        width: '100%', background: selectedCase?.case_number === c.case_number ? '#eef4ff' : 'none',
                                        border: 'none', borderBottom: `1px solid ${GOV.border}`, padding: '11px 14px',
                                        cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit',
                                        borderLeft: selectedCase?.case_number === c.case_number ? `4px solid ${GOV.navy}` : '4px solid transparent',
                                        transition: 'all 0.15s',
                                    }}
                                    onMouseEnter={e => { if (selectedCase?.case_number !== c.case_number) e.currentTarget.style.background = GOV.offWhite; }}
                                    onMouseLeave={e => { if (selectedCase?.case_number !== c.case_number) e.currentTarget.style.background = 'none'; }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                        <span style={{ fontFamily: 'monospace', fontSize: '12px', fontWeight: 700, color: GOV.navy }}>{c.case_number}</span>
                                        <span style={statusBadge(c.status)}>{c.status}</span>
                                    </div>
                                    <div style={{ fontSize: '13px', color: GOV.textDark, fontWeight: 600 }}>{c.petitioner}</div>
                                    <div style={{ fontSize: '12px', color: GOV.textGrey }}>vs. {c.respondent}</div>
                                    <div style={{ fontSize: '11px', color: '#aab8cc', marginTop: '3px' }}>{c.court_name}</div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Case Detail */}
                {selectedCase && (
                    <div style={sectionCard}>
                        <div style={{ ...sectionHeader, background: GOV.navy }}>
                            <span>📄 {selectedCase.case_number}</span>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                    onClick={() => trackCase(selectedCase.case_number)}
                                    style={{ background: tracking.has(selectedCase.case_number) ? GOV.green : GOV.gold, color: GOV.white, border: 'none', borderRadius: '4px', padding: '4px 14px', fontSize: '11px', fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}
                                >
                                    {tracking.has(selectedCase.case_number) ? '✓ Tracking' : '+ Track Case'}
                                </button>
                            </div>
                        </div>
                        <div style={{ padding: '18px' }}>
                            {/* Sub header */}
                            <div style={{ background: GOV.offWhite, border: `1px solid ${GOV.border}`, borderRadius: '4px', padding: '10px 14px', marginBottom: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <div style={{ fontSize: '12px', color: GOV.textGrey }}>Court</div>
                                    <div style={{ fontSize: '14px', fontWeight: 700, color: GOV.navy }}>{selectedCase.court_name}</div>
                                </div>
                                <span style={statusBadge(selectedCase.status)}>{selectedCase.status}</span>
                            </div>

                            {/* 2x3 detail grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', border: `1px solid ${GOV.border}`, borderRadius: '4px', overflow: 'hidden', marginBottom: '18px' }}>
                                {[
                                    { label: 'Petitioner', value: selectedCase.petitioner },
                                    { label: 'Respondent', value: selectedCase.respondent },
                                    { label: "Petitioner's Advocate", value: selectedCase.advocate_petitioner || '—' },
                                    { label: "Respondent's Advocate", value: selectedCase.advocate_respondent || '—' },
                                    { label: 'Filing Date', value: selectedCase.filing_date || '—' },
                                    { label: 'Next Hearing', value: selectedCase.next_hearing_date || '—' },
                                    { label: 'Bench', value: selectedCase.bench || '—' },
                                    { label: 'Court Type', value: selectedCase.court_type },
                                ].map((item, i) => (
                                    <div key={i} style={{ padding: '10px 14px', borderBottom: `1px solid ${GOV.border}`, borderRight: i % 2 === 0 ? `1px solid ${GOV.border}` : 'none', background: i % 4 < 2 ? GOV.white : GOV.offWhite }}>
                                        <div style={{ fontSize: '10px', color: GOV.textGrey, textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 700, marginBottom: '3px' }}>{item.label}</div>
                                        <div style={{ fontSize: '13px', color: GOV.textDark, fontWeight: 500 }}>{item.value}</div>
                                    </div>
                                ))}
                            </div>

                            {selectedCase.subject && (
                                <div style={{ marginBottom: '18px', padding: '10px 14px', background: '#fffbeb', borderRadius: '4px', borderLeft: `3px solid ${GOV.gold}` }}>
                                    <div style={{ fontSize: '10px', color: GOV.textGrey, textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 700, marginBottom: '3px' }}>Subject Matter</div>
                                    <div style={{ fontSize: '13px', color: GOV.textDark }}>{selectedCase.subject}</div>
                                </div>
                            )}

                            {selectedCase.hearings && selectedCase.hearings.length > 0 && (
                                <>
                                    <div style={{ fontSize: '12px', fontWeight: 700, color: GOV.navy, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
                                        Hearing History ({selectedCase.hearings.length})
                                    </div>
                                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', border: `1px solid ${GOV.border}` }}>
                                        <thead>
                                            <tr style={{ background: GOV.navy }}>
                                                <th style={{ padding: '8px 12px', textAlign: 'left', color: GOV.white, fontWeight: 700, width: '110px' }}>Date</th>
                                                <th style={{ padding: '8px 12px', textAlign: 'left', color: GOV.white, fontWeight: 700 }}>Order / Proceedings</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {selectedCase.hearings.map((h, i) => (
                                                <tr key={i} style={{ background: i % 2 === 0 ? GOV.white : GOV.offWhite, borderBottom: `1px solid ${GOV.border}` }}>
                                                    <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: GOV.navy, whiteSpace: 'nowrap', borderRight: `1px solid ${GOV.border}` }}>{h.date}</td>
                                                    <td style={{ padding: '8px 12px', color: GOV.textDark }}>{h.order_summary || '—'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* Empty state */}
                {results.length === 0 && !error && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0' }}>
                        <div style={sectionCard}>
                            <div style={{ ...sectionHeader, background: '#2c5282' }}><span>ℹ How to Search</span></div>
                            {[
                                'Enter a case number in the format: WP(C)/1234/2024, CIVIL APPEAL/567/2023, etc.',
                                'You can also search by petitioner or respondent name',
                                'Select the court type filter to narrow results (Supreme Court, High Court, District Court)',
                                'Use Advanced Filters to filter by filing year or case status',
                                'Click any result to view the full case details including hearing history',
                                'Click "Track Case" to receive updates when the case is listed for hearing',
                                'Use "Export CSV" to download all results as a spreadsheet',
                            ].map((step, i) => (
                                <div key={i} style={{ padding: '11px 18px', borderBottom: `1px solid ${GOV.border}`, display: 'flex', gap: '12px', alignItems: 'flex-start', fontSize: '13px', color: GOV.textDark }}>
                                    <span style={{ background: GOV.navy, color: GOV.white, borderRadius: '50%', width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 700, flexShrink: 0 }}>{i + 1}</span>
                                    <span>{step}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
