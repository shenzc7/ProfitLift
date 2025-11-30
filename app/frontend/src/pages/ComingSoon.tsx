import { Construction, Calendar, BarChart3, Users, ArrowRight, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export function PerformanceTracker() {
    return (
        <div className="max-w-4xl mx-auto space-y-8 py-6 px-4">
            <header className="text-center space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                    <Construction size={14} />
                    Coming Soon
                </div>
                <h1 className="text-3xl font-bold text-text-primary">Performance Tracker</h1>
                <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                    Monitor your bundle performance over time, track ROI, and optimize your merchandising strategy with real-time analytics.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-surface border border-border rounded-2xl p-6 text-center">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-primary/10 flex items-center justify-center">
                        <BarChart3 size={24} className="text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">Real-time Metrics</h3>
                    <p className="text-text-secondary text-sm">
                        Track lift, attach rates, and revenue impact as bundles perform in real-time.
                    </p>
                </div>

                <div className="bg-surface border border-border rounded-2xl p-6 text-center">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-success/10 flex items-center justify-center">
                        <Calendar size={24} className="text-success" />
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">Historical Analysis</h3>
                    <p className="text-text-secondary text-sm">
                        Compare performance across time periods and identify seasonal patterns.
                    </p>
                </div>

                <div className="bg-surface border border-border rounded-2xl p-6 text-center">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-accent/10 flex items-center justify-center">
                        <Users size={24} className="text-accent" />
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">Customer Insights</h3>
                    <p className="text-text-secondary text-sm">
                        Understand customer segments and personalize bundle recommendations.
                    </p>
                </div>
            </div>

            <div className="bg-surface border border-border rounded-2xl p-8 text-center">
                <Clock size={48} className="mx-auto mb-4 text-text-muted" />
                <h2 className="text-xl font-semibold text-text-primary mb-2">Feature in Development</h2>
                <p className="text-text-secondary mb-6">
                    We're building advanced performance tracking capabilities. This feature will be available in the next update.
                </p>
                <Link
                    to="/"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary-dark transition-colors"
                >
                    Return to Dashboard
                    <ArrowRight size={16} />
                </Link>
            </div>
        </div>
    );
}

export function StoreComparison() {
    return (
        <div className="max-w-4xl mx-auto space-y-8 py-6 px-4">
            <header className="text-center space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                    <Construction size={14} />
                    Coming Soon
                </div>
                <h1 className="text-3xl font-bold text-text-primary">Store Comparison</h1>
                <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                    Compare bundle performance across different store locations and identify regional opportunities.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-surface border border-border rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <BarChart3 size={20} className="text-primary" />
                        </div>
                        <h3 className="text-lg font-semibold text-text-primary">Cross-Store Analysis</h3>
                    </div>
                    <p className="text-text-secondary text-sm mb-4">
                        Compare how the same bundles perform across different locations and customer segments.
                    </p>
                    <ul className="space-y-2 text-sm text-text-secondary">
                        <li>• Regional performance metrics</li>
                        <li>• Store-specific optimizations</li>
                        <li>• Customer demographic insights</li>
                    </ul>
                </div>

                <div className="bg-surface border border-border rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                            <Users size={20} className="text-success" />
                        </div>
                        <h3 className="text-lg font-semibold text-text-primary">Location Intelligence</h3>
                    </div>
                    <p className="text-text-secondary text-sm mb-4">
                        Understand how local factors influence bundle performance and customer behavior.
                    </p>
                    <ul className="space-y-2 text-sm text-text-secondary">
                        <li>• Geographic performance patterns</li>
                        <li>• Local market preferences</li>
                        <li>• Seasonal location effects</li>
                    </ul>
                </div>
            </div>

            <div className="bg-surface border border-border rounded-2xl p-8 text-center">
                <Clock size={48} className="mx-auto mb-4 text-text-muted" />
                <h2 className="text-xl font-semibold text-text-primary mb-2">Multi-Store Feature</h2>
                <p className="text-text-secondary mb-6">
                    Advanced store comparison tools are currently in development. Contact us for early access.
                </p>
                <Link
                    to="/"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary-dark transition-colors"
                >
                    Return to Dashboard
                    <ArrowRight size={16} />
                </Link>
            </div>
        </div>
    );
}