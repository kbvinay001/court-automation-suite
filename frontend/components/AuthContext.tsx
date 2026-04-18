import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface AuthUser {
    email: string;
    full_name: string;
    role: string;
}

interface AuthState {
    user: AuthUser | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
    register: (data: RegisterData) => Promise<{ success: boolean; error?: string }>;
    logout: () => void;
    getAuthHeaders: () => Record<string, string>;
}

interface RegisterData {
    email: string;
    full_name: string;
    password: string;
    phone?: string;
    role?: string;
    bar_council_id?: string;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Restore session from localStorage on mount
    useEffect(() => {
        const savedToken = localStorage.getItem('court_auth_token');
        const savedUser = localStorage.getItem('court_auth_user');
        if (savedToken && savedUser) {
            try {
                setToken(savedToken);
                setUser(JSON.parse(savedUser));
            } catch {
                localStorage.removeItem('court_auth_token');
                localStorage.removeItem('court_auth_user');
            }
        }
        setIsLoading(false);
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await res.json();
            if (res.ok && data.success) {
                const { access_token, user: userData } = data.data;
                setToken(access_token);
                setUser(userData);
                localStorage.setItem('court_auth_token', access_token);
                localStorage.setItem('court_auth_user', JSON.stringify(userData));
                return { success: true };
            }
            return { success: false, error: data.detail || 'Login failed' };
        } catch (err) {
            return { success: false, error: 'Network error. Is the backend running?' };
        }
    }, []);

    const register = useCallback(async (regData: RegisterData) => {
        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(regData),
            });
            const data = await res.json();
            if (res.ok && data.success) {
                const { access_token, user: userData } = data.data;
                setToken(access_token);
                setUser(userData);
                localStorage.setItem('court_auth_token', access_token);
                localStorage.setItem('court_auth_user', JSON.stringify(userData));
                return { success: true };
            }
            return { success: false, error: data.detail || 'Registration failed' };
        } catch (err) {
            return { success: false, error: 'Network error. Is the backend running?' };
        }
    }, []);

    const logout = useCallback(() => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('court_auth_token');
        localStorage.removeItem('court_auth_user');
    }, []);

    const getAuthHeaders = useCallback(() => {
        return token ? { Authorization: `Bearer ${token}` } : {};
    }, [token]);

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                isAuthenticated: !!token && !!user,
                isLoading,
                login,
                register,
                logout,
                getAuthHeaders,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthState {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
