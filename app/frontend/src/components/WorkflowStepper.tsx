import { CheckCircle, Upload, Gift, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';

type WorkflowStep = {
    id: string;
    label: string;
    description: string;
    path: string;
    icon: React.ElementType;
};

const steps: WorkflowStep[] = [
    { id: 'upload', label: 'Import Data', description: 'Upload transactions', path: '/upload', icon: Upload },
    { id: 'analyze', label: 'Discover', description: 'Find patterns', path: '/recommendations', icon: Gift },
    { id: 'validate', label: 'Validate', description: 'Verify causally', path: '/validation', icon: ShieldCheck },
];

type WorkflowStepperProps = {
    currentStep?: number;
    hasData?: boolean;
    hasRecommendations?: boolean;
};

export function WorkflowStepper({ currentStep = 0, hasData = false, hasRecommendations = false }: WorkflowStepperProps) {
    const getStepStatus = (index: number): 'completed' | 'current' | 'upcoming' => {
        if (index < currentStep) return 'completed';
        if (index === currentStep) return 'current';
        return 'upcoming';
    };

    const isStepAccessible = (index: number): boolean => {
        if (index === 0) return true;
        if (index === 1) return hasData;
        if (index === 2) return hasRecommendations;
        return false;
    };

    return (
        <div className="relative">
            {/* Background connector line */}
            <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" />
            
            {/* Progress line */}
            <div 
                className="absolute top-5 left-0 h-0.5 bg-primary transition-all duration-700 ease-out"
                style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />

            {/* Steps */}
            <div className="relative flex justify-between">
                {steps.map((step, index) => {
                    const status = getStepStatus(index);
                    const accessible = isStepAccessible(index);
                    const Icon = step.icon;

                    return (
                        <Link
                            key={step.id}
                            to={accessible ? step.path : '#'}
                            className={clsx(
                                'flex flex-col items-center group transition-all',
                                !accessible && 'cursor-not-allowed opacity-50'
                            )}
                            onClick={e => !accessible && e.preventDefault()}
                        >
                            {/* Step circle */}
                            <div
                                className={clsx(
                                    'relative w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 z-10',
                                    status === 'completed' && 'bg-primary text-white shadow-md',
                                    status === 'current' && 'bg-primary text-white shadow-lg ring-4 ring-primary/20 scale-110',
                                    status === 'upcoming' && 'bg-surface border-2 border-border text-text-muted',
                                    accessible && status !== 'upcoming' && 'group-hover:scale-105'
                                )}
                            >
                                {status === 'completed' ? (
                                    <CheckCircle size={18} className="animate-in zoom-in duration-300" />
                                ) : (
                                    <Icon size={18} />
                                )}
                                
                                {/* Pulse animation for current step */}
                                {status === 'current' && (
                                    <span className="absolute inset-0 rounded-full bg-primary animate-ping opacity-30" />
                                )}
                            </div>

                            {/* Label */}
                            <div className="mt-3 text-center">
                                <div className={clsx(
                                    'text-xs font-semibold transition-colors',
                                    status === 'current' ? 'text-primary' : 
                                    status === 'completed' ? 'text-text-primary' : 'text-text-muted'
                                )}>
                                    {step.label}
                                </div>
                                <div className="text-[10px] text-text-muted mt-0.5 hidden sm:block">
                                    {step.description}
                                </div>
                            </div>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
}

// Compact inline stepper for page headers
export function InlineWorkflowIndicator({ step }: { step: number }) {
    return (
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/5 border border-primary/10">
            <span className="text-[10px] font-bold text-primary uppercase tracking-wider">
                Step {step + 1} of 3
            </span>
            <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                    <div 
                        key={i}
                        className={clsx(
                            'w-1.5 h-1.5 rounded-full transition-all',
                            i <= step ? 'bg-primary' : 'bg-border'
                        )}
                    />
                ))}
            </div>
        </div>
    );
}

