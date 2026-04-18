import React, { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface CaseResult {
    case_number: string;
    court_name: string;
    petitioner: string;
    respondent: string;
    status: string;
    next_hearing_date: string;
    filing_date: string;
}

export default function CasesPage() {
    const [query, setQuery] = useState('');
    const [courtType, setCourtType] = useState('high_court');
    const [results, setResults] = useState<CaseResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError('');
        try {
            const res = await fetch(
                `${API_BASE}/scraper/search?query=${encodeURIComponent(query)}&court_type=${courtType}`
            );
            const data = await res.json();
            setResults(data.data || []);
        } catch (err) {
            setError('Failed to search. Please check the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const statusBadge = (status: string) => {
        const classes: Record<string, string> = {
            pending: 'badge-pending',
            disposed: 'badge-disposed',
            listed: 'badge-listed',
        };
        return (
            <span className={classes[status] || 'badge bg-slate-600 text-slate-300'}>
                {status}
            </span>
        );
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 min-h-screen bg-slate-950 text-white">
            <h1 className="text-3xl font-bold gradient-text mb-8">Case Search</h1>

            <form onSubmit={handleSearch} className="glass-card p-6 mb-8">
                <div className="flex flex-col md:flex-row gap-4">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search by case number or party name..."
                        className="input-field flex-1"
                    />
                    <select
                        value={courtType}
                        onChange={(e) => setCourtType(e.target.value)}
                        className="input-field md:w-48"
                    >
                        <option value="high_court">High Court</option>
                        <option value="district_court">District Court</option>
                        <option value="supreme_court">Supreme Court</option>
                    </select>
                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
            </form>

            {error && (
                <div className="glass-card p-4 mb-6 border-red-500/50 text-red-400">
                    {error}
                </div>
            )}

            {results.length > 0 && (
                <div className="glass-card overflow-hidden">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Case Number</th>
                                <th>Petitioner vs Respondent</th>
                                <th>Court</th>
                                <th>Status</th>
                                <th>Next Hearing</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results.map((c, i) => (
                                <tr key={i} className="animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
                                    <td className="font-mono text-blue-400">{c.case_number}</td>
                                    <td>
                                        <span className="text-white">{c.petitioner}</span>
                                        <span className="text-slate-500 mx-1">vs</span>
                                        <span className="text-slate-300">{c.respondent}</span>
                                    </td>
                                    <td className="text-slate-400">{c.court_name}</td>
                                    <td>{statusBadge(c.status)}</td>
                                    <td className="text-slate-300">{c.next_hearing_date || '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {!loading && results.length === 0 && query && (
                <div className="text-center py-12 text-slate-500">
                    No cases found for "{query}"
                </div>
            )}
        </div>
    );
}
