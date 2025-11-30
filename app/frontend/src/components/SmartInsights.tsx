import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Activity,
    ArrowRight,
    BarChart3,
    Brain,
    Gift,
    RefreshCw,
    Sparkles,
    TrendingUp,
    Upload,
    Zap
} from 'lucide-react';
import clsx from 'clsx';

interface LiveActivityIndicatorProps {
    isActive: boolean;
    label: string;
}

export function LiveActivityIndicator({ isActive, label }: LiveActivityIndicatorProps) {
    return (
        <div className="flex items-center gap-2 text-sm">
            <div className={clsx(
                'w-2 h-2 rounded-full transition-colors',
                isActive ? 'bg-success animate-pulse' : 'bg-text-muted'
            )} />
            <span className={clsx(
                'font-medium',
                isActive ? 'text-success' : 'text-text-muted'
            )}>
                {label}
            </span>
        </div>
    );
}

interface SmartInsightsProps {
    hasData: boolean;
    hasRecommendations: boolean;
    avgLift?: number;
    topOpportunity?: {
        label: string;
        value: number;
    };
}

export function SmartInsights({ hasData, hasRecommendations, avgLift, topOpportunity }: SmartInsightsProps) {
    const [currentInsight, setCurrentInsight] = useState(0);

    const insights = [
        {
            icon: Brain,
            title: "AI-Powered Analysis",
            description: "Context-aware machine learning finds hidden profit opportunities",
            color: "text-primary"
        },
        {
            icon: TrendingUp,
            title: "Causal ML Technology",
            description: "Separates correlation from causation for reliable insights",
            color: "text-accent"
        },
        {
            icon: Zap,
            title: "Real-time Processing",
            description: "Updates as new data flows in, keeping insights current",
            color: "text-success"
        }
    ];

    if (hasData && hasRecommendations) {
        return (
            <div className="bg-gradient-to-r from-primary/5 via-accent/5 to-success/5 border border-primary/10 rounded-2xl p-6 mb-8">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-primary/10">
                        <Sparkles size={20} className="text-primary" />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-text-primary">🎯 Smart Insights Active</h2>
                        <p className="text-sm text-text-secondary">AI has analyzed your data and found profitable opportunities</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {avgLift && (
                        <div className="bg-surface/50 rounded-xl p-4 border border-border/50">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp size={16} className="text-success" />
                                <span className="text-sm font-medium text-text-primary">Average Lift</span>
                            </div>
                            <div className="text-2xl font-bold text-success">{avgLift.toFixed(1)}×</div>
                            <p className="text-xs text-text-muted">Pattern strength score</p>
                        </div>
                    )}

                    {topOpportunity && (
                        <div className="bg-surface/50 rounded-xl p-4 border border-border/50">
                            <div className="flex items-center gap-2 mb-2">
                                <Gift size={16} className="text-accent" />
                                <span className="text-sm font-medium text-text-primary">Top Opportunity</span>
                            </div>
                            <div className="text-lg font-bold text-text-primary truncate">{topOpportunity.label}</div>
                            <p className="text-sm text-success">+₹{topOpportunity.value.toLocaleString()}</p>
                        </div>
                    )}

                    <div className="bg-surface/50 rounded-xl p-4 border border-border/50">
                        <div className="flex items-center gap-2 mb-2">
                            <Activity size={16} className="text-primary" />
                            <span className="text-sm font-medium text-text-primary">Ready to Act</span>
                        </div>
                        <div className="text-lg font-bold text-primary">{hasRecommendations ? 'Yes' : 'No'}</div>
                        <p className="text-xs text-text-muted">Recommendations available</p>
                    </div>
                </div>
            </div>
        );
    }

    // Default insights when no data
    const insight = insights[currentInsight];

    return (
        <div className="bg-gradient-to-r from-primary/5 via-accent/5 to-success/5 border border-primary/10 rounded-2xl p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                        <insight.icon size={20} className={insight.color} />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-text-primary">{insight.title}</h2>
                        <p className="text-sm text-text-secondary">{insight.description}</p>
                    </div>
                </div>
                <button
                    onClick={() => setCurrentInsight((prev) => (prev + 1) % insights.length)}
                    className="p-2 rounded-lg hover:bg-surface/50 transition-colors"
                >
                    <RefreshCw size={16} className="text-text-muted" />
                </button>
            </div>

            {!hasData && (
                <div className="mt-4 p-4 bg-surface/30 rounded-xl border border-border/30">
                    <p className="text-sm text-text-secondary mb-3">
                        💡 <strong>Ready to get started?</strong> Upload your transaction data to unlock AI-powered insights.
                    </p>
                    <Link
                        to="/upload"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
                    >
                        <Upload size={14} />
                        Upload Data
                        <ArrowRight size={14} />
                    </Link>
                </div>
            )}
        </div>
    );
}

interface QuickActionCardProps {
    icon: React.ComponentType<{ size?: number; className?: string }>;
    title: string;
    description: string;
    to: string;
    variant?: 'primary' | 'success' | 'default';
    badge?: string;
}

export function QuickActionCard({ icon: Icon, title, description, to, variant = 'default', badge }: QuickActionCardProps) {
    const variants = {
        primary: 'border-primary/20 hover:border-primary/40 bg-primary/5 hover:bg-primary/10',
        success: 'border-success/20 hover:border-success/40 bg-success/5 hover:bg-success/10',
        default: 'border-border hover:border-border-strong bg-surface hover:bg-surface-elevated'
    };

    return (
        <Link
            to={to}
            className={clsx(
                'group relative block p-4 rounded-xl border transition-all hover:shadow-md',
                variants[variant]
            )}
        >
            <div className="flex items-start gap-3">
                <div className={clsx(
                    'p-2.5 rounded-lg shrink-0 transition-colors',
                    variant === 'primary' ? 'bg-primary/10 group-hover:bg-primary group-hover:text-white' :
                    variant === 'success' ? 'bg-success/10 group-hover:bg-success group-hover:text-white' :
                    'bg-surface-elevated group-hover:bg-primary group-hover:text-white'
                )}>
                    <Icon size={16} className={clsx(
                        variant === 'primary' ? 'text-primary group-hover:text-white' :
                        variant === 'success' ? 'text-success group-hover:text-white' :
                        'text-text-secondary group-hover:text-white'
                    )} />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-text-primary group-hover:text-primary transition-colors">
                            {title}
                        </h3>
                        {badge && (
                            <span className="px-1.5 py-0.5 text-xs font-medium bg-accent/10 text-accent rounded">
                                {badge}
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-text-secondary group-hover:text-text-primary transition-colors">
                        {description}
                    </p>
                </div>
                <ArrowRight size={16} className="text-text-muted group-hover:text-primary group-hover:translate-x-1 transition-all shrink-0 mt-1" />
            </div>
        </Link>
    );
}