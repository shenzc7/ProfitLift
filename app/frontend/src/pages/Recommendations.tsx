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

const safeNumber = (value: unknown): number | undefined => {
    const num = typeof value === 'number'
        ? value
        : typeof value === 'string'
            ? Number(value)
            : NaN;
    return Number.isFinite(num) ? num : undefined;
};

const formatCurrency = (value: unknown) => {
    const num = safeNumber(value);
    if (num === undefined) return '-';
    return num >= 10000000
        ? `₹${(num / 10000000).toFixed(1)}Cr`
        : num >= 100000
            ? `₹${(num / 100000).toFixed(1)}L`
            : `₹${num.toLocaleString()}`;
};

const formatNumber = (value: unknown, digits = 2) => {
    const num = safeNumber(value);
    return num === undefined ? '-' : num.toFixed(digits);
};

const formatPercent = (value: unknown, digits = 0) => {
    const num = safeNumber(value);
    return num === undefined ? '-' : `${(num * 100).toFixed(digits)}%`;
};

const formatLift = (value: unknown) => {
    const num = safeNumber(value);
    return num === undefined ? '-' : `${num.toFixed(2)}×`;
};

const formatList = (items?: string[]) =>
    Array.isArray(items) && items.length > 0 ? items.join(' + ') : 'N/A';

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

            const rulesPayload = Array.isArray(rulesRes.data) ? rulesRes.data : [];
            const bundlesPayload = Array.isArray(bundlesRes.data) ? bundlesRes.data : [];

            setRules(rulesPayload);
            setBundles(bundlesPayload);
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

    const normalizedSearch = searchTerm.toLowerCase();
    const matchesItems = (items?: string[]) =>
        (Array.isArray(items) ? items : []).some(item =>
            typeof item === 'string' && item.toLowerCase().includes(normalizedSearch)
        );

    const filteredRules = rules.filter(rule =>
        matchesItems(rule?.antecedent) || matchesItems(rule?.consequent)
    );

    const filteredBundles = bundles.filter(bundle =>
        matchesItems(bundle?.anchor_items) || matchesItems(bundle?.recommended_items)
    );

    const renderRules = () => (
        <div className="space-y-4">
            {filteredRules.map((rule, idx) => {
                const profitText = formatCurrency(rule.profit_score);
                const attachLift = rule.uplift ? formatPercent(rule.uplift.incremental_attach_rate, 1) : '-';
                const revenueLift = rule.uplift ? formatCurrency(rule.uplift.incremental_revenue) : '-';
                const marginLift = rule.uplift ? formatCurrency(rule.uplift.incremental_margin) : '-';

                return (
                    <div key={idx} className="bg-surface border border-border rounded-2xl p-6 hover:shadow-md transition-all">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="px-2 py-1 bg-primary/10 text-primary text-xs font-medium rounded">
                                        {rule.context?.label ?? 'Overall'}
                                    </span>
                                    <span className="text-sm text-text-muted">
                                        Lift: {formatLift(rule.lift)} • Confidence: {formatPercent(rule.confidence)}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="font-medium text-text-primary">
                                        {formatList(rule.antecedent)}
                                    </span>
                                    <ArrowRight size={16} className="text-primary" />
                                    <span className="font-medium text-success">
                                        {formatList(rule.consequent)}
                                    </span>
                                </div>
                                <p className="text-sm text-text-secondary mb-3">{rule.explanation || 'No explanation available.'}</p>
                            </div>
                            <div className="text-right ml-4">
                                {profitText !== '-' && (
                                    <div className="text-lg font-bold text-success">
                                        +{profitText}
                                    </div>
                                )}
                                <div className="text-xs text-text-muted">est. profit</div>
                            </div>
                        </div>

                        {rule.uplift && (
                            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
                                <div className="text-center">
                                    <div className="text-sm font-medium text-success">
                                        {attachLift === '-' ? attachLift : `+${attachLift}`}
                                    </div>
                                    <div className="text-xs text-text-muted">attach rate lift</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-sm font-medium text-primary">
                                        {revenueLift === '-' ? revenueLift : `+${revenueLift}`}
                                    </div>
                                    <div className="text-xs text-text-muted">revenue lift</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-sm font-medium text-accent">
                                        {marginLift === '-' ? marginLift : `+${marginLift}`}
                                    </div>
                                    <div className="text-xs text-text-muted">margin lift</div>
                                </div>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );

    const renderBundles = () => (
        <div className="space-y-4">
            {filteredBundles.map((bundle, idx) => {
                const expectedMargin = formatCurrency(bundle.expected_margin);
                const expectedAttach = formatPercent(bundle.expected_attach_rate, 1);
                const overallScore = formatNumber(bundle.overall_score, 2);

                return (
                    <div key={bundle.bundle_id || idx} className="bg-surface border border-border rounded-2xl p-6 hover:shadow-md transition-all">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="px-2 py-1 bg-accent/10 text-accent text-xs font-medium rounded">
                                        {bundle.context?.label ?? 'Overall'}
                                    </span>
                                    <span className="text-sm text-text-muted">
                                        Confidence: {formatPercent(bundle.confidence)} • Lift: {formatLift(bundle.lift)}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="font-medium text-text-primary">
                                        {formatList(bundle.anchor_items)}
                                    </span>
                                    <ArrowRight size={16} className="text-accent" />
                                    <span className="font-medium text-success">
                                        {formatList(bundle.recommended_items)}
                                    </span>
                                </div>
                                <p className="text-sm text-text-secondary">{bundle.narrative || 'No narrative available.'}</p>
                            </div>
                            <div className="text-right ml-4">
                                <div className="text-lg font-bold text-success">
                                    {expectedMargin === '-' ? expectedMargin : `+${expectedMargin}`}
                                </div>
                                <div className="text-xs text-text-muted">expected margin</div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                            <div className="text-center">
                                <div className="text-sm font-medium text-primary">
                                    {expectedAttach}
                                </div>
                                <div className="text-xs text-text-muted">expected attach rate</div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm font-medium text-accent">
                                    {overallScore}
                                </div>
                                <div className="text-xs text-text-muted">overall score</div>
                            </div>
                        </div>
                    </div>
                );
            })}
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
