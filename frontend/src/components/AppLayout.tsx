import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { LayoutDashboard, Search, History, Info, LogOut, ShieldCheck, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyze', label: 'Analyze', icon: Search },
  { to: '/history', label: 'History', icon: History },
  { to: '/model', label: 'Model', icon: Info },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-40 w-60 bg-white border-r border-slate-200 flex flex-col transition-transform duration-200",
        mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="h-16 flex items-center gap-2.5 px-6 border-b border-slate-200">
          <ShieldCheck className="h-5 w-5 text-indigo-600" strokeWidth={1.75} />
          <span className="font-semibold text-slate-800 tracking-tight">ReviewGuard</span>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-0.5">
          {navItems.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to || location.pathname.startsWith(to + '/');
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                  active
                    ? "bg-indigo-50 text-indigo-700 font-medium"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                )}
              >
                <Icon className="h-4 w-4 flex-shrink-0" strokeWidth={1.75} />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-slate-200 p-4">
          <div className="text-xs text-slate-500 mb-3 truncate">{user?.email}</div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 transition-colors w-full"
          >
            <LogOut className="h-4 w-4" strokeWidth={1.75} />
            Sign out
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 lg:ml-60 flex flex-col min-h-screen">
        {/* Top bar (mobile) */}
        <header className="lg:hidden h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3">
          <button onClick={() => setMobileOpen(true)} className="text-slate-500 hover:text-slate-800">
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-indigo-600" strokeWidth={1.75} />
            <span className="font-semibold text-slate-800 text-sm">ReviewGuard</span>
          </div>
        </header>

        <main className="flex-1 p-6 lg:p-8 max-w-5xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
