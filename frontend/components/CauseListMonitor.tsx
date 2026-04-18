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
    width: '100%',
    boxSizing: 'border-box',
};

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '11px',
    fontWeight: 700,
    color: GOV.textDark,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    marginBottom: '5px',
};

// All 25 High Courts + Supreme Court of India
const ALL_COURTS = [
    { label: '── Supreme Court ──', value: '', disabled: true },
    { label: 'Supreme Court of India', value: 'Supreme Court of India', disabled: false },
    { label: '── High Courts (A–G) ──', value: '', disabled: true },
    { label: 'Allahabad High Court', value: 'Allahabad High Court', disabled: false },
    { label: 'Andhra Pradesh High Court', value: 'Andhra Pradesh High Court', disabled: false },
    { label: 'Bombay High Court', value: 'Bombay High Court', disabled: false },
    { label: 'Calcutta High Court', value: 'Calcutta High Court', disabled: false },
    { label: 'Chhattisgarh High Court', value: 'Chhattisgarh High Court', disabled: false },
    { label: 'Delhi High Court', value: 'Delhi High Court', disabled: false },
    { label: 'Gauhati High Court', value: 'Gauhati High Court', disabled: false },
    { label: 'Gujarat High Court', value: 'Gujarat High Court', disabled: false },
    { label: '── High Courts (H–M) ──', value: '', disabled: true },
    { label: 'Himachal Pradesh High Court', value: 'Himachal Pradesh High Court', disabled: false },
    { label: 'Jammu & Kashmir and Ladakh High Court', value: 'Jammu & Kashmir and Ladakh High Court', disabled: false },
    { label: 'Jharkhand High Court', value: 'Jharkhand High Court', disabled: false },
    { label: 'Karnataka High Court', value: 'Karnataka High Court', disabled: false },
    { label: 'Kerala High Court', value: 'Kerala High Court', disabled: false },
    { label: 'Madhya Pradesh High Court', value: 'Madhya Pradesh High Court', disabled: false },
    { label: 'Madras High Court', value: 'Madras High Court', disabled: false },
    { label: 'Manipur High Court', value: 'Manipur High Court', disabled: false },
    { label: 'Meghalaya High Court', value: 'Meghalaya High Court', disabled: false },
    { label: '── High Courts (O–T) ──', value: '', disabled: true },
    { label: 'Orissa High Court', value: 'Orissa High Court', disabled: false },
    { label: 'Patna High Court', value: 'Patna High Court', disabled: false },
    { label: 'Punjab & Haryana High Court', value: 'Punjab & Haryana High Court', disabled: false },
    { label: 'Rajasthan High Court', value: 'Rajasthan High Court', disabled: false },
    { label: 'Sikkim High Court', value: 'Sikkim High Court', disabled: false },
    { label: 'Telangana High Court', value: 'Telangana High Court', disabled: false },
    { label: 'Tripura High Court', value: 'Tripura High Court', disabled: false },
    { label: 'Uttarakhand High Court', value: 'Uttarakhand High Court', disabled: false },
];

const SELECTABLE_COURTS = ALL_COURTS.filter(c => !c.disabled).map(c => c.value);

interface CauseListEntry { serial_number: number; case_number: string; petitioner: string; respondent: string; advocate?: string; }
interface CauseList { court_name: string; date: string; court_number: string; bench: string; total_cases: number; entries: CauseListEntry[]; }

