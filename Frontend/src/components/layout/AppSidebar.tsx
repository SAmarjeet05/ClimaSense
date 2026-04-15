import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, Lightbulb, Map,
  Database, Cpu, Users, ScrollText, BarChart3, ChevronLeft, ChevronRight, Zap, MessageSquare
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { UserRole } from '@/hooks/useAuth';

interface SidebarProps {
  role: UserRole;
  collapsed: boolean;
  onToggle: () => void;
}

const userLinks = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/forecast', icon: Zap, label: 'Forecast & Simulator' },
  { to: '/insights', icon: Lightbulb, label: 'Insights & Compare' },
  { to: '/climate-map', icon: Map, label: 'Climate Map' },
  { to: '/assistant', icon: MessageSquare, label: 'AI Assistant' },
];

const adminLinks = [
  { to: '/admin', icon: BarChart3, label: 'Overview' },
  { to: '/admin/datasets', icon: Database, label: 'Datasets' },
  { to: '/admin/models', icon: Cpu, label: 'Models' },
  { to: '/admin/users', icon: Users, label: 'Users' },
  { to: '/admin/logs', icon: ScrollText, label: 'Logs' },
];

export const AppSidebar: React.FC<SidebarProps> = ({ role, collapsed, onToggle }) => {
  const location = useLocation();
  const links = role === 'admin' ? [...userLinks, ...adminLinks] : userLinks;

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-screen z-40 glass-strong border-r border-border/10 flex flex-col"
    >
      {/* Logo */}
      <div className="p-4 flex items-center gap-3 border-b border-border/10 min-h-[64px]">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center flex-shrink-0">
          <Zap className="w-5 h-5 text-primary-foreground" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="font-bold text-lg text-gradient-primary whitespace-nowrap">
              ClimaAI
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto scrollbar-thin">
        {role === 'admin' && !collapsed && (
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-3 mb-2">Analytics</p>
        )}
        {userLinks.map(link => (
          <SidebarLink key={link.to} {...link} active={location.pathname === link.to} collapsed={collapsed} />
        ))}
        {role === 'admin' && (
          <>
            {!collapsed && <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-3 mt-6 mb-2">Admin</p>}
            {collapsed && <div className="border-t border-border/10 my-3" />}
            {adminLinks.map(link => (
              <SidebarLink key={link.to} {...link} active={location.pathname === link.to} collapsed={collapsed} />
            ))}
          </>
        )}
      </nav>

      {/* Toggle */}
      <button onClick={onToggle} className="p-4 border-t border-border/10 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </motion.aside>
  );
};

const SidebarLink: React.FC<{ to: string; icon: React.FC<any>; label: string; active: boolean; collapsed: boolean }> = ({ to, icon: Icon, label, active, collapsed }) => (
  <Link
    to={to}
    className={cn(
      'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
      active ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
    )}
  >
    {active && (
      <motion.div layoutId="sidebar-active" className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-primary rounded-r-full" />
    )}
    <Icon className={cn('w-[18px] h-[18px] flex-shrink-0', active && 'text-primary')} />
    <AnimatePresence>
      {!collapsed && (
        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-sm font-medium whitespace-nowrap">
          {label}
        </motion.span>
      )}
    </AnimatePresence>
  </Link>
);
