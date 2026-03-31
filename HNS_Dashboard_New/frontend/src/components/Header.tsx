import React from 'react';
import { useAuth } from '../api/AuthContext';
import { Bell } from 'lucide-react';

interface HeaderProps {
  title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
  const { user } = useAuth();
  const displayName = user?.username || 'Admin (Test)';
  const firstLetter = displayName.charAt(0).toUpperCase();

  return (
    <header className="bg-surface p-4 border-b border-border flex justify-between items-center">
      <h1 className="text-2xl font-bold text-textPrimary">{title}</h1>
      <div className="flex items-center space-x-4">
        <button className="relative text-textSecondary hover:text-primary">
          <Bell size={20} />
          <span className="absolute top-0 right-0 w-2 h-2 bg-danger rounded-full"></span>
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold">
            {firstLetter}
          </div>
          <span className="text-sm font-semibold text-textPrimary">{displayName}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
