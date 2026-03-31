import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { Target, TrendingUp, Users, DollarSign } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface OTPerformance {
  employee_id: number;
  employee_name: string;
  total_sale: number;
  mtd_sale: number;
  yesterday_sale: number;
  target_amount: number;
  per_day_target: number;
  remaining_target: number;
  next_day_target: number;
  achievement_pct: number;
}

const OTTargetsTab: React.FC = () => {
  const [performance, setPerformance] = useState<OTPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { startDate, endDate, selectedBranches, dataMode, branches } = useFilters();
  const [activeShopId, setActiveShopId] = useState<number | null>(null);

  useEffect(() => {
    if (selectedBranches.length > 0 && !activeShopId) {
      setActiveShopId(selectedBranches[0]);
    }
  }, [selectedBranches]);

  // For targets, we use the year and month from the startDate
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
          `${API_BASE_URL}/order-takers/performance?year=${year}&month=${month}&start_date=${startDate}&end_date=${endDate}&shop_id=${activeShopId}&data_mode=${dataMode}`
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

  if (loading && performance.length === 0) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading targets...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const totalSales = performance.reduce((acc, curr) => acc + curr.total_sale, 0);
  const totalTarget = performance.reduce((acc, curr) => acc + curr.target_amount, 0);
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

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card title="Total OT Sales" value={`Rs. ${totalSales.toLocaleString()}`} icon={<DollarSign size={24} />} />
        <Card title="Total Target" value={`Rs. ${totalTarget.toLocaleString()}`} icon={<Target size={24} />} />
        <Card title="Number of OTs" value={performance.length} icon={<Users size={24} />} />
        <Card title="Avg. Achievement" value={`${avgAchievement.toFixed(1)}%`} icon={<TrendingUp size={24} />} />
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-bold text-textPrimary">OT Performance & Projections</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-background text-textSecondary uppercase sticky top-0">
              <tr>
                <th className="px-4 py-3 font-semibold">OT Name</th>
                <th className="px-4 py-3 font-semibold text-right">Target</th>
                <th className="px-4 py-3 font-semibold text-right">Daily Target</th>
                <th className="px-4 py-3 font-semibold text-right">Yesterday</th>
                <th className="px-4 py-3 font-semibold text-right">MTD Sale</th>
                <th className="px-4 py-3 font-semibold text-right">Rem. Target</th>
                <th className="px-4 py-3 font-semibold text-right">Next Day Tgt</th>
                <th className="px-4 py-3 font-semibold text-right">Current Sale</th>
                <th className="px-4 py-3 font-semibold text-right">Achievement %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {performance.map((ot) => (
                <tr key={ot.employee_id} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4 font-bold text-textPrimary">{ot.employee_name}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">Rs. {ot.target_amount.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">Rs. {ot.per_day_target.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className="px-4 py-4 text-right font-medium text-primary">Rs. {ot.yesterday_sale.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">Rs. {ot.mtd_sale.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">Rs. {ot.remaining_target.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right font-bold text-secondary">Rs. {ot.next_day_target.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className="px-4 py-4 text-right font-bold text-primary">Rs. {ot.total_sale.toLocaleString()}</td>
                  <td className={`px-4 py-4 text-right font-black ${ot.achievement_pct >= 100 ? 'text-success' : ot.achievement_pct >= 70 ? 'text-warning' : 'text-danger'}`}>
                    {ot.achievement_pct.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OTTargetsTab;
