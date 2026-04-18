import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface CauseListEntry {
    serial_number: number;
    case_number: string;
    petitioner: string;
    respondent: string;
    court_number?: string;
    bench?: string;
}

interface CauseList {
    court_name: string;
    date: string;
    court_number: string;
    bench: string;
    total_cases: number;
    entries: CauseListEntry[];
}

export default function CauseListPage() {
    const [courtName, setCourtName] = useState('Delhi High Court');
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [causeLists, setCauseLists] = useState<CauseList[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const courts = [
        'Delhi High Court', 'Bombay High Court', 'Madras High Court',
        'Calcutta High Court', 'Karnataka High Court', 'Supreme Court of India',
    ];

    const fetchCauseList = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await fetch(
                `${API_BASE}/causelist/${selectedDate}?court_name=${encodeURIComponent(courtName)}`
            );
            const data = await res.json();
            setCauseLists(data.data || []);
        } catch (err) {
            setError('Failed to fetch cause list');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 min-h-screen bg-slate-950 text-white">
            <h1 className="text-3xl font-bold gradient-text mb-8">Cause List Monitor</h1>

            {/* Filters */}
            <div className="glass-card p-6 mb-8">
                <div className="flex flex-col md:flex-row gap-4 items-end">
                    <div className="flex-1">
                        <label className="block text-sm text-slate-400 mb-1">Court</label>
                        <select
                            value={courtName}
                            onChange={(e) => setCourtName(e.target.value)}
                            className="input-field"
                        >
                            {courts.map((c) => (
                                <option key={c} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Date</label>
                        <input
                            type="date"
                            value={selectedDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                            className="input-field"
                        />
                    </div>
                    <button onClick={fetchCauseList} className="btn-primary" disabled={loading}>
                        {loading ? 'Loading...' : 'Fetch'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="glass-card p-4 mb-6 border-red-500/50 text-red-400">{error}</div>
            )}

            {/* Cause Lists */}
            {causeLists.map((cl, idx) => (
                <div key={idx} className="glass-card mb-6 animate-fade-in" style={{ animationDelay: `${idx * 100}ms` }}>
                    <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                        <div>
                            <h3 className="font-bold text-lg text-white">
                                Court No. {cl.court_number || '—'}
                            </h3>
                            {cl.bench && <p className="text-sm text-slate-400">Bench: {cl.bench}</p>}
                        </div>
                        <span className="badge bg-blue-500/20 text-blue-400">
                            {cl.total_cases} cases
                        </span>
                    </div>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Sr.</th>
                                <th>Case Number</th>
                                <th>Petitioner</th>
                                <th>Respondent</th>
                            </tr>
                        </thead>
                        <tbody>
                            {cl.entries.map((e) => (
                                <tr key={e.serial_number}>
                                    <td className="text-slate-500">{e.serial_number}</td>
                                    <td className="font-mono text-blue-400">{e.case_number}</td>
                                    <td>{e.petitioner}</td>
                                    <td>{e.respondent}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ))}

            {!loading && causeLists.length === 0 && (
                <div className="text-center py-16 text-slate-500">
                    <svg className="w-12 h-12 text-slate-600 mx-auto mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
                    <p>Select a court and date, then click Fetch to view the cause list</p>
                </div>
            )}
        </div>
    );
}
