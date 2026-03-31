import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { Target, TrendingUp, DollarSign } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface ChefPerformance {
  category_id: number;
  category_name: string;
  target_amount: number;
  target_type: string;
  total_qty: number;
  total_revenue: number;
  mtd_qty: number;
  mtd_revenue: number;
  current: number;
  remaining: number;
  achievement_pct: number;
  bonus: number;
}

const ChefTargetsTab: React.FC = () => {
  const [performance, setPerformance] = useState<ChefPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { startDate, endDate, selectedBranches, dataMode, branches } = useFilters();
  const [activeShopId, setActiveShopId] = useState<number | null>(null);

  useEffect(() => {
    if (selectedBranches.length > 0 && !activeShopId) {
      setActiveShopId(selectedBranches[0]);
    }
  }, [selectedBranches]);

  const start = new Date(startDate);
  const year = start.getFullYear();
  const month = start.getMonth() + 1;

  useEffect(() => {
    const fetchData = async () => {
      if (!activeShopId) {
        setPerformance([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const response = await axios.get(
          `${API_BASE_URL}/chef-sales/performance?year=${year}&month=${month}&start_date=${startDate}&end_date=${endDate}&shop_id=${activeShopId}&data_mode=${dataMode}`
        );
        setPerformance(response.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, activeShopId, dataMode, year, month]);

  if (loading && performance.length === 0) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading chef targets...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const totalSales = performance.reduce((acc, curr) => acc + (curr.target_type === 'Sale' ? curr.total_revenue : 0), 0);
  const totalTarget = performance.reduce((acc, curr) => acc + (curr.target_type === 'Sale' ? curr.target_amount : 0), 0);
  const avgAchievement = totalTarget > 0 ? (totalSales / totalTarget) * 100 : 0;

  return (
    <div className="space-y-8">
      {/* Branch Selector */}
      <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
        <div className="flex flex-col md:flex-row gap-6 items-end">
          <div className="w-full md:w-64 space-y-2">
            <label className="text-xs font-bold text-textSecondary uppercase">Select Branch for Targets</label>
            <select 
              value={activeShopId || ''} 
              onChange={(e) => setActiveShopId(Number(e.target.value))}
              className="w-full bg-background border border-border rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              {selectedBranches.map(id => {
                const b = branches.find(branch => branch.Shop_id === id);
                return <option key={id} value={id}>{b?.Shop_name || `Branch ${id}`}</option>;
              })}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Total Chef Sales (Targeted)" value={`Rs. ${totalSales.toLocaleString()}`} icon={<DollarSign size={24} />} />
        <Card title="Total Target" value={`Rs. ${totalTarget.toLocaleString()}`} icon={<Target size={24} />} />
        <Card title="Avg. Achievement" value={`${avgAchievement.toFixed(1)}%`} icon={<TrendingUp size={24} />} />
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-bold text-textPrimary">Chef Performance Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-background text-textSecondary uppercase sticky top-0">
              <tr>
                <th className="px-4 py-3 font-semibold">Category</th>
                <th className="px-4 py-3 font-semibold text-center">Type</th>
                <th className="px-4 py-3 font-semibold text-right">Target</th>
                <th className="px-4 py-3 font-semibold text-right">Current</th>
                <th className="px-4 py-3 font-semibold text-right">Remaining</th>
                <th className="px-4 py-3 font-semibold text-right">Achievement %</th>
                <th className="px-4 py-3 font-semibold text-right">Est. Bonus</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {performance.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4 font-bold text-textPrimary">{item.category_name}</td>
                  <td className="px-4 py-4 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${item.target_type === 'Sale' ? 'bg-primary/10 text-primary' : 'bg-secondary/10 text-secondary'}`}>
                      {item.target_type}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right text-textSecondary">
                    {item.target_type === 'Sale' ? `Rs. ${item.target_amount.toLocaleString()}` : item.target_amount.toLocaleString()}
                  </td>
                  <td className="px-4 py-4 text-right font-bold text-primary">
                    {item.target_type === 'Sale' ? `Rs. ${item.current.toLocaleString()}` : item.current.toLocaleString()}
                  </td>
                  <td className="px-4 py-4 text-right text-textSecondary">
                    {item.target_type === 'Sale' ? `Rs. ${item.remaining.toLocaleString()}` : item.remaining.toLocaleString()}
                  </td>
                  <td className={`px-4 py-4 text-right font-black ${item.achievement_pct >= 100 ? 'text-success' : item.achievement_pct >= 70 ? 'text-warning' : 'text-danger'}`}>
                    {item.achievement_pct.toFixed(1)}%
                  </td>
                  <td className="px-4 py-4 text-right font-bold text-success">
                    {item.bonus > 0 ? `Rs. ${item.bonus.toLocaleString()}` : '-'}
                  </td>
                </tr>
              ))}
              {performance.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-textSecondary italic">No target data found for this branch.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ChefTargetsTab;
