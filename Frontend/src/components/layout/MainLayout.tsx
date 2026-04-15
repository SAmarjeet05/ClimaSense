import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AppSidebar } from './AppSidebar';
import { TopNav } from './TopNav';
import { useAuth } from '@/hooks/useAuth';

export const MainLayout: React.FC = () => {
  const { user, switchRole, logout } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background flex">
      <AppSidebar role={user.role} collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <motion.div
        animate={{ marginLeft: sidebarCollapsed ? 72 : 260 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="flex-1 flex flex-col min-h-screen"
      >
        <TopNav user={user} onRoleSwitch={switchRole} onLogout={logout} />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </motion.div>
    </div>
  );
};
