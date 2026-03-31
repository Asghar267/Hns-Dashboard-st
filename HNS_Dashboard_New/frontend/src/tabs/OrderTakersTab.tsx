import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { Users, DollarSign, TrendingUp, Search, Download } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';
const COLORS = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'];

interface OTSummary {
  shop_id: number;
  shop_name: string;
  employee_id: number;
  employee_name: string;
  employee_code: string;
  total_sale: number;
  total_orders: number;
  target_amount: number;
  achievement_pct: number;
  remaining_target: number;
  next_day_target: number;
  performance_index: number;
}

const OrderTakersTab: React.FC = () => {
  const [data, setData] = useState<OTSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();

  useEffect(() => {
    const fetchData = async () => {
      if (selectedBranches.length === 0) {
        setData([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const branchParams = selectedBranches.map(id => `branch_ids=${id}`).join('&');
        const response = await axios.get(
          `${API_BASE_URL}/order-takers/summary?start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`
        );
        setData(response.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading OT data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const filteredData = data.filter(item => 
    item.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.employee_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalSales = data.reduce((acc, curr) => acc + curr.total_sale, 0);
  const totalTarget = data.reduce((acc, curr) => acc + curr.target_amount, 0);
  const overallAchievement = totalTarget > 0 ? (totalSales / totalTarget) * 100 : 0;
  const activeOTs = data.length;

  const top10 = [...data].sort((a, b) => b.total_sale - a.total_sale).slice(0, 10);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-textPrimary">Order Taker Performance</h2>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card 
          title="Total OT Sales" 
          value={`PKR ${totalSales.toLocaleString()}`}
          icon={<DollarSign size={24} />}
        />
        <Card 
          title="Group Target" 
          value={`PKR ${totalTarget.toLocaleString()}`}
          icon={<Target size={24} />}
        />
        <Card 
          title="Achievement" 
          value={`${overallAchievement.toFixed(1)}%`}
          icon={<TrendingUp size={24} />}
          trend={{ value: overallAchievement >= 100 ? 'Target Met' : 'In Progress', isPositive: overallAchievement >= 100 }}
        />
        <Card 
          title="Active OTs" 
          value={activeOTs.toLocaleString()}
          icon={<Users size={24} />}
        />
      </div>

      {/* Detailed Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-4 bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">All Order Takers & Cashiers</h3>
          
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
              <input 
                type="text"
                placeholder="Search by name or code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-background border border-border rounded-md pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <button 
              onClick={() => exportToCSV(data, 'order_takers_report')}
              className="flex items-center space-x-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors text-sm font-semibold"
            >
              <Download size={16} />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-4 py-3 border-b border-border">OT Name</th>
                <th className="px-4 py-3 border-b border-border">Code</th>
                <th className="px-4 py-3 border-b border-border">Branch</th>
                <th className="px-4 py-3 border-b border-border text-right">Orders</th>
                <th className="px-4 py-3 border-b border-border text-right">Sales</th>
                <th className="px-4 py-3 border-b border-border text-right">Target</th>
                <th className="px-4 py-3 border-b border-border text-right">Ach %</th>
                <th className="px-4 py-3 border-b border-border text-right bg-primary/5">Next Day Target</th>
                <th className="px-4 py-3 border-b border-border text-right bg-success/5">Perf Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredData.map((ot, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4 font-bold text-textPrimary">{ot.employee_name}</td>
                  <td className="px-4 py-4 text-textSecondary font-mono text-[11px]">{ot.employee_code}</td>
                  <td className="px-4 py-4 text-textSecondary text-[11px]">{ot.shop_name}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">{ot.total_orders.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right font-medium text-textPrimary">PKR {ot.total_sale.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">PKR {ot.target_amount.toLocaleString()}</td>
                  <td className={`px-4 py-4 text-right font-black ${ot.achievement_pct >= 100 ? 'text-success' : ot.achievement_pct >= 70 ? 'text-warning' : 'text-danger'}`}>
                    {ot.achievement_pct.toFixed(1)}%
                  </td>
                  <td className="px-4 py-4 text-right font-bold text-primary bg-primary/5">PKR {ot.next_day_target.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className={`px-4 py-4 text-right font-black bg-success/5 ${ot.performance_index >= 100 ? 'text-success' : ot.performance_index >= 80 ? 'text-warning' : 'text-danger'}`}>
                    {ot.performance_index.toFixed(1)}%
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-textSecondary italic">No order takers found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OrderTakersTab;
