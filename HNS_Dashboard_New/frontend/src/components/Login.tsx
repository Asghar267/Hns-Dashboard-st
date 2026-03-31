import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../api/AuthContext';
import { LogIn, Loader } from 'lucide-react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/auth/token', 
        new URLSearchParams({
          username: username,
          password: password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      login(response.data.access_token, username, response.data.refresh_token);
    } catch (err) {
      setError('Invalid username or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="w-full max-w-sm p-8 space-y-8 bg-surface rounded-xl shadow-card">
        <div className="text-center">
          <div className="inline-block p-3 bg-primary rounded-lg">
            <span className="text-white font-bold text-2xl">HNS</span>
          </div>
          <h1 className="mt-4 text-2xl font-bold text-textPrimary">Performance Dashboard</h1>
          <p className="text-textSecondary">Welcome back! Please sign in to continue.</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-textPrimary">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-background border border-border rounded-md focus:ring-2 focus:ring-primary outline-none"
              placeholder="Enter your username"
              name="username"
              autoComplete="username"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-textPrimary">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-background border border-border rounded-md focus:ring-2 focus:ring-primary outline-none"
              placeholder="Enter your password"
              name="password"
              autoComplete="current-password"
            />
          </div>

          {error && <p className="text-sm text-danger text-center">{error}</p>}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full flex justify-center items-center py-3 px-4 bg-primary text-white font-semibold rounded-md hover:bg-opacity-90 transition-all disabled:bg-opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader className="animate-spin" /> : <LogIn size={20} className="mr-2" />} 
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
        
        <div className="mt-8 text-center text-textSecondary text-xs">
          &copy; {new Date().getFullYear()} HNS Performance Dashboard v2.1
        </div>
      </div>
    </div>
  );
};

export default Login;
