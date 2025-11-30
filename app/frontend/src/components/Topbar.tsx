import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Upload, Gift, ShieldCheck, Settings, Database, Brain, Activity, Store } from 'lucide-react';
import clsx from 'clsx';
import { useDemo } from '../context/DemoContext';
import logoMark from '../assets/profitlift-logo-new.svg';
import { useState, useEffect } from 'react';

type NavItem = {
    to: string;
    icon: React.ComponentType<{ size?: number; strokeWidth?: number }>;
    label: string;
    phase?: 1 | 2;
    hint?: string;
};

const navItems: NavItem[] = [
    // Phase 1 - Current
    { to: '/', icon: LayoutDashboard, label: 'Overview', phase: 1, hint: 'your dashboard' },
    { to: '/upload', icon: Upload, label: 'Upload', phase: 1, hint: 'import data' },
    { to: '/recommendations', icon: Gift, label: 'Actions', phase: 1, hint: 'bundle ideas' },
    { to: '/validation', icon: ShieldCheck, label: 'Evidence', phase: 1, hint: 'causal proof' },
    // Phase 2 - Coming Soon
    { to: '/performance', icon: Activity, label: 'Track', phase: 2, hint: 'coming soon' },
    { to: '/stores', icon: Store, label: 'Stores', phase: 2, hint: 'coming soon' },
];

export function Topbar() {
    const location = useLocation();
    const { isDemoMode, toggleDemoMode } = useDemo();
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinkClasses = (isActive: boolean, isPhase2: boolean) =>
        clsx(
            'relative flex items-center gap-1.5 px-2.5 py-2 rounded-xl text-sm font-medium transition-all',
            isPhase2 && 'opacity-50 cursor-not-allowed',
            isActive && !isPhase2
                ? 'bg-primary/10 text-primary'
                : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
        );

    return (
        <header className={clsx(
            'h-16 flex items-center justify-between px-4 border-b bg-surface/95 backdrop-blur-lg shrink-0 sticky top-0 z-50 transition-all duration-300',
            isScrolled ? 'border-border shadow-sm' : 'border-transparent'
        )}>
            {/* Logo Section */}
            <NavLink to="/" className="flex items-center gap-2.5 group shrink-0">
                <div className="relative w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center overflow-hidden group-hover:bg-primary/20 transition-colors">
                    <img src={logoMark} alt="ProfitLift" className="w-5 h-5 relative z-10" />
                </div>
                <div className="hidden lg:block">
                    <h1 className="text-sm font-bold text-text-primary tracking-tight group-hover:text-primary transition-colors">
                        ProfitLift
                    </h1>
                    <p className="text-[9px] text-text-muted -mt-0.5 flex items-center gap-1">
                        <Brain size={8} />
                        Causal AI
                    </p>
                </div>
                    </NavLink>

            {/* Navigation - All items visible with Phase indicators */}
            <nav className="flex items-center bg-surface-elevated/50 rounded-2xl p-1 mx-2">
                {/* Phase 1 items */}
                <div className="flex items-center gap-0.5 pr-2 border-r border-border mr-2">
                    {navItems.filter(item => item.phase === 1).map((item) => {
                        const isActive = location.pathname === item.to;
                        return (
                                <NavLink
                                key={item.to} 
                                to={item.to} 
                                className={navLinkClasses(isActive, false)}
                                title={item.hint}
                            >
                                <item.icon size={16} strokeWidth={isActive ? 2.5 : 2} />
                                <span className="hidden md:inline text-xs">{item.label}</span>
                                </NavLink>
                        );
                    })}
                </div>

                {/* Phase 2 items - clickable to see preview */}
                <div className="flex items-center gap-0.5">
                    <span className="text-[9px] font-bold text-accent uppercase tracking-wider px-1.5 hidden sm:block">P2</span>
                    {navItems.filter(item => item.phase === 2).map((item) => {
                        const isActive = location.pathname === item.to;
                        return (
                                <NavLink
                                key={item.to}
                                to={item.to}
                                className={clsx(
                                    'relative flex items-center gap-1.5 px-2.5 py-2 rounded-xl text-sm font-medium transition-all',
                                    isActive
                                        ? 'bg-accent/10 text-accent'
                                        : 'text-text-muted hover:text-accent hover:bg-accent/5'
                                )}
                                title={`${item.label} - ${item.hint}`}
                            >
                                <item.icon size={16} strokeWidth={isActive ? 2.5 : 2} />
                                <span className="hidden lg:inline text-xs">{item.label}</span>
                                {/* Phase 2 indicator dot */}
                                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-accent rounded-full" />
                                </NavLink>
                        );
                    })}
                </div>
            </nav>

            {/* Right Section */}
            <div className="flex items-center gap-2 shrink-0">
                {/* Demo Mode Toggle */}
                <button
                    onClick={toggleDemoMode}
                    className={clsx(
                        'flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all',
                        isDemoMode
                            ? 'bg-primary text-white shadow-md hover:bg-primary-dark'
                            : 'bg-surface-elevated text-text-muted hover:text-text-secondary hover:bg-surface-hover'
                    )}
                    title={isDemoMode ? 'Using sample data' : 'Try with sample data'}
                >
                    <Database size={14} className={isDemoMode ? 'animate-pulse' : ''} />
                    <span className="hidden sm:inline">
                        {isDemoMode ? 'Demo' : 'Demo'}
                    </span>
                </button>

                {/* Settings */}
                <NavLink
                    to="/settings"
                    className={({ isActive }) =>
                        clsx(
                            'flex items-center justify-center w-9 h-9 rounded-xl transition-all',
                            isActive
                                ? 'bg-primary/10 text-primary'
                                : 'text-text-muted hover:text-text-secondary hover:bg-surface-elevated'
                        )
                    }
                    title="System settings"
                >
                    <Settings size={18} />
                </NavLink>
            </div>
        </header>
    );
}
