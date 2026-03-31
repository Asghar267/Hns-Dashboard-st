import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend
} from 'recharts';
import { ShoppingBag, DollarSign, Package, Search, Download } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';
const COLORS = ['#10b981', '#059669', '#047857', '#065f46', '#064e3b'];

interface ChefSummary {
  branch: string;
  product: string;
  total_qty: number;
  total_revenue: number;
  target_amount?: number;
  achievement_pct?: number;
}

const ChefSalesTab: React.FC = () => {
  const [data, setData] = useState<ChefSummary[]>([]);
  const [performance, setPerformance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [minSales, setMinSales] = useState(0);
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
        
        // Fetch both summary and performance (targets)
        const start = new Date(startDate);
        const year = start.getFullYear();
        const month = start.getMonth() + 1;
        
        const [summaryRes, performanceRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/chef-sales/summary?start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`),
          axios.get(`${API_BASE_URL}/chef-sales/performance?year=${year}&month=${month}&start_date=${startDate}&end_date=${endDate}&shop_id=${selectedBranches[0]}&data_mode=${dataMode}`)
        ]);

        setData(summaryRes.data);
        setPerformance(performanceRes.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading chef data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  // Aggregate by product across branches for summary and charts
  const productSummary = data.reduce((acc: any[], curr) => {
    const existing = acc.find(item => item.product === curr.product);
    const perf = performance.find(p => p.category_name === curr.product);
    
    if (existing) {
      existing.total_qty += curr.total_qty;
      existing.total_revenue += curr.total_revenue;
    } else {
      acc.push({ 
        product: curr.product, 
        total_qty: curr.total_qty, 
        total_revenue: curr.total_revenue,
        target_amount: perf?.target_amount || 0,
        achievement_pct: perf?.achievement_pct || 0
      });
    }
    return acc;
  }, []).sort((a, b) => b.total_revenue - a.total_revenue);

  const filteredSummary = productSummary.filter(item => 
    item.product.toLowerCase().includes(searchTerm.toLowerCase()) &&
    item.total_revenue >= minSales
  );

  const totalSales = productSummary.reduce((acc, curr) => acc + curr.total_revenue, 0);
  const totalTarget = productSummary.reduce((acc, curr) => acc + curr.target_amount, 0);
  const overallAchievement = totalTarget > 0 ? (totalSales / totalTarget) * 100 : 0;
  const totalQty = productSummary.reduce((acc, curr) => acc + curr.total_qty, 0);
  const uniqueProducts = productSummary.length;

  const top15 = filteredSummary.slice(0, 15);
  const top10 = filteredSummary.slice(0, 10);

  return (
    <div className="space-y-8">
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card 
          title="Total Chef Sales" 
          value={`PKR ${totalSales.toLocaleString()}`}
          icon={<DollarSign size={24} />}
        />
        <Card 
          title="Category Targets" 
          value={`PKR ${totalTarget.toLocaleString()}`}
          icon={<Package size={24} />}
        />
        <Card 
          title="Achievement" 
          value={`${overallAchievement.toFixed(1)}%`}
          icon={<TrendingUp size={24} />}
          trend={{ value: overallAchievement >= 100 ? 'Bonus Active' : 'Below Target', isPositive: overallAchievement >= 100 }}
        />
        <Card 
          title="Total Qty" 
          value={totalQty.toLocaleString()}
          icon={<ShoppingBag size={24} />}
        />
      </div>

      {/* Leaderboard Chart */}
      <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
          <ShoppingBag size={20} className="text-primary" />
          Top 10 Performing Categories
        </h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={top10} layout="vertical" margin={{ left: 50, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
              <XAxis type="number" tickFormatter={(val) => `PKR ${val/1000}k`} />
              <YAxis type="category" dataKey="product" width={120} tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip formatter={(val: number) => `PKR ${val.toLocaleString()}`} />
              <Bar dataKey="total_revenue" radius={[0, 4, 4, 0]}>
                {top10.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Product Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-4 bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Category Breakdown & Targets</h3>
          
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
              <input 
                type="text"
                placeholder="Search category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-background border border-border rounded-md pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <button 
              onClick={() => exportToCSV(productSummary, 'chef_sales_report')}
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
                <th className="px-4 py-3 border-b border-border">Category</th>
                <th className="px-4 py-3 border-b border-border text-right">Qty</th>
                <th className="px-4 py-3 border-b border-border text-right">Revenue</th>
                <th className="px-4 py-3 border-b border-border text-right">Target</th>
                <th className="px-4 py-3 border-b border-border text-right">Ach %</th>
                <th className="px-4 py-3 border-b border-border text-right bg-success/5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredSummary.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4 font-bold text-textPrimary">{item.product}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">{item.total_qty.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right font-medium text-textPrimary">PKR {item.total_revenue.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">
                    {item.target_amount && item.target_amount > 0 ? `PKR ${item.target_amount.toLocaleString()}` : '-'}
                  </td>
                  <td className={`px-4 py-4 text-right font-black ${item.achievement_pct && item.achievement_pct >= 100 ? 'text-success' : item.achievement_pct && item.achievement_pct >= 70 ? 'text-warning' : 'text-textSecondary'}`}>
                    {item.achievement_pct && item.achievement_pct > 0 ? `${item.achievement_pct.toFixed(1)}%` : '-'}
                  </td>
                  <td className="px-4 py-4 text-right bg-success/5">
                    {item.achievement_pct && item.achievement_pct >= 100 ? (
                      <span className="px-2 py-1 bg-success/10 text-success rounded text-[10px] font-black uppercase">Bonus Hit</span>
                    ) : (
                      <span className="text-[10px] text-textSecondary uppercase font-bold">Pending</span>
                    )}
                  </td>
                </tr>
              ))}
              {filteredSummary.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-textSecondary italic">No product categories found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Branch Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden">
        <div className="p-6 border-b border-border">
          <h3 className="text-lg font-bold text-textPrimary">Branch-wise Category Performance</h3>
        </div>
        <div className="overflow-x-auto max-h-[600px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-xs uppercase sticky top-0">
              <tr>
                <th className="px-6 py-3 font-semibold">Branch</th>
                <th className="px-6 py-3 font-semibold">Product Category</th>
                <th className="px-6 py-3 font-semibold text-right">Quantity</th>
                <th className="px-6 py-3 font-semibold text-right">Total Sales</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.sort((a, b) => a.branch.localeCompare(b.branch)).map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 text-textSecondary">{item.branch}</td>
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.product}</td>
                  <td className="px-6 py-4 text-right text-textSecondary">{item.total_qty.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-bold text-primary">Rs. {item.total_revenue.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ChefSalesTab;
