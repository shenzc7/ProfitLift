import { useState } from 'react';
import {
    Database,
    RefreshCw,
    Trash2,
    Download,
    Upload,
    Moon,
    Sun,
    Monitor,
    Settings as SettingsIcon,
    AlertTriangle,
    CheckCircle
} from 'lucide-react';
import { api } from '../lib/api';
import { useTheme } from '../context/ThemeContext';
import { useDemo } from '../context/DemoContext';
import clsx from 'clsx';

type ClearRequest = {
    clear_rules: boolean;
    clear_bundles: boolean;
    clear_uploads: boolean;
    clear_cache: boolean;
};

type ClearResponse = {
    tables_cleared: string[];
    counts_before: Record<string, number>;
    cache_cleared: boolean;
};

export function SettingsPage() {
    const { theme, toggleTheme } = useTheme();
    const { isDemoMode, toggleDemoMode } = useDemo();
    const [clearing, setClearing] = useState(false);
    const [clearResult, setClearResult] = useState<ClearResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleClearData = async (options: ClearRequest) => {
        setClearing(true);
        setError(null);

        try {
            const response = await api.post('/api/settings/clear', options);
            setClearResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to clear data');
        } finally {
            setClearing(false);
        }
    };

    const getThemeIcon = () => {
        switch (theme) {
            case 'light': return Sun;
            case 'dark': return Moon;
            default: return Monitor;
        }
    };

    const ThemeIcon = getThemeIcon();

    return (
        <div className="max-w-4xl mx-auto space-y-8 py-6 px-4">
            {/* Header */}
            <header className="space-y-4">
                <div className="flex items-center gap-3">
                    <SettingsIcon size={24} className="text-primary" />
                    <h1 className="text-3xl font-bold text-text-primary">Settings</h1>
                </div>
                <p className="text-text-secondary">
                    Manage your application preferences and data
                </p>
            </header>

            {/* Theme Settings */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Appearance</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <ThemeIcon size={20} className="text-primary" />
                            <div>
                                <div className="font-medium text-text-primary">Theme</div>
                                <div className="text-sm text-text-muted">Choose your preferred color scheme</div>
                            </div>
                        </div>
                        <button
                            onClick={toggleTheme}
                            className="px-4 py-2 bg-surface-elevated border border-border rounded-lg text-text-primary hover:bg-surface transition-colors flex items-center gap-2"
                        >
                            <ThemeIcon size={16} />
                            {theme === 'light' ? 'Light' : theme === 'dark' ? 'Dark' : 'System'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Demo Mode */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Development</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Database size={20} className="text-accent" />
                            <div>
                                <div className="font-medium text-text-primary">Demo Mode</div>
                                <div className="text-sm text-text-muted">
                                    Use sample data instead of uploaded data for testing
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={toggleDemoMode}
                            className={clsx(
                                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                                isDemoMode ? 'bg-accent' : 'bg-surface-elevated border border-border'
                            )}
                        >
                            <span
                                className={clsx(
                                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                                    isDemoMode ? 'translate-x-6' : 'translate-x-1'
                                )}
                            />
                        </button>
                    </div>
                </div>
            </div>

            {/* Data Management */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Data Management</h2>

                {clearResult && (
                    <div className="mb-6 p-4 bg-success/5 border border-success/20 rounded-xl">
                        <div className="flex items-center gap-2 mb-2">
                            <CheckCircle size={16} className="text-success" />
                            <span className="font-medium text-success">Data Cleared Successfully</span>
                        </div>
                        <div className="text-sm text-success/80">
                            Cleared tables: {clearResult.tables_cleared.join(', ')}
                        </div>
                        {Object.keys(clearResult.counts_before).length > 0 && (
                            <div className="mt-2 text-xs text-success/60">
                                Previous counts: {Object.entries(clearResult.counts_before)
                                    .map(([table, count]) => `${table}: ${count}`)
                                    .join(', ')}
                            </div>
                        )}
                    </div>
                )}

                {error && (
                    <div className="mb-6 p-4 bg-danger/5 border border-danger/20 rounded-xl">
                        <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle size={16} className="text-danger" />
                            <span className="font-medium text-danger">Error</span>
                        </div>
                        <div className="text-sm text-danger/80">{error}</div>
                    </div>
                )}

                <div className="space-y-4">
                    <div className="p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <div className="font-medium text-text-primary">Clear Analysis Results</div>
                                <div className="text-sm text-text-muted">
                                    Remove generated rules and bundle recommendations
                                </div>
                            </div>
                            <button
                                onClick={() => handleClearData({
                                    clear_rules: true,
                                    clear_bundles: true,
                                    clear_uploads: false,
                                    clear_cache: true
                                })}
                                disabled={clearing}
                                className="px-4 py-2 bg-warning/10 text-warning border border-warning/20 rounded-lg hover:bg-warning/20 transition-colors disabled:opacity-50 flex items-center gap-2"
                            >
                                {clearing ? (
                                    <RefreshCw size={14} className="animate-spin" />
                                ) : (
                                    <RefreshCw size={14} />
                                )}
                                Clear Rules
                            </button>
                        </div>
                    </div>

                    <div className="p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <div className="font-medium text-text-primary">Clear All Data</div>
                                <div className="text-sm text-text-muted">
                                    Remove all uploaded transactions and items (irreversible)
                                </div>
                            </div>
                            <button
                                onClick={() => handleClearData({
                                    clear_rules: true,
                                    clear_bundles: true,
                                    clear_uploads: true,
                                    clear_cache: true
                                })}
                                disabled={clearing}
                                className="px-4 py-2 bg-danger/10 text-danger border border-danger/20 rounded-lg hover:bg-danger/20 transition-colors disabled:opacity-50 flex items-center gap-2"
                            >
                                {clearing ? (
                                    <RefreshCw size={14} className="animate-spin" />
                                ) : (
                                    <Trash2 size={14} />
                                )}
                                Clear All Data
                            </button>
                        </div>
                    </div>

                    <div className="p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="font-medium text-text-primary">Export Data</div>
                                <div className="text-sm text-text-muted">
                                    Download your data for backup or analysis
                                </div>
                            </div>
                            <button
                                disabled
                                className="px-4 py-2 bg-surface border border-border text-text-muted rounded-lg cursor-not-allowed flex items-center gap-2"
                            >
                                <Download size={14} />
                                Export (Coming Soon)
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* System Information */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">System Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-text-secondary">Version</span>
                            <span className="font-medium text-text-primary">ProfitLift v1.0.0</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-text-secondary">Frontend</span>
                            <span className="font-medium text-text-primary">React + Vite</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-text-secondary">Backend</span>
                            <span className="font-medium text-text-primary">FastAPI + SQLite</span>
                        </div>
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-text-secondary">AI Engine</span>
                            <span className="font-medium text-text-primary">T-Learner ML</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-text-secondary">Data Mining</span>
                            <span className="font-medium text-text-primary">FP-Growth + ECLAT</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-text-secondary">Status</span>
                            <span className="font-medium text-success">Operational</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}