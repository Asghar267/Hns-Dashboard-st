import React, { useEffect, useState } from 'react';
import { useFilters } from '../api/FilterContext';
import { Calendar, MapPin, SlidersHorizontal, Power, Settings, Sun, Moon, RefreshCw, Activity, Heart, Camera, Clock, ChevronDown } from 'lucide-react';
import { useAuth } from '../api/AuthContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const CollapsibleSection: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode; isOpen: boolean; onClick: () => void }> = ({ title, icon, children, isOpen, onClick }) => (
  <div className="border-b border-border/50">
    <button onClick={onClick} className="w-full flex items-center justify-between py-3 px-1 text-sm font-bold text-textPrimary">
      <div className="flex items-center gap-2">
        {icon}
        {title}
      </div>
      <ChevronDown size={18} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
    </button>
    {isOpen && (
      <div className="pb-4 pt-2 px-1 space-y-4">
        {children}
      </div>
    )}
  </div>
);

const Sidebar: React.FC = () => {
  const {
    startDate, setStartDate,
    endDate, setEndDate,
    selectedBranches, setSelectedBranches,
    dataMode, setDataMode,
    branches
  } = useFilters();
  const { logout } = useAuth();
  const [isDarkMode, setIsDarkMode] = React.useState(false);
  const [isAutoRefresh, setIsAutoRefresh] = React.useState(false);
  const [perfTrace, setPerfTrace] = useState<any[]>([]);
  const [showPerf, setShowPerf] = useState(false);
  const [openSection, setOpenSection] = useState('filters');

  useEffect(() => {
    let interval: any;
    if (showPerf) {
      const fetchPerf = async () => {
        try {
          const res = await axios.get(`${API_BASE_URL}/system/perf-trace`);
          setPerfTrace(res.data.reverse());
        } catch (e) {}
      };
      fetchPerf();
      interval = setInterval(fetchPerf, 3000);
    }
    return () => clearInterval(interval);
  }, [showPerf]);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  const handleBranchChange = (branchId: number) => {
    const newSelection = selectedBranches.includes(branchId)
      ? selectedBranches.filter(id => id !== branchId)
      : [...selectedBranches, branchId];
    setSelectedBranches(newSelection);
  };

  return (
    <aside className="w-72 bg-surface text-textPrimary flex flex-col h-screen p-4 border-r border-border">
      <div className="flex items-center mb-6 pl-1">
        <div className="w-10 h-10 bg-primary text-white flex items-center justify-center rounded-lg mr-3">
          <span className="font-bold text-lg">HNS</span>
        </div>
        <h1 className="text-xl font-bold">Dashboard</h1>
      </div>

      <div className="flex-grow overflow-y-auto pr-2 -mr-2">
        <CollapsibleSection 
          title="Main Filters"
          icon={<SlidersHorizontal size={16} />}
          isOpen={openSection === 'filters'}
          onClick={() => setOpenSection(openSection === 'filters' ? '' : 'filters')}
        >
          <div className="space-y-2">
            <label className="text-xs font-bold text-textSecondary uppercase">Date Range</label>
            <input 
              type="date" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
            />
            <input 
              type="date" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold text-textSecondary uppercase">Data Mode</label>
            <select 
              value={dataMode}
              onChange={(e) => setDataMode(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none cursor-pointer"
            >
              <option value="Unfiltered">Unfiltered</option>
              <option value="Filtered">Filtered</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-bold text-textSecondary uppercase">Branches</label>
            <div className="max-h-48 overflow-y-auto space-y-2 p-2 bg-background rounded-md border border-border">
              {branches.map(branch => (
                <div key={branch.Shop_id} className="flex items-center">
                  <input 
                    type="checkbox" 
                    id={`branch-${branch.Shop_id}`}
                    checked={selectedBranches.includes(branch.Shop_id)}
                    onChange={() => handleBranchChange(branch.Shop_id)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <label htmlFor={`branch-${branch.Shop_id}`} className="ml-2 text-sm text-textPrimary">
                    {branch.Shop_name}
                  </label>
                </div>
              ))}
            </div>
          </div>
        </CollapsibleSection>

        <CollapsibleSection 
          title="Settings"
          icon={<Settings size={16} />}
          isOpen={openSection === 'settings'}
          onClick={() => setOpenSection(openSection === 'settings' ? '' : 'settings')}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm font-medium text-textPrimary">
              {isDarkMode ? <Moon size={16} className="mr-2 text-secondary" /> : <Sun size={16} className="mr-2 text-secondary" />}
              Dark Mode
            </div>
            <button 
              onClick={toggleDarkMode}
              className={`w-10 h-5 rounded-full transition-colors relative ${isDarkMode ? 'bg-primary' : 'bg-gray-300'}`}
            >
              <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${isDarkMode ? 'right-1' : 'left-1'}`} />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm font-medium text-textPrimary">
              <RefreshCw size={16} className={`mr-2 text-secondary ${isAutoRefresh ? 'animate-spin' : ''}`} />
              Auto Refresh
            </div>
            <button 
              onClick={() => setIsAutoRefresh(!isAutoRefresh)}
              className={`w-10 h-5 rounded-full transition-colors relative ${isAutoRefresh ? 'bg-primary' : 'bg-gray-300'}`}
            >
              <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${isAutoRefresh ? 'right-1' : 'left-1'}`} />
            </button>
          </div>
        </CollapsibleSection>

        <CollapsibleSection 
          title="System Actions"
          icon={<Activity size={16} />}
          isOpen={openSection === 'actions'}
          onClick={() => setOpenSection(openSection === 'actions' ? '' : 'actions')}
        >
          <button 
            onClick={() => axios.post(`${API_BASE_URL}/system/snapshots`).then(() => alert('Snapshot generation started'))}
            className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-textPrimary hover:bg-background rounded-md transition-colors"
          >
            <Camera size={16} className="text-secondary" />
            <span>Generate Snapshots</span>
          </button>
          <button 
            onClick={() => axios.get(`${API_BASE_URL}/system/health`).then(res => alert(JSON.stringify(res.data, null, 2)))}
            className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-textPrimary hover:bg-background rounded-md transition-colors"
          >
            <Heart size={16} className="text-danger" />
            <span>Health Check</span>
          </button>
          <button 
            onClick={() => setShowPerf(!showPerf)}
            className={`w-full flex items-center space-x-2 px-3 py-2 text-sm text-textPrimary hover:bg-background rounded-md transition-colors ${showPerf ? 'bg-primary/10 text-primary' : ''}`}
          >
            <Clock size={16} className="text-primary" />
            <span>Performance Trace</span>
          </button>

          {showPerf && (
            <div className="mt-2 p-2 bg-background rounded-md border border-border text-[10px] max-h-48 overflow-y-auto space-y-1">
              {perfTrace.map((trace, i) => (
                <div key={i} className="flex justify-between items-start border-b border-border/50 pb-1">
                  <div className="flex-1 truncate pr-1">
                    <span className="font-bold">{trace.timestamp}</span> - {trace.label}
                  </div>
                  <div className="font-mono text-primary">{trace.duration}s</div>
                </div>
              ))}
              {perfTrace.length === 0 && <div className="text-center italic text-textSecondary">No traces yet</div>}
            </div>
          )}
        </CollapsibleSection>
      </div>

      <div className="mt-auto pt-4 border-t border-border">
        <button 
          onClick={logout}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-textSecondary rounded-lg hover:bg-danger hover:text-white transition-colors text-sm font-semibold"
        >
          <Power size={16} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
