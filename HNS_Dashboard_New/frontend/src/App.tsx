import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import OverviewTab from './tabs/OverviewTab';
import QRCommissionTab from './tabs/QRCommissionTab';
import ChefSalesTab from './tabs/ChefSalesTab';
import OrderTakersTab from './tabs/OrderTakersTab';
import OTTargetsTab from './tabs/OTTargetsTab';
import ChefTargetsTab from './tabs/ChefTargetsTab';
import KhaddaDiagnosticsTab from './tabs/KhaddaDiagnosticsTab';
import PivotTablesTab from './tabs/PivotTablesTab';
import CategoryCoverageTab from './tabs/CategoryCoverageTab';
import TrendsAnalyticsTab from './tabs/TrendsAnalyticsTab';
import MaterialCostCommissionTab from './tabs/MaterialCostCommissionTab';
import RamzanDealsTab from './tabs/RamzanDealsTab';
import AdminTab from './tabs/AdminTab';
import Login from './components/Login';
import { AuthProvider, useAuth } from './api/AuthContext';
import { FilterProvider } from './api/FilterContext';
import Header from './components/Header';

const TABS = {
  "Overview": <OverviewTab />,
  "QR Commission": <QRCommissionTab />,
  "Khadda Diagnostics": <KhaddaDiagnosticsTab />,
  "Chef Sales": <ChefSalesTab />,
  "Order Takers": <OrderTakersTab />,
  "OT Targets": <OTTargetsTab />,
  "Chef Targets": <ChefTargetsTab />,
  "Pivot Tables": <PivotTablesTab />,
  "Category Coverage": <CategoryCoverageTab />,
  "Trends & Analytics": <TrendsAnalyticsTab />,
  "Material Cost Commission": <MaterialCostCommissionTab />,
  "Ramzan Deals": <RamzanDealsTab />,
  "Admin": <AdminTab />,
};

const AppContent: React.FC = () => {
  const { user } = useAuth();
  
  // Temporarily bypass login for testing as requested
  const mockUser = { username: 'admin00==', role: 'admin', allowed_tabs: Object.keys(TABS) };
  const effectiveUser = user || mockUser;

  // Filter tabs based on user's allowed_tabs
  const allowedTabs = effectiveUser.role === 'admin' 
    ? Object.keys(TABS) 
    : (effectiveUser.allowed_tabs && effectiveUser.allowed_tabs.length > 0 
        ? effectiveUser.allowed_tabs 
        : ["Overview"]);

  const [activeTab, setActiveTab] = useState<keyof typeof TABS>(allowedTabs[0] as keyof typeof TABS);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <Header title={activeTab} />
        <div className="flex-1 overflow-y-auto p-8">
          <div className="flex space-x-2 mb-6 bg-surface p-2 rounded-lg border border-border overflow-x-auto">
            {allowedTabs.map(tab => (
              <button 
                key={tab}
                onClick={() => setActiveTab(tab as keyof typeof TABS)}
                className={`px-4 py-2 rounded-md text-xs font-semibold whitespace-nowrap transition-all ${
                  activeTab === tab 
                    ? 'bg-primary text-white shadow-sm' 
                    : 'text-textSecondary hover:bg-background'
                }`}>
                {tab}
              </button>
            ))}
          </div>
          {TABS[activeTab]}
        </div>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <FilterProvider>
        <AppContent />
      </FilterProvider>
    </AuthProvider>
  );
};

export default App;
