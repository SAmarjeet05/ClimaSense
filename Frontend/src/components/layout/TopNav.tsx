import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, ChevronDown, LogOut } from 'lucide-react';
import { User, UserRole } from '@/hooks/useAuth';

interface TopNavProps {
  user: User;
  onRoleSwitch: (role: UserRole) => void;
  onLogout: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ user, onRoleSwitch, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <header className="h-16 glass-strong border-b border-border/10 flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Search */}
      <div className="relative max-w-md w-full">

      </div>

      <div className="flex items-center gap-4">
        {/* Role Switcher
        <select
          value={user.role}
          onChange={(e) => onRoleSwitch(e.target.value as UserRole)}
          className="bg-muted/30 border border-border/20 rounded-lg px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 cursor-pointer"
        >
          <option value="user">Viewer</option>
          <option value="admin">Admin</option>
        </select> */}

        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-muted/50 transition-colors">
          <Bell className="w-4 h-4 text-muted-foreground" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full animate-pulse-glow" />
        </button>

        {/* Profile */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-xs font-bold text-primary-foreground">
            {user.name.charAt(0)}
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium text-foreground">{user.name}</p>
            <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="p-2 rounded-lg hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors"
          title="Logout"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
