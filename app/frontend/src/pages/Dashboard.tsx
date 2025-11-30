import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    ArrowRight,
    ArrowUpRight,
    BarChart3,
    Brain,
    Gift,
    RefreshCw,
    Sparkles,
    TrendingUp,
    Upload,
    Zap,
    ChevronRight,
    Target,
    Calendar,
    Activity
} from 'lucide-react';
import { api } from '../lib/api';
import clsx from 'clsx';
import { useDemo } from '../context/DemoContext';
import { SmartInsights, QuickActionCard, LiveActivityIndicator } from '../components/SmartInsights';

type DashboardStats = {
    avg_lift: number;
    profit_opportunity: number;
    active_rules: number;
    top_opportunities: { label: string; value: number | null }[];
};

type HealthStatus = 'checking' | 'ok' | 'offline';

const normalizeStats = (payload: any): DashboardStats => ({
    avg_lift: Number(payload?.avg_lift ?? 0),
    profit_opportunity: Number(payload?.profit_opportunity ?? 0),
    active_rules: Number(payload?.active_rules ?? 0),
    top_opportunities: Array.isArray(payload?.top_opportunities)
        ? payload.top_opportunities.map((item: any, idx: number) => ({
            label: typeof item?.label === 'string' ? item.label : `Opportunity ${idx + 1}`,
            value: item?.value !== undefined && item?.value !== null ? Number(item.value) : null,
        }))
        : [],
});

const formatCurrency = (value: number) =>
    isNaN(value) ? '-' : value >= 10000000 ? `₹${(value / 10000000).toFixed(1)}Cr` : value >= 100000 ? `₹${(value / 100000).toFixed(1)}L` : `₹${value.toLocaleString()}`;