export default function CauseListMonitor() {
    const [courtName, setCourtName] = useState('Delhi High Court');
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [searchCase, setSearchCase] = useState('');
    const [caseType, setCaseType] = useState<'Civil' | 'Criminal'>('Civil');
    const [causeLists, setCauseLists] = useState<CauseList[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [fetched, setFetched] = useState(false);

    const fetchCauseList = async () => {
        if (!courtName) { setError('Please select a court.'); return; }
        setLoading(true); setError(''); setFetched(false);
        try {
            const isToday = selectedDate === new Date().toISOString().split('T')[0];
            const endpoint = isToday
                ? `${API_BASE}/causelist/today?court_name=${encodeURIComponent(courtName)}&case_type=${caseType.toLowerCase()}`
                : `${API_BASE}/causelist/${selectedDate}?court_name=${encodeURIComponent(courtName)}&case_type=${caseType.toLowerCase()}`;
            const res = await fetch(endpoint);
            const data = await res.json();
            setCauseLists(data.data || []);
            setFetched(true);
            if (!data.data?.length) setError(`No ${caseType} cause list found for ${courtName} on ${selectedDate}.`);
        } catch { setError('Failed to fetch cause list. Please try again.'); }
        finally { setLoading(false); }
    };

    const searchInCauseList = async () => {
        if (!searchCase.trim()) { setError('Please enter a case number to search.'); return; }
        setLoading(true); setError(''); setFetched(false);
        try {
            const res = await fetch(`${API_BASE}/causelist/search?case_number=${encodeURIComponent(searchCase)}&court_name=${encodeURIComponent(courtName)}`);
            const data = await res.json();
            setCauseLists(data.data || []);
            setFetched(true);
        } catch { setError('Search failed.'); }
        finally { setLoading(false); }
    };

    const totalEntries = causeLists.reduce((s, cl) => s + cl.total_cases, 0);

    const formatDate = (d: string) => {
        const [y, m, day] = d.split('-');
        return `${day}-${m}-${y}`;
    };

    return (
        <div style={{ fontFamily: '"Segoe UI", system-ui, sans-serif' }}>

            {/* Page Title */}
            <div style={{ marginBottom: '18px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 800, color: GOV.navy, margin: '0 0 4px 0' }}>Cause List Monitor</h2>
                <p style={{ fontSize: '13px', color: GOV.textGrey, margin: 0 }}>
                    View daily court cause lists for Supreme Court of India and all 25 High Courts
                </p>
            </div>

            {/* Notice Banner */}
            <div style={{ background: '#eef4ff', border: `1px solid #b8d0f5`, borderRadius: '4px', padding: '8px 16px', marginBottom: '16px', fontSize: '12px', color: '#1a3a6b' }}>
                ℹ Cause list displayed may differ from the actual cause list. For further queries, contact the court administrator.
            </div>

            {/* Main Filter Card */}
            <div style={sectionCard}>
                <div style={sectionHeader}>
                    <span>📋 Cause List Search</span>
                    <span style={{ fontSize: '11px', fontStyle: 'italic', color: '#a8c0e0', fontWeight: 400 }}>
                        Covering all 25 High Courts + Supreme Court of India
                    </span>
                </div>
                <div style={{ padding: '20px' }}>

                    {/* Row 1: Court + Date */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '16px' }}>
                        <div>
                            <label style={labelStyle}>
                                <span style={{ color: GOV.red }}>* </span>Court Name
                            </label>
                            <select value={courtName} onChange={e => setCourtName(e.target.value)} style={inputStyle}>
                                <option value="">— Select Court —</option>
                                {ALL_COURTS.map((c, i) =>
                                    c.disabled
                                        ? <option key={i} value="" disabled style={{ color: '#888', fontStyle: 'italic' }}>{c.label}</option>
                                        : <option key={i} value={c.value}>{c.label}</option>
                                )}
                            </select>
                        </div>
                        <div>
                            <label style={labelStyle}>
                                <span style={{ color: GOV.red }}>* </span>Cause List Date
                            </label>
                            <input
                                type="date"
                                value={selectedDate}
                                onChange={e => setSelectedDate(e.target.value)}
                                style={inputStyle}
                            />
                        </div>
                    </div>

                    {/* Row 2: Search case + Civil/Criminal */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '20px', marginBottom: '20px', alignItems: 'end' }}>
                        <div>
                            <label style={labelStyle}>Search by Case Number</label>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <input
                                    type="text"
                                    value={searchCase}
                                    onChange={e => setSearchCase(e.target.value)}
                                    placeholder="e.g. WP(C)/1234/2024"
                                    style={{ ...inputStyle, flex: 1 }}
                                    onKeyDown={e => e.key === 'Enter' && searchInCauseList()}
                                />
                                <button
                                    onClick={searchInCauseList}
                                    disabled={loading}
                                    title="Search case in cause list"
                                    style={{ background: GOV.white, color: GOV.navy, border: `2px solid ${GOV.navy}`, borderRadius: '4px', padding: '8px 14px', fontSize: '13px', fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', whiteSpace: 'nowrap' }}
                                    onMouseEnter={e => { e.currentTarget.style.background = GOV.offWhite; }}
                                    onMouseLeave={e => { e.currentTarget.style.background = GOV.white; }}
                                >
                                    🔍 Search
                                </button>
                            </div>
                        </div>
                        <div>
                            <label style={labelStyle}>Case Type</label>
                            <div style={{ display: 'flex', borderRadius: '4px', overflow: 'hidden', border: `2px solid ${GOV.navy}` }}>
                                {(['Civil', 'Criminal'] as const).map(t => (
                                    <button
                                        key={t}
                                        onClick={() => setCaseType(t)}
                                        style={{
                                            background: caseType === t ? GOV.navy : GOV.white,
                                            color: caseType === t ? GOV.white : GOV.navy,
                                            border: 'none',
                                            padding: '8px 24px',
                                            fontSize: '13px',
                                            fontWeight: 700,
                                            cursor: 'pointer',
                                            fontFamily: 'inherit',
                                            transition: 'all 0.15s',
                                            flex: 1,
                                        }}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Fetch Button */}
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <button
                            onClick={fetchCauseList}
                            disabled={loading}
                            style={{
                                background: GOV.navy, color: GOV.white, border: 'none', borderRadius: '4px',
                                padding: '10px 32px', fontSize: '14px', fontWeight: 700, cursor: 'pointer',
                                fontFamily: 'inherit', opacity: loading ? 0.7 : 1, letterSpacing: '0.3px',
                            }}
                            onMouseEnter={e => (e.currentTarget.style.background = GOV.navyDark)}
                            onMouseLeave={e => (e.currentTarget.style.background = GOV.navy)}
                        >
                            {loading ? '⏳ Fetching…' : `📋 Fetch ${caseType} Cause List`}
                        </button>
                        {fetched && (
                            <button
                                onClick={() => { setCauseLists([]); setFetched(false); setError(''); }}
                                style={{ background: GOV.white, color: GOV.textGrey, border: `1px solid ${GOV.border}`, borderRadius: '4px', padding: '10px 20px', fontSize: '13px', cursor: 'pointer', fontFamily: 'inherit' }}
                            >
                                🔄 Clear
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {error && (
                <div style={{ background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px', padding: '10px 16px', marginBottom: '16px', color: '#856404', fontSize: '13px' }}>
                    ⚠ {error}
                </div>
            )}

            {/* Summary Bar */}
            {causeLists.length > 0 && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '20px' }}>
                    {[
                        { label: 'Court', value: courtName.replace(' High Court', ' HC').replace('Supreme Court of India', 'SC'), accent: GOV.navy },
                        { label: 'Date', value: formatDate(selectedDate), accent: '#5e4fcb' },
                        { label: 'Benches Listed', value: causeLists.length, accent: '#2d7d46' },
                        { label: `Total ${caseType} Cases`, value: totalEntries, accent: '#b86e00' },
                    ].map((s, i) => (
                        <div key={i} style={{ background: GOV.white, border: `1px solid ${GOV.border}`, borderTop: `4px solid ${s.accent}`, borderRadius: '6px', padding: '12px 16px' }}>
                            <div style={{ fontSize: '10px', color: GOV.textGrey, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{s.label}</div>
                            <div style={{ fontSize: '16px', fontWeight: 800, color: s.accent, wordBreak: 'break-word' }}>{s.value}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* Cause List Tables */}
            {causeLists.map((cl, idx) => (
                <div key={idx} style={sectionCard}>
                    <div style={{ ...sectionHeader, background: GOV.navy }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1px' }}>
                            <span>Court No. {cl.court_number || idx + 1} — {cl.court_name}</span>
                            {cl.bench && <span style={{ fontSize: '11px', fontWeight: 400, color: '#a8c0e0' }}>Bench: {cl.bench}</span>}
                        </div>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <span style={{ background: caseType === 'Civil' ? '#e0f0ff' : '#ffe0e0', color: caseType === 'Civil' ? '#004085' : '#7d0000', fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '3px' }}>{caseType}</span>
                            <span style={{ background: GOV.gold, color: GOV.navy, fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '12px' }}>
                                {cl.total_cases} cases
                            </span>
                        </div>
                    </div>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                        <thead>
                            <tr style={{ background: '#eef2f8' }}>
                                {['Sr. No.', 'Case Number', 'Petitioner', 'Respondent', 'Advocate'].map(h => (
                                    <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 700, color: GOV.navy, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.4px', borderBottom: `1px solid ${GOV.border}`, borderRight: `1px solid ${GOV.border}` }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {cl.entries.map((e, i) => (
                                <tr key={e.serial_number} style={{ background: i % 2 === 0 ? GOV.white : '#fafcff', borderBottom: `1px solid ${GOV.border}` }}>
                                    <td style={{ padding: '8px 12px', color: GOV.textGrey, width: '52px', textAlign: 'center', borderRight: `1px solid ${GOV.border}` }}>{e.serial_number}</td>
                                    <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontWeight: 700, color: GOV.navy, borderRight: `1px solid ${GOV.border}`, whiteSpace: 'nowrap' }}>{e.case_number}</td>
                                    <td style={{ padding: '8px 12px', color: GOV.textDark, borderRight: `1px solid ${GOV.border}` }}>{e.petitioner}</td>
                                    <td style={{ padding: '8px 12px', color: GOV.textGrey, borderRight: `1px solid ${GOV.border}` }}>{e.respondent}</td>
                                    <td style={{ padding: '8px 12px', color: GOV.textGrey, fontSize: '12px' }}>{e.advocate || '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ))}

            {/* Empty State */}
            {!loading && !fetched && causeLists.length === 0 && !error && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0' }}>
                    {/* How To Section */}
                    <div style={sectionCard}>
                        <div style={{ ...sectionHeader, background: '#2c5282' }}>
                            <span>ℹ How to Use Cause List Monitor</span>
                        </div>
                        <div style={{ padding: '0' }}>
                            {[
                                'Select the Court Name from the dropdown (Supreme Court of India or any of the 25 High Courts)',
                                'Select the Cause List Date using the date picker — defaults to today\'s date',
                                'Choose the case type: Civil or Criminal',
                                'Click "Fetch Cause List" to retrieve all listed cases for that court and date',
                                'To find a specific case, enter the case number and click the 🔍 Search button',
                                'Case numbers appear in the format: WP(C)/1234/2024 or CRL.A/456/2023',
                            ].map((step, i) => (
                                <div key={i} style={{ padding: '12px 18px', borderBottom: `1px solid ${GOV.border}`, display: 'flex', gap: '12px', alignItems: 'flex-start', fontSize: '13px', color: GOV.textDark }}>
                                    <span style={{ background: GOV.navy, color: GOV.white, borderRadius: '50%', width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 700, flexShrink: 0 }}>{i + 1}</span>
                                    <span>{step}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Court Coverage */}
                    <div style={sectionCard}>
                        <div style={sectionHeader}><span>🏛 Covered Courts</span></div>
                        <div style={{ padding: '16px 18px' }}>
                            <div style={{ marginBottom: '12px' }}>
                                <span style={{ background: GOV.navy, color: GOV.white, fontSize: '11px', fontWeight: 700, padding: '3px 12px', borderRadius: '3px', display: 'inline-block', marginBottom: '10px' }}>Supreme Court of India</span>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
                                {SELECTABLE_COURTS.filter(c => c !== 'Supreme Court of India').map((c, i) => (
                                    <div
                                        key={i}
                                        onClick={() => setCourtName(c)}
                                        style={{ padding: '7px 12px', border: `1px solid ${GOV.border}`, borderRadius: '4px', fontSize: '12px', color: GOV.navy, cursor: 'pointer', background: courtName === c ? '#eef4ff' : GOV.white, fontWeight: courtName === c ? 700 : 400, borderLeft: courtName === c ? `3px solid ${GOV.navy}` : `1px solid ${GOV.border}`, transition: 'all 0.15s' }}
                                        onMouseEnter={e => { if (courtName !== c) e.currentTarget.style.background = GOV.offWhite; }}
                                        onMouseLeave={e => { if (courtName !== c) e.currentTarget.style.background = GOV.white; }}
                                    >
                                        {c}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
