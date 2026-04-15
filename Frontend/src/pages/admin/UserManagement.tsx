import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Shield, Trash2, Plus, Loader2 } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { adminAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
  created_at: string;
  is_current_user?: boolean;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionInProgress, setActionInProgress] = useState<number | null>(null);
  const [roleDialogUser, setRoleDialogUser] = useState<User | null>(null);
  const [selectedRole, setSelectedRole] = useState<'admin' | 'user'>('user');
  const { toast } = useToast();

  // Load users on component mount
  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await adminAPI.getUsers();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
      toast({
        title: 'Error',
        description: 'Failed to load users',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number, userName: string) => {
    if (!window.confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone.`)) {
      return;
    }

    setActionInProgress(userId);
    try {
      await adminAPI.deleteUser(userId);
      toast({
        title: 'Success',
        description: `User "${userName}" has been deleted`,
      });
      setUsers(users.filter(u => u.id !== userId));
    } catch (error: any) {
      console.error('Failed to delete user:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete user',
        variant: 'destructive',
      });
    } finally {
      setActionInProgress(null);
    }
  };

  const handleUpdateRole = async (userId: number, newRole: 'admin' | 'user') => {
    setActionInProgress(userId);
    try {
      await adminAPI.updateUserRole(userId, newRole);
      toast({
        title: 'Success',
        description: `User role updated to ${newRole}`,
      });
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
      setRoleDialogUser(null);
    } catch (error: any) {
      console.error('Failed to update user role:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update user role',
        variant: 'destructive',
      });
    } finally {
      setActionInProgress(null);
    }
  };

  const getStatus = (created_at: string) => {
    // Consider user active if created within last 30 days
    const createdDate = new Date(created_at);
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return createdDate > thirtyDaysAgo ? 'active' : 'inactive';
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">User Management</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage users and role assignments</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary/20 text-primary border border-primary/30 rounded-lg text-sm font-medium hover:bg-primary/30 transition-colors">
          <Plus className="w-4 h-4" /> Add User
        </button>
      </div>

      <GlassCard hover={false} className="p-0 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
            <span className="ml-2 text-muted-foreground">Loading users...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/10 text-muted-foreground text-xs uppercase tracking-wider">
                  <th className="text-left p-4">User</th>
                  <th className="text-left p-4">Role</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Joined</th>
                  <th className="text-left p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      No users found
                    </td>
                  </tr>
                ) : (
                  users.map(u => {
                    const status = getStatus(u.created_at);
                    const joinedDate = new Date(u.created_at).toLocaleDateString();
                    return (
                      <tr key={u.id} className="border-b border-border/5 hover:bg-muted/20 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-xs font-bold text-primary-foreground">
                              {u.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="text-foreground font-medium">
                                {u.name}
                                {u.is_current_user && <span className="text-[10px] ml-2 px-2 py-0.5 bg-accent/20 text-accent rounded">You</span>}
                              </p>
                              <p className="text-muted-foreground text-xs">{u.email}</p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${u.role === 'admin' ? 'bg-secondary/20 text-secondary' : 'bg-primary/20 text-primary'}`}>
                            {u.role}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${status === 'active' ? 'bg-accent/20 text-accent' : 'bg-muted text-muted-foreground'}`}>
                            {status}
                          </span>
                        </td>
                        <td className="p-4 text-muted-foreground">{joinedDate}</td>
                        <td className="p-4 flex gap-2">
                          <button 
                            onClick={() => {
                              setRoleDialogUser(u);
                              setSelectedRole(u.role);
                            }}
                            className="p-1.5 rounded hover:bg-muted/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            title="Edit permissions"
                            disabled={actionInProgress === u.id}
                          >
                            {actionInProgress === u.id ? (
                              <Loader2 className="w-3.5 h-3.5 text-muted-foreground animate-spin" />
                            ) : (
                              <Shield className="w-3.5 h-3.5 text-muted-foreground" />
                            )}
                          </button>
                          <button 
                            onClick={() => handleDeleteUser(u.id, u.name)}
                            className="p-1.5 rounded hover:bg-destructive/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            disabled={u.is_current_user || actionInProgress === u.id} 
                            title={u.is_current_user ? "Cannot delete yourself" : "Delete user"}
                          >
                            {actionInProgress === u.id ? (
                              <Loader2 className="w-3.5 h-3.5 text-destructive animate-spin" />
                            ) : (
                              <Trash2 className="w-3.5 h-3.5 text-destructive" />
                            )}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* Role Selection Dialog */}
      {roleDialogUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <GlassCard className="w-96 p-6">
            <h3 className="text-lg font-bold mb-4">Change User Role</h3>
            <p className="text-muted-foreground mb-4">Current user: <span className="font-medium text-foreground">{roleDialogUser.name}</span></p>
            
            <div className="space-y-3 mb-6">
              <label className="flex items-center gap-3 p-3 border border-border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                <input
                  type="radio"
                  name="role"
                  value="user"
                  checked={selectedRole === 'user'}
                  onChange={(e) => setSelectedRole(e.target.value as 'user')}
                  className="w-4 h-4"
                />
                <div>
                  <p className="font-medium text-foreground">User</p>
                  <p className="text-xs text-muted-foreground">Limited access to application features</p>
                </div>
              </label>
              
              <label className="flex items-center gap-3 p-3 border border-border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                <input
                  type="radio"
                  name="role"
                  value="admin"
                  checked={selectedRole === 'admin'}
                  onChange={(e) => setSelectedRole(e.target.value as 'admin')}
                  className="w-4 h-4"
                />
                <div>
                  <p className="font-medium text-foreground">Admin</p>
                  <p className="text-xs text-muted-foreground">Full access to all features and settings</p>
                </div>
              </label>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setRoleDialogUser(null)}
                className="flex-1 px-4 py-2 text-muted-foreground border border-border rounded-lg hover:bg-muted/50 transition-colors"
                disabled={actionInProgress === roleDialogUser.id}
              >
                Cancel
              </button>
              <button
                onClick={() => handleUpdateRole(roleDialogUser.id, selectedRole)}
                className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                disabled={actionInProgress === roleDialogUser.id || selectedRole === roleDialogUser.role}
              >
                {actionInProgress === roleDialogUser.id ? 'Updating...' : 'Update Role'}
              </button>
            </div>
          </GlassCard>
        </div>
      )}
    </motion.div>
  );
};

export default UserManagement;
