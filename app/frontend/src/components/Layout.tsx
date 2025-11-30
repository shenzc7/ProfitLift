import { Outlet } from 'react-router-dom';
import { Topbar } from './Topbar';

export function Layout() {
    return (
        <div className="flex flex-col h-screen bg-background text-text-primary overflow-hidden font-sans">
            <Topbar />
            <main className="flex-1 overflow-auto relative">
                <div className="p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
