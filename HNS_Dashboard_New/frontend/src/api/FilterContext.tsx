import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

import { useAuth } from './AuthContext';

interface Branch {
  Shop_id: number;
  Shop_name: string;
}

interface FilterContextType {
  startDate: string;
  setStartDate: (date: string) => void;
  endDate: string;
  setEndDate: (date: string) => void;
  selectedBranches: number[];
  setSelectedBranches: (branches: number[]) => void;
  dataMode: string;
  setDataMode: (mode: string) => void;
  branches: Branch[];
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [startDate, setStartDate] = useState('2026-03-01');
  const [endDate, setEndDate] = useState('2026-03-17');
  const [selectedBranches, setSelectedBranches] = useState<number[]>([]);
  const [dataMode, setDataMode] = useState('Unfiltered');
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBranches = async () => {
      try {
        const response = await axios.get('http://localhost:8000/branches');
        const allBranches = response.data.map((b: any) => ({
          Shop_id: Math.floor(b.Shop_id),
          Shop_name: b.Shop_name
        }));
        
        // Filter branches based on user's allowed_branches
        const filteredBranches = user?.allowed_branches && user.allowed_branches.length > 0
          ? allBranches.filter((b: Branch) => user.allowed_branches?.includes(b.Shop_id))
          : allBranches;

        setBranches(filteredBranches);
        // Select all allowed branches by default
        setSelectedBranches(filteredBranches.map((b: Branch) => b.Shop_id));
      } catch (err) {
        console.error('Failed to fetch branches', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBranches();
  }, [user]);

  return (
    <FilterContext.Provider value={{
      startDate, setStartDate,
      endDate, setEndDate,
      selectedBranches, setSelectedBranches,
      dataMode, setDataMode,
      branches
    }}>
      {!loading && children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};
