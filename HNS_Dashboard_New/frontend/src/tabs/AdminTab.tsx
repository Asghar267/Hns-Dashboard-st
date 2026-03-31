import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../api/AuthContext';
import { useFilters } from '../api/FilterContext';
import { UserPlus, Trash2, Shield, User, MapPin, Layout } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface UserData {
  username: string;
  role: string;
  allowed_branches?: number[];
  allowed_tabs?: string[];
}

const TAB_OPTIONS = [
  "Overview", "QR Commission", "Khadda Diagnostics", "Chef Sales", "Order Takers", "OT Targets",
  "Chef Targets", "Pivot Tables", "Category Coverage", "Trends & Analytics", 
  "Material Cost Commission", "Ramzan Deals"
];

const AdminTab: React.FC = () => {
  const { token, user } = useAuth();
  const { branches } = useFilters();
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<any>({
    username: '',
    password: '',
    role: 'user',
    allowed_branches: [],
    allowed_tabs: []
  });
  const [editingUser, setEditingUser] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/auth/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchUsers();
    }
  }, [token, user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await axios.put(`${API_BASE_URL}/auth/users/${editingUser}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API_BASE_URL}/auth/users`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      alert('User saved successfully');
      setFormData({ username: '', password: '', role: 'user', allowed_branches: [], allowed_tabs: [] });
      setEditingUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save user');
    }
  };

  const handleDelete = async (username: string) => {
    if (!confirm(`Are you sure you want to delete user ${username}?`)) return;
    try {
      await axios.delete(`${API_BASE_URL}/auth/users/${username}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  const handleEdit = (u: UserData) => {
    setFormData({
      username: u.username,
      role: u.role,
      allowed_branches: u.allowed_branches || [],
      allowed_tabs: u.allowed_tabs || [],
      password: '' // Don't show password
    });
    setEditingUser(u.username);
  };

  const toggleBranch = (branchId: number) => {
    const current = formData.allowed_branches || [];
    const updated = current.includes(branchId)
      ? current.filter((id: number) => id !== branchId)
      : [...current, branchId];
    setFormData({ ...formData, allowed_branches: updated });
  };

  const toggleTab = (tabName: string) => {
    const current = formData.allowed_tabs || [];
    const updated = current.includes(tabName)
      ? current.filter((t: string) => t !== tabName)
      : [...current, tabName];
    setFormData({ ...formData, allowed_tabs: updated });
  };

  if (user?.role !== 'admin') {
    return <div className="p-8 text-center text-danger font-bold">Access Denied. Admin only.</div>;
  }

  if (loading && users.length === 0) return <div>Loading...</div>;

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Form */}
        <div className="lg:col-span-1 bg-surface p-6 rounded-lg shadow-card border border-border">
          <h3 className="text-lg font-bold text-textPrimary mb-6 flex items-center gap-2">
            <UserPlus size={20} className="text-primary" />
            {editingUser ? 'Edit User' : 'Create New User'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-textSecondary uppercase block mb-1">Username</label>
                <input 
                  type="text"
                  disabled={!!editingUser}
                  value={formData.username}
                  onChange={e => setFormData({...formData, username: e.target.value})}
                  className="w-full bg-background border border-border rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
                  required
                />
              </div>
              
              <div>
                <label className="text-xs font-bold text-textSecondary uppercase block mb-1">
                  {editingUser ? 'New Password (Optional)' : 'Password'}
                </label>
                <input 
                  type="password"
                  value={formData.password}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-background border border-border rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                  required={!editingUser}
                />
              </div>
              
              <div>
                <label className="text-xs font-bold text-textSecondary uppercase block mb-1">Role</label>
                <select 
                  value={formData.role}
                  onChange={e => setFormData({...formData, role: e.target.value})}
                  className="w-full bg-background border border-border rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-textSecondary uppercase block mb-2 flex items-center gap-2">
                <MapPin size={14} className="text-secondary" />
                Branch Access
              </label>
              <div className="max-h-32 overflow-y-auto space-y-1 p-2 bg-background rounded-md border border-border">
                {branches.map(branch => (
                  <div key={branch.Shop_id} className="flex items-center">
                    <input 
                      type="checkbox" 
                      id={`access-branch-${branch.Shop_id}`}
                      checked={(formData.allowed_branches || []).includes(branch.Shop_id)}
                      onChange={() => toggleBranch(branch.Shop_id)}
                      className="h-3 w-3 rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <label htmlFor={`access-branch-${branch.Shop_id}`} className="ml-2 text-[11px] text-textPrimary truncate">
                      {branch.Shop_name}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-textSecondary uppercase block mb-2 flex items-center gap-2">
                <Layout size={14} className="text-secondary" />
                Tab Access
              </label>
              <div className="max-h-40 overflow-y-auto grid grid-cols-1 gap-1 p-2 bg-background rounded-md border border-border">
                {TAB_OPTIONS.map(tab => (
                  <div key={tab} className="flex items-center">
                    <input 
                      type="checkbox" 
                      id={`access-tab-${tab}`}
                      checked={(formData.allowed_tabs || []).includes(tab)}
                      onChange={() => toggleTab(tab)}
                      className="h-3 w-3 rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <label htmlFor={`access-tab-${tab}`} className="ml-2 text-[11px] text-textPrimary truncate">
                      {tab}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 flex gap-2">
              <button 
                type="submit"
                className="flex-1 bg-primary text-white py-2 rounded-md text-sm font-bold hover:bg-primary/90 transition-colors"
              >
                {editingUser ? 'Update User' : 'Create User'}
              </button>
              {editingUser && (
                <button 
                  type="button"
                  onClick={() => {
                    setEditingUser(null);
                    setFormData({ username: '', password: '', role: 'user', allowed_branches: [], allowed_tabs: [] });
                  }}
                  className="bg-background border border-border px-4 py-2 rounded-md text-sm font-medium hover:bg-surface transition-colors"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        {/* User List */}
        <div className="lg:col-span-2 bg-surface rounded-lg shadow-card border border-border overflow-hidden flex flex-col">
          <div className="p-6 border-b border-border">
            <h3 className="text-lg font-bold text-textPrimary flex items-center gap-2">
              <Shield size={20} className="text-success" />
              Current Users
            </h3>
          </div>
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-sm">
              <thead className="bg-background text-textSecondary text-xs uppercase sticky top-0">
                <tr>
                  <th className="px-6 py-3 font-semibold">User</th>
                  <th className="px-6 py-3 font-semibold">Role</th>
                  <th className="px-6 py-3 font-semibold">Access</th>
                  <th className="px-6 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {users.map((u) => (
                  <tr key={u.username} className="hover:bg-background transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                          <User size={16} />
                        </div>
                        <span className="font-bold text-textPrimary">{u.username}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${u.role === 'admin' ? 'bg-danger/10 text-danger' : 'bg-primary/10 text-primary'}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-[10px] text-textSecondary max-w-[200px] truncate">
                        {u.allowed_branches?.length || 0} branches, {u.allowed_tabs?.length || 0} tabs
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button 
                          onClick={() => handleEdit(u)}
                          className="p-2 text-textSecondary hover:text-primary transition-colors"
                          title="Edit User"
                        >
                          <Layout size={18} />
                        </button>
                        <button 
                          onClick={() => handleDelete(u.username)}
                          disabled={u.username === user?.username}
                          className={`p-2 transition-colors ${u.username === user?.username ? 'opacity-20 cursor-not-allowed' : 'text-textSecondary hover:text-danger'}`}
                          title="Delete User"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminTab;