// Animated counter component
function AnimatedNumber({ value, prefix = '', suffix = '', duration = 1000 }: { value: number; prefix?: string; suffix?: string; duration?: number }) {
    const [displayValue, setDisplayValue] = useState(0);
    
    useEffect(() => {
        const startTime = Date.now();
        const startValue = displayValue;
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = startValue + (value - startValue) * eased;
            
            setDisplayValue(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }, [value]);
    
    return <span>{prefix}{displayValue.toFixed(value % 1 === 0 ? 0 : 1)}{suffix}</span>;
}

export function Dashboard() {
    const navigate = useNavigate();
    const { isDemoMode } = useDemo();
    const [health, setHealth] = useState<HealthStatus>('checking');
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [greeting, setGreeting] = useState('');
    const [animationComplete, setAnimationComplete] = useState(false);

    // Set greeting based on time
    useEffect(() => {
        const hour = new Date().getHours();
        if (hour < 12) setGreeting('Good morning');
        else if (hour < 17) setGreeting('Good afternoon');
        else setGreeting('Good evening');
        
        // Trigger entrance animations
        setTimeout(() => setAnimationComplete(true), 100);
    }, []);

    const fetchHealth = async () => {
        if (isDemoMode) {
            setHealth('ok');
            return;
        }
        try {
            const res = await api.get('/api/health', {
                params: { _: Date.now() },
                headers: { 'Cache-Control': 'no-cache' },
            });
            setHealth(res.data.status === 'ok' ? 'ok' : 'offline');
        } catch {
            setHealth('offline');
        }
    };

    const fetchStats = async () => {
        setLoading(true);

        if (isDemoMode) {
            setTimeout(() => {
                setStats({
                    avg_lift: 2.4,
                    profit_opportunity: 45000,
                    active_rules: 12,
                    top_opportunities: [
                        { label: "Atta → Ghee", value: 4200 },
                        { label: "Sweets → Dry Fruits", value: 3800 },
                        { label: "Milk → Bread", value: 1500 }
                    ]
                });
                setLoading(false);
            }, 600);
            return;
        }

        try {
            const res = await api.get('/api/stats', {
                params: { _: Date.now() },
                headers: { 'Cache-Control': 'no-cache' },
            });
            setStats(normalizeStats(res.data));
        } catch {
            setStats(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
        fetchStats();
    }, [isDemoMode]);

    const maxOpportunity = useMemo(() => {
        const values = stats?.top_opportunities?.map((item) => item.value || 0) ?? [];
        return values.length ? Math.max(...values) : 0;
    }, [stats]);

    const hasData = !!stats;
    const hasRecommendations = (stats?.active_rules || 0) > 0;

    return (
        <div className="max-w-4xl mx-auto space-y-8 py-6 px-4">
            {/* Hero Header */}
            <header className={clsx(
                'space-y-4 transition-all duration-700',
                animationComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            )}>
                <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-bold text-text-primary">{greeting}</h1>
                            <LiveActivityIndicator 
                                isActive={health === 'ok'} 
                                label={isDemoMode ? 'Demo Mode' : health === 'ok' ? 'Live' : 'Offline'} 
                            />
                        </div>
                        <p className="text-text-secondary">
                            {hasRecommendations 
                                ? `${stats?.active_rules} actionable patterns ready for review`
                                : 'Discover profitable product bundles using causal AI'
                            }
                        </p>
                    </div>
                    <button
                        onClick={() => { fetchHealth(); fetchStats(); }}
                        disabled={loading}
                        className="p-2.5 rounded-xl border border-border bg-surface text-text-secondary hover:bg-surface-elevated hover:text-text-primary disabled:opacity-50 transition-all hover:scale-105 active:scale-95"
                        title="Refresh data"
                    >
                        <RefreshCw size={16} className={clsx(loading && 'animate-spin')} />
                    </button>
                </div>
            </header>

            {/* Smart Insights Banner */}
            <div className={clsx(
                'transition-all duration-700 delay-100',
                animationComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            )}>
                <SmartInsights 
                    hasData={hasData}
                    hasRecommendations={hasRecommendations}
                    avgLift={stats?.avg_lift}
                    topOpportunity={stats?.top_opportunities?.[0] ? {
                        label: stats.top_opportunities[0].label,
                        value: stats.top_opportunities[0].value || 0
                    } : undefined}
                />
            </div>

            {/* Stats Grid */}
            <div className={clsx(
                'grid grid-cols-1 md:grid-cols-3 gap-4 transition-all duration-700 delay-200',
                animationComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            )}>
                <div className="bg-surface border border-border rounded-2xl p-5 group hover:shadow-md hover:border-primary/20 transition-all cursor-default">
                    <div className="flex items-center justify-between mb-3">
                        <div className="p-2.5 rounded-xl bg-primary/10 group-hover:bg-primary group-hover:text-white transition-colors">
                            <TrendingUp size={18} className="text-primary group-hover:text-white" />
                        </div>
                        <div className="flex items-center gap-1">
                            <span className="text-[10px] font-semibold text-primary uppercase tracking-wider">Avg Lift</span>
                            {stats && stats.avg_lift > 2 && (
                                <ArrowUpRight size={12} className="text-success" />
                            )}
                        </div>
                    </div>
                    <div className="text-2xl font-bold text-text-primary">
                        {stats ? (
                            <AnimatedNumber value={stats.avg_lift} suffix="×" />
                        ) : loading ? (
                            <span className="inline-block w-16 h-8 bg-surface-elevated rounded animate-pulse" />
                        ) : '0×'}
                    </div>
                    <p className="text-xs text-text-muted mt-1">Pattern strength score</p>
                    <p className="text-[10px] text-text-secondary/80 mt-0.5 italic">how strong the link</p>
                </div>

                <div className="bg-surface border border-border rounded-2xl p-5 group hover:shadow-md hover:border-success/20 transition-all cursor-default">
                    <div className="flex items-center justify-between mb-3">
                        <div className="p-2.5 rounded-xl bg-success/10 group-hover:bg-success group-hover:text-white transition-colors">
                            <BarChart3 size={18} className="text-success group-hover:text-white" />
                        </div>
                        <span className="text-[10px] font-semibold text-success uppercase tracking-wider">Monthly</span>
                    </div>
                    <div className="text-2xl font-bold text-text-primary">
                        {stats ? formatCurrency(stats.profit_opportunity) : loading ? (
                            <span className="inline-block w-20 h-8 bg-surface-elevated rounded animate-pulse" />
                        ) : '₹0'}
                    </div>
                    <p className="text-xs text-text-muted mt-1">Profit opportunity</p>
                    <p className="text-[10px] text-text-secondary/80 mt-0.5 italic">estimated monthly gain</p>
                </div>

                <div 
                    className="bg-surface border border-border rounded-2xl p-5 group hover:shadow-md hover:border-accent/20 transition-all cursor-pointer"
                    onClick={() => navigate('/recommendations')}
                >
                    <div className="flex items-center justify-between mb-3">
                        <div className="p-2.5 rounded-xl bg-accent/10 group-hover:bg-accent group-hover:text-white transition-colors">
                            <Zap size={18} className="text-accent group-hover:text-white" />
                        </div>
                        <span className="text-[10px] font-semibold text-accent uppercase tracking-wider">Active</span>
                    </div>
                    <div className="text-2xl font-bold text-text-primary flex items-center gap-2">
                        {stats ? (
                            <>
                                <AnimatedNumber value={stats.active_rules} />
                                <ChevronRight size={16} className="text-text-muted group-hover:text-accent group-hover:translate-x-1 transition-all" />
                            </>
                        ) : loading ? (
                            <span className="inline-block w-12 h-8 bg-surface-elevated rounded animate-pulse" />
                        ) : 0}
                    </div>
                    <p className="text-xs text-text-muted mt-1">Patterns found</p>
                    <p className="text-[10px] text-text-secondary/80 mt-0.5 italic">rules ready to act on</p>
                </div>
            </div>

            {/* Top Opportunities with enhanced visuals */}
            <div className={clsx(
                'bg-surface border border-border rounded-2xl p-6 transition-all duration-700 delay-300',
                animationComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            )}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-success/10">
                            <Target size={16} className="text-success" />
                        </div>
                        <div>
                            <h2 className="text-base font-semibold text-text-primary">Top Opportunities</h2>
                            <p className="text-xs text-text-muted">Highest profit potential bundles <span className="text-text-secondary/80 italic">· ranked by margin</span></p>
                        </div>
                    </div>
                    <Link 
                        to="/recommendations"
                        className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:text-primary-dark hover:gap-2.5 transition-all"
                    >
                        View all <ArrowRight size={12} />
                    </Link>
                </div>

                {loading ? (
                    <div className="py-12 text-center">
                        <div className="relative mx-auto w-12 h-12">
                            <div className="absolute inset-0 rounded-full border-2 border-border" />
                            <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                            <Brain size={20} className="absolute inset-0 m-auto text-primary" />
                        </div>
                        <p className="mt-4 text-text-secondary text-sm">Analyzing patterns...</p>
                    </div>
                ) : stats && stats.top_opportunities.length > 0 ? (
                    <div className="space-y-3">
                        {stats.top_opportunities.map((item, idx) => (
                            <Link 
                                key={item.label + idx} 
                                to="/recommendations"
                                className={clsx(
                                    'group flex items-center gap-4 p-3 rounded-xl transition-all hover:bg-surface-elevated',
                                    idx === 0 && 'bg-success/5 hover:bg-success/10'
                                )}
                                style={{ animationDelay: `${idx * 100}ms` }}
                            >
                                <span className={clsx(
                                    'flex items-center justify-center w-8 h-8 rounded-lg text-xs font-bold shrink-0 transition-all',
                                    idx === 0 ? 'bg-success text-white' :
                                    idx < 3 ? 'bg-primary/10 text-primary' : 
                                    'bg-surface-elevated text-text-muted'
                                )}>
                                    {idx + 1}
                                </span>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1.5">
                                        <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors truncate">
                                            {item.label}
                                        </span>
                                        <span className="text-sm font-bold text-success shrink-0 ml-2">
                                            {item.value !== null ? formatCurrency(item.value) : '-'}
                                        </span>
                                    </div>
                                    <div className="h-1.5 bg-surface-elevated rounded-full overflow-hidden">
                                        <div
                                            className={clsx(
                                                'h-full rounded-full transition-all duration-1000',
                                                idx === 0 ? 'bg-success' : 'bg-primary'
                                            )}
                                            style={{ 
                                                width: `${maxOpportunity ? Math.max((item.value || 0) / maxOpportunity * 100, 8) : 0}%`,
                                                transitionDelay: `${idx * 200}ms`
                                            }}
                                        />
                                    </div>
                                </div>
                                <ChevronRight size={16} className="text-text-muted group-hover:text-primary group-hover:translate-x-1 transition-all shrink-0" />
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className="py-12 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-surface-elevated flex items-center justify-center">
                            <Sparkles size={28} className="text-text-muted" />
                        </div>
                        <p className="text-text-secondary text-sm font-medium">No opportunities found yet</p>
                        <p className="text-text-muted text-xs mt-1 mb-4">Upload your transaction data to discover patterns</p>
                        <Link 
                            to="/upload" 
                            className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl text-sm font-semibold hover:bg-primary-dark transition-colors"
                        >
                            <Upload size={14} />
                            Upload Data
                        </Link>
                    </div>
                )}
            </div>

            {/* Quick Actions - Enhanced */}
            <div className={clsx(
                'grid grid-cols-1 md:grid-cols-2 gap-4 transition-all duration-700 delay-400',
                animationComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            )}>
                <QuickActionCard
                    icon={Upload}
                    title="Upload Data"
                    description="Import CSV or Excel transactions to begin analysis"
                    to="/upload"
                    variant="primary"
                />
                <QuickActionCard
                    icon={Gift}
                    title="View Recommendations"
                    description={hasRecommendations ? `${stats?.active_rules} bundles ready` : 'See AI-powered bundle suggestions'}
                    to="/recommendations"
                    variant="success"
                    badge={hasRecommendations ? 'New' : undefined}
                />
            </div>

            {/* How It Works - For new users */}
            {!hasData && (
                <div className={clsx(
                    'bg-surface border border-border rounded-2xl p-6 transition-all duration-700 delay-500',
                    animationComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                )}>
                    <div className="flex items-center gap-2 mb-4">
                        <Sparkles size={16} className="text-primary" />
                        <h3 className="text-sm font-semibold text-text-primary">How ProfitLift Works</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[
                            { icon: Upload, title: 'Upload', desc: 'Import your transaction data' },
                            { icon: Brain, title: 'Analyze', desc: 'AI finds causal patterns' },
                            { icon: Target, title: 'Act', desc: 'Execute validated bundles' }
                        ].map((step) => (
                            <div key={step.title} className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                    <step.icon size={16} className="text-primary" />
                                </div>
                                <div>
                                    <h4 className="text-sm font-semibold text-text-primary">{step.title}</h4>
                                    <p className="text-xs text-text-muted mt-0.5">{step.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Methodology Badge for MTech presentation */}
            <div className={clsx(
                'flex items-center justify-center gap-4 py-4 transition-all duration-700 delay-600',
                animationComplete ? 'opacity-100' : 'opacity-0'
            )}>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-border group cursor-help" title="Separates cause from chance">
                    <Brain size={12} className="text-primary" />
                    <span className="text-[10px] font-semibold text-text-muted">T-Learner Causal ML</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-border group cursor-help" title="Uses time & festival data">
                    <Calendar size={12} className="text-accent" />
                    <span className="text-[10px] font-semibold text-text-muted">Context-Aware Mining</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-border group cursor-help" title="Updates as data flows in">
                    <Activity size={12} className="text-success" />
                    <span className="text-[10px] font-semibold text-text-muted">Real-time Analysis</span>
                </div>
            </div>
        </div>
    );
}
