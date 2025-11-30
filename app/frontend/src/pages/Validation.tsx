import { useEffect, useState } from 'react';
import {
    CheckCircle,
    AlertTriangle,
    Database,
    RefreshCw,
    TrendingUp,
    Users,
    ShoppingCart,
    Calendar
} from 'lucide-react';
import { api } from '../lib/api';
import clsx from 'clsx';

type ValidationStats = {
    db_path: string;
    table_counts: Record<string, number>;
    cache_entries: number;
    last_ingest_at: string | null;
    api_version: string;
};

export function Validation() {
    const [stats, setStats] = useState<ValidationStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchStats = async () => {
        try {
            const response = await api.get('/api/settings/overview');
            setStats(response.data);
        } catch (error) {
            console.error('Failed to fetch validation stats:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchStats();
    };

    const formatTimestamp = (timestamp: string | null) => {
        if (!timestamp) return 'Never';
        return new Date(timestamp).toLocaleString();
    };

    const getHealthStatus = () => {
        if (!stats) return { status: 'unknown', color: 'text-text-muted' };

        const totalRecords = Object.values(stats.table_counts).reduce((sum, count) => sum + count, 0);

        if (totalRecords === 0) {
            return { status: 'empty', color: 'text-warning' };
        }

        if (stats.last_ingest_at) {
            const daysSinceLastIngest = (Date.now() - new Date(stats.last_ingest_at).getTime()) / (1000 * 60 * 60 * 24);
            if (daysSinceLastIngest > 7) {
                return { status: 'stale', color: 'text-warning' };
            }
        }

        return { status: 'healthy', color: 'text-success' };
    };

    const health = getHealthStatus();

    return (
        <div className="max-w-6xl mx-auto space-y-8 py-6 px-4">
            {/* Header */}
            <header className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-text-primary">Data Validation</h1>
                        <p className="text-text-secondary mt-1">
                            Monitor your data pipeline health and system status
                        </p>
                    </div>
                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="p-2.5 rounded-xl border border-border bg-surface text-text-secondary hover:bg-surface-elevated hover:text-text-primary disabled:opacity-50 transition-all hover:scale-105 active:scale-95"
                        title="Refresh validation data"
                    >
                        <RefreshCw size={16} className={clsx(refreshing && 'animate-spin')} />
                    </button>
                </div>
            </header>

            {/* Health Status */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className={clsx(
                        'w-3 h-3 rounded-full',
                        health.status === 'healthy' ? 'bg-success' :
                        health.status === 'stale' ? 'bg-warning' :
                        health.status === 'empty' ? 'bg-danger' : 'bg-text-muted'
                    )} />
                    <h2 className="text-xl font-semibold text-text-primary">System Health</h2>
                    <span className={clsx(
                        'px-2 py-1 text-xs font-medium rounded-full',
                        health.color === 'text-success' ? 'bg-success/10 text-success' :
                        health.color === 'text-warning' ? 'bg-warning/10 text-warning' :
                        health.color === 'text-danger' ? 'bg-danger/10 text-danger' :
                        'bg-surface-elevated text-text-muted'
                    )}>
                        {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
                    </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-primary/10 flex items-center justify-center">
                            <Database size={20} className="text-primary" />
                        </div>
                        <div className="text-2xl font-bold text-text-primary">
                            {stats ? Object.values(stats.table_counts).reduce((sum, count) => sum + count, 0).toLocaleString() : '0'}
                        </div>
                        <div className="text-sm text-text-muted">Total Records</div>
                    </div>

                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-success/10 flex items-center justify-center">
                            <Users size={20} className="text-success" />
                        </div>
                        <div className="text-2xl font-bold text-text-primary">
                            {stats?.table_counts?.transactions || 0}
                        </div>
                        <div className="text-sm text-text-muted">Transactions</div>
                    </div>

                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-accent/10 flex items-center justify-center">
                            <ShoppingCart size={20} className="text-accent" />
                        </div>
                        <div className="text-2xl font-bold text-text-primary">
                            {stats?.table_counts?.items || 0}
                        </div>
                        <div className="text-sm text-text-muted">Items</div>
                    </div>

                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-warning/10 flex items-center justify-center">
                            <TrendingUp size={20} className="text-warning" />
                        </div>
                        <div className="text-2xl font-bold text-text-primary">
                            {stats?.table_counts?.association_rules || 0}
                        </div>
                        <div className="text-sm text-text-muted">Rules Found</div>
                    </div>
                </div>
            </div>

            {/* Database Tables */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Database Tables</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {stats && Object.entries(stats.table_counts).map(([table, count]) => (
                        <div key={table} className="flex items-center justify-between p-4 bg-surface-elevated rounded-xl">
                            <div className="flex items-center gap-3">
                                <Database size={16} className="text-primary" />
                                <span className="font-medium text-text-primary capitalize">
                                    {table.replace(/_/g, ' ')}
                                </span>
                            </div>
                            <div className="text-right">
                                <div className="text-lg font-bold text-text-primary">{count.toLocaleString()}</div>
                                <div className="text-xs text-text-muted">records</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Data Pipeline Status */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Data Pipeline Status</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center gap-3">
                            <Calendar size={16} className="text-primary" />
                            <div>
                                <div className="font-medium text-text-primary">Last Data Ingestion</div>
                                <div className="text-sm text-text-muted">When data was last processed</div>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm font-medium text-text-primary">
                                {formatTimestamp(stats?.last_ingest_at || null)}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center gap-3">
                            <CheckCircle size={16} className="text-success" />
                            <div>
                                <div className="font-medium text-text-primary">API Version</div>
                                <div className="text-sm text-text-muted">Current backend version</div>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm font-medium text-text-primary">
                                {stats?.api_version || 'Unknown'}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center gap-3">
                            <Database size={16} className="text-primary" />
                            <div>
                                <div className="font-medium text-text-primary">Database Path</div>
                                <div className="text-sm text-text-muted">SQLite database location</div>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-xs font-mono text-text-primary max-w-xs truncate">
                                {stats?.db_path || 'Unknown'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                        onClick={() => window.location.reload()}
                        className="p-4 bg-surface-elevated hover:bg-surface rounded-xl text-left transition-colors group"
                    >
                        <div className="flex items-center gap-3">
                            <RefreshCw size={16} className="text-primary group-hover:rotate-180 transition-transform" />
                            <div>
                                <div className="font-medium text-text-primary">Refresh Dashboard</div>
                                <div className="text-sm text-text-muted">Reload all data and metrics</div>
                            </div>
                        </div>
                    </button>

                    <div className="p-4 bg-surface-elevated rounded-xl">
                        <div className="flex items-center gap-3">
                            <AlertTriangle size={16} className="text-warning" />
                            <div>
                                <div className="font-medium text-text-primary">Data Quality Check</div>
                                <div className="text-sm text-text-muted">Automated validation coming soon</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}