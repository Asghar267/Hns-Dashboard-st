import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend, LineChart, Line
} from 'recharts';
import { DollarSign, Target, TrendingUp, AlertCircle, ShoppingBag, Users } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

interface BranchSummary {
  shop_id: number;
  shop_name: string;
  total_sales: number;
  total_Nt_amount: number;
  monthly_target: number;
  remaining_target: number;
  achievement_pct: number;
  required_daily: number;
  avg_daily: number;
  month_end_projection: number;
  projection_gap: number;
}

interface Highlights {
  chef_top: { product: string; sales: number }[];
  product_top: { product: string; sales: number }[];
  ot_top: { employee_name: string; sales: number }[];
}

interface OrderType {
  order_type: string;
  total_orders: number;
  total_sales: number;
}

const OverviewTab: React.FC = () => {
  const [summary, setSummary] = useState<BranchSummary[]>([]);
  const [highlights, setHighlights] = useState<Highlights | null>(null);
  const [orderTypes, setOrderTypes] = useState<OrderType[]>([]);
  const [dailySales, setDailySales] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();

  useEffect(() => {
    const fetchData = async () => {
      if (selectedBranches.length === 0) {
        setSummary([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const branchParams = selectedBranches.map(id => `branch_ids=${id}`).join('&');
        const commonParams = `start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`;
        
        const [summaryRes, highlightsRes, orderTypesRes, dailyRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/overview/summary?${commonParams}`),
          axios.get(`${API_BASE_URL}/overview/highlights?${commonParams}`),
          axios.get(`${API_BASE_URL}/overview/order-types?${commonParams}`),
          axios.get(`${API_BASE_URL}/overview/daily-sales?${commonParams}`)
        ]);

        setSummary(summaryRes.data);
        setHighlights(highlightsRes.data);
        setOrderTypes(orderTypesRes.data);
        setDailySales(dailyRes.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading overview data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  if (summary.length === 0) {
    return (
      <div className="p-12 text-center bg-surface rounded-lg shadow-card border border-border">
        <AlertCircle size={48} className="mx-auto text-warning mb-4" />
        <h3 className="text-xl font-bold text-textPrimary mb-2">No Data Found</h3>
        <p className="text-textSecondary">No sales records were found for the selected date range and branches. Please adjust your filters in the sidebar.</p>
      </div>
    );
  }

  const totalSales = summary.reduce((acc, curr) => acc + curr.total_Nt_amount, 0);
  const totalTarget = summary.reduce((acc, curr) => acc + curr.monthly_target, 0);
  const totalOrders = orderTypes.reduce((acc, curr) => acc + curr.total_orders, 0);
  const avgOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;
  const totalRemaining = Math.max(0, totalTarget - totalSales);
  const overallAchievement = totalTarget > 0 ? (totalSales / totalTarget) * 100 : 0;
  const totalProjection = summary.reduce((acc, curr) => acc + curr.month_end_projection, 0);
  const totalGap = totalProjection - totalTarget;

  return (
    <div className="space-y-8">
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <Card 
          title="Total Sales" 
          value={`PKR ${totalSales.toLocaleString()}`}
          icon={<DollarSign size={20} />}
        />
        <Card 
          title="Monthly Target" 
          value={`PKR ${totalTarget.toLocaleString()}`}
          icon={<Target size={20} />}
        />
        <Card 
          title="Achievement" 
          value={`${overallAchievement.toFixed(1)}%`}
          icon={<TrendingUp size={20} />}
          trend={{ value: overallAchievement >= 100 ? 'On Track' : 'Below Target', isPositive: overallAchievement >= 100 }}
        />
        <Card 
          title="Projection" 
          value={`PKR ${totalProjection.toLocaleString()}`}
          icon={<TrendingUp size={20} className="text-primary" />}
          trend={{ value: totalGap >= 0 ? `+${totalGap.toLocaleString()}` : totalGap.toLocaleString(), isPositive: totalGap >= 0 }}
        />
        <Card 
          title="Avg Order" 
          value={`PKR ${avgOrderValue.toFixed(0)}`}
          icon={<ShoppingBag size={20} />}
        />
      </div>

      {/* Highlights Leaderboards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2 border-b border-border pb-2">
            <ShoppingBag size={20} className="text-primary" />
            Top Chef Categories
          </h3>
          <div className="space-y-4">
            {highlights?.chef_top.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-textPrimary truncate">{item.product}</span>
                  <span className="font-bold text-primary">PKR {item.sales.toLocaleString()}</span>
                </div>
                <div className="w-full bg-background rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-primary h-full rounded-full" 
                    style={{ width: `${(item.sales / (highlights?.chef_top[0]?.sales || 1)) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2 border-b border-border pb-2">
            <ShoppingBag size={20} className="text-secondary" />
            Top Products
          </h3>
          <div className="space-y-4">
            {highlights?.product_top.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-textPrimary truncate">{item.product}</span>
                  <span className="font-bold text-secondary">PKR {item.sales.toLocaleString()}</span>
                </div>
                <div className="w-full bg-background rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-secondary h-full rounded-full" 
                    style={{ width: `${(item.sales / (highlights?.product_top[0]?.sales || 1)) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2 border-b border-border pb-2">
            <Users size={20} className="text-success" />
            Top Order Takers
          </h3>
          <div className="space-y-4">
            {highlights?.ot_top.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-textPrimary truncate">{item.employee_name}</span>
                  <span className="font-bold text-success">PKR {item.sales.toLocaleString()}</span>
                </div>
                <div className="w-full bg-background rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-success h-full rounded-full" 
                    style={{ width: `${(item.sales / (highlights?.ot_top[0]?.sales || 1)) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Branch Performance Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Branch Performance & Projections</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-4 py-3 border-b border-border">Branch</th>
                <th className="px-4 py-3 border-b border-border text-right">Sales</th>
                <th className="px-4 py-3 border-b border-border text-right">Target</th>
                <th className="px-4 py-3 border-b border-border text-right">Ach %</th>
                <th className="px-4 py-3 border-b border-border text-right">Remaining</th>
                <th className="px-4 py-3 border-b border-border text-right bg-primary/5">Req Daily</th>
                <th className="px-4 py-3 border-b border-border text-right bg-secondary/5">Avg Daily</th>
                <th className="px-4 py-3 border-b border-border text-right bg-success/5">Projection</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {summary.map((branch) => (
                <tr key={branch.shop_id} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4 font-bold text-textPrimary">{branch.shop_name}</td>
                  <td className="px-4 py-4 text-right font-medium">PKR {branch.total_Nt_amount.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-textSecondary">PKR {branch.monthly_target.toLocaleString()}</td>
                  <td className={`px-4 py-4 text-right font-black ${branch.achievement_pct >= 100 ? 'text-success' : branch.achievement_pct >= 70 ? 'text-warning' : 'text-danger'}`}>
                    {branch.achievement_pct.toFixed(1)}%
                  </td>
                  <td className="px-4 py-4 text-right text-textSecondary font-mono text-[11px]">PKR {branch.remaining_target.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right font-bold text-primary bg-primary/5">PKR {branch.required_daily.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className="px-4 py-4 text-right text-secondary bg-secondary/5">PKR {branch.avg_daily.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className={`px-4 py-4 text-right font-black bg-success/5 ${branch.projection_gap >= 0 ? 'text-success' : 'text-danger'}`}>
                    PKR {branch.month_end_projection.toLocaleString(undefined, {maximumFractionDigits: 0})}
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

export default OverviewTab;
