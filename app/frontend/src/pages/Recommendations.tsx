import { useEffect, useState } from 'react';
import {
    ArrowRight,
    BarChart3,
    Brain,
    ChevronRight,
    Filter,
    Gift,
    RefreshCw,
    Search,
    TrendingUp,
    Zap
} from 'lucide-react';
import { api } from '../lib/api';
import clsx from 'clsx';
import { useDemo } from '../context/DemoContext';

type RuleResponse = {
    antecedent: string[];
    consequent: string[];
    context: {
        label: string;
        store_id?: string;
        time_bin?: string;
        weekday_weekend?: string;
        quarter?: number;
    };
    support: number;
    confidence: number;
    lift: number;
    profit_score?: number;
    diversity_score?: number;
    overall_score?: number;
    explanation: string;
    uplift?: {
        incremental_attach_rate: number;
        incremental_revenue: number;
        incremental_margin: number;
        control_rate: number;
        treatment_rate: number;
    };
};

type BundleResponse = {
    bundle_id: string;
    anchor_items: string[];
    recommended_items: string[];
    context: {
        label: string;
        store_id?: string;
        time_bin?: string;
        weekday_weekend?: string;
        quarter?: number;
    };
    expected_margin: number;
    expected_attach_rate: number;
    overall_score: number;
    narrative: string;
    confidence: number;
    lift: number;
    uplift?: {
        incremental_attach_rate: number;
        incremental_revenue: number;
        incremental_margin: number;
        control_rate: number;
        treatment_rate: number;
    };
};

const formatCurrency = (value: number) =>
    isNaN(value) ? '-' : value >= 10000000 ? `₹${(value / 10000000).toFixed(1)}Cr` : value >= 100000 ? `₹${(value / 100000).toFixed(1)}L` : `₹${value.toLocaleString()}`;

export function Recommendations() {
    const { isDemoMode } = useDemo();
    const [rules, setRules] = useState<RuleResponse[]>([]);
    const [bundles, setBundles] = useState<BundleResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'rules' | 'bundles'>('bundles');
    const [searchTerm, setSearchTerm] = useState('');

    const fetchData = async () => {
        setLoading(true);
        try {
            const [rulesRes, bundlesRes] = await Promise.all([
                api.get('/api/rules', { params: { _: Date.now() } }),
                api.get('/api/bundles', { params: { _: Date.now() } })
            ]);

            setRules(rulesRes.data || []);
            setBundles(bundlesRes.data || []);
        } catch (error) {
            console.error('Failed to fetch recommendations:', error);
            setRules([]);
            setBundles([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [isDemoMode]);

    const filteredRules = rules.filter(rule =>
        rule.antecedent.some(item => item.toLowerCase().includes(searchTerm.toLowerCase())) ||
        rule.consequent.some(item => item.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const filteredBundles = bundles.filter(bundle =>
        bundle.anchor_items.some(item => item.toLowerCase().includes(searchTerm.toLowerCase())) ||
        bundle.recommended_items.some(item => item.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const renderRules = () => (
        <div className="space-y-4">
            {filteredRules.map((rule, idx) => (
                <div key={idx} className="bg-surface border border-border rounded-2xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="px-2 py-1 bg-primary/10 text-primary text-xs font-medium rounded">
                                    {rule.context.label}
                                </span>
                                <span className="text-sm text-text-muted">
                                    Lift: {rule.lift.toFixed(2)}× • Confidence: {(rule.confidence * 100).toFixed(0)}%
                                </span>
                            </div>
                            <div className="flex items-center gap-2 mb-3">
                                <span className="font-medium text-text-primary">
                                    {rule.antecedent.join(' + ')}
                                </span>
                                <ArrowRight size={16} className="text-primary" />
                                <span className="font-medium text-success">
                                    {rule.consequent.join(' + ')}
                                </span>
                            </div>
                            <p className="text-sm text-text-secondary mb-3">{rule.explanation}</p>
                        </div>
                        <div className="text-right ml-4">
                            {rule.profit_score && (
                                <div className="text-lg font-bold text-success">
                                    +₹{rule.profit_score.toFixed(0)}
                                </div>
                            )}
                            <div className="text-xs text-text-muted">est. profit</div>
                        </div>
                    </div>

                    {rule.uplift && (
                        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
                            <div className="text-center">
                                <div className="text-sm font-medium text-success">
                                    +{(rule.uplift.incremental_attach_rate * 100).toFixed(1)}%
                                </div>
                                <div className="text-xs text-text-muted">attach rate lift</div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm font-medium text-primary">
                                    +₹{rule.uplift.incremental_revenue.toFixed(0)}
                                </div>
                                <div className="text-xs text-text-muted">revenue lift</div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm font-medium text-accent">
                                    +₹{rule.uplift.incremental_margin.toFixed(0)}
                                </div>
                                <div className="text-xs text-text-muted">margin lift</div>
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );

    const renderBundles = () => (
        <div className="space-y-4">
            {filteredBundles.map((bundle, idx) => (
                <div key={bundle.bundle_id} className="bg-surface border border-border rounded-2xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="px-2 py-1 bg-accent/10 text-accent text-xs font-medium rounded">
                                    {bundle.context.label}
                                </span>
                                <span className="text-sm text-text-muted">
                                    Confidence: {(bundle.confidence * 100).toFixed(0)}% • Lift: {bundle.lift.toFixed(2)}×
                                </span>
                            </div>
                            <div className="flex items-center gap-2 mb-3">
                                <span className="font-medium text-text-primary">
                                    {bundle.anchor_items.join(' + ')}
                                </span>
                                <ArrowRight size={16} className="text-accent" />
                                <span className="font-medium text-success">
                                    {bundle.recommended_items.join(' + ')}
                                </span>
                            </div>
                            <p className="text-sm text-text-secondary">{bundle.narrative}</p>
                        </div>
                        <div className="text-right ml-4">
                            <div className="text-lg font-bold text-success">
                                +₹{bundle.expected_margin.toFixed(0)}
                            </div>
                            <div className="text-xs text-text-muted">expected margin</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                        <div className="text-center">
                            <div className="text-sm font-medium text-primary">
                                {(bundle.expected_attach_rate * 100).toFixed(1)}%
                            </div>
                            <div className="text-xs text-text-muted">expected attach rate</div>
                        </div>
                        <div className="text-center">
                            <div className="text-sm font-medium text-accent">
                                {bundle.overall_score.toFixed(2)}
                            </div>
                            <div className="text-xs text-text-muted">overall score</div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    return (
        <div className="max-w-6xl mx-auto space-y-8 py-6 px-4">
            {/* Header */}
            <header className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-text-primary">AI Recommendations</h1>
                        <p className="text-text-secondary mt-1">
                            {activeTab === 'bundles'
                                ? 'Smart bundle suggestions powered by causal AI'
                                : 'Association rules discovered from your transaction data'
                            }
                        </p>
                    </div>
                    <button
                        onClick={fetchData}
                        disabled={loading}
                        className="p-2.5 rounded-xl border border-border bg-surface text-text-secondary hover:bg-surface-elevated hover:text-text-primary disabled:opacity-50 transition-all hover:scale-105 active:scale-95"
                        title="Refresh recommendations"
                    >
                        <RefreshCw size={16} className={clsx(loading && 'animate-spin')} />
                    </button>
                </div>
            </header>

            {/* Search and Filters */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-md">
                    <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-muted" />
                    <input
                        type="text"
                        placeholder="Search products..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 rounded-xl border border-border bg-surface text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    />
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setActiveTab('bundles')}
                        className={clsx(
                            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
                            activeTab === 'bundles'
                                ? 'bg-accent text-white shadow-md'
                                : 'bg-surface border border-border text-text-secondary hover:bg-surface-elevated'
                        )}
                    >
                        <Gift size={14} className="inline mr-2" />
                        Bundles ({bundles.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('rules')}
                        className={clsx(
                            'px-4 py-2 rounded-xl text-sm font-medium transition-all',
                            activeTab === 'rules'
                                ? 'bg-primary text-white shadow-md'
                                : 'bg-surface border border-border text-text-secondary hover:bg-surface-elevated'
                        )}
                    >
                        <Brain size={14} className="inline mr-2" />
                        Rules ({rules.length})
                    </button>
                </div>
            </div>

            {/* Content */}
            {loading ? (
                <div className="py-12 text-center">
                    <div className="relative mx-auto w-12 h-12">
                        <div className="absolute inset-0 rounded-full border-2 border-border" />
                        <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                        <Brain size={20} className="absolute inset-0 m-auto text-primary" />
                    </div>
                    <p className="mt-4 text-text-secondary text-sm">Analyzing patterns...</p>
                </div>
            ) : activeTab === 'bundles' ? (
                filteredBundles.length > 0 ? renderBundles() : (
                    <div className="py-12 text-center">
                        <Gift size={48} className="mx-auto mb-4 text-text-muted" />
                        <p className="text-text-secondary text-lg font-medium">No bundles found</p>
                        <p className="text-text-muted text-sm mt-1">Upload transaction data to generate bundle recommendations</p>
                    </div>
                )
            ) : (
                filteredRules.length > 0 ? renderRules() : (
                    <div className="py-12 text-center">
                        <Brain size={48} className="mx-auto mb-4 text-text-muted" />
                        <p className="text-text-secondary text-lg font-medium">No rules found</p>
                        <p className="text-text-muted text-sm mt-1">Upload transaction data to discover association patterns</p>
                    </div>
                )
            )}
        </div>
    );
}