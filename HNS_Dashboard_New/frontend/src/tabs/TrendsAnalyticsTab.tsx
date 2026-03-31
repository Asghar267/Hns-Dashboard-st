import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, Legend, Cell
} from 'recharts';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { TrendingUp, Clock, Calendar as CalendarIcon, DollarSign } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';
const COLORS = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff'];

interface MonthlyTrend {
  period_date: string;
  total_sales: number;
}

interface DOWTrend {
  day_name: string;
  day_index: number;
  total_sales: number;
  total_orders: number;
}

interface HourlyTrend {
  hour: number;
  total_sales: number;
  total_orders: number;
}

const TrendsAnalyticsTab: React.FC = () => {
  const [trends, setTrends] = useState<MonthlyTrend[]>([]);
  const [dowTrends, setDowTrends] = useState<DOWTrend[]>([]);
  const [hourlyTrends, setHourlyTrends] = useState<HourlyTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();

  useEffect(() => {
    const fetchData = async () => {
      if (selectedBranches.length === 0) {
        setTrends([]);
        setDowTrends([]);
        setHourlyTrends([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const branchParams = selectedBranches.map(id => `branch_ids=${id}`).join('&');
        const commonParams = `start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`;
        
        const [trendsRes, dowRes, hourlyRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/trends/monthly?${commonParams}`),
          axios.get(`${API_BASE_URL}/trends/day-of-week?${commonParams}`),
          axios.get(`${API_BASE_URL}/trends/hourly?${commonParams}`)
        ]);

        setTrends(trendsRes.data);
        setDowTrends(dowRes.data);
        setHourlyTrends(hourlyRes.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const totalSales = trends.reduce((acc, curr) => acc + curr.total_sales, 0);
  const peakHour = [...hourlyTrends].sort((a, b) => b.total_sales - a.total_sales)[0]?.hour || 0;
  const peakDay = [...dowTrends].sort((a, b) => b.total_sales - a.total_sales)[0]?.day_name || 'N/A';

  return (
    <div className="space-y-8">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Total Sales in Period" value={`PKR ${totalSales.toLocaleString()}`} icon={<DollarSign size={24} />} />
        <Card title="Peak Sales Day" value={peakDay} icon={<CalendarIcon size={24} />} />
        <Card title="Peak Hour" value={`${peakHour}:00`} icon={<Clock size={24} />} />
      </div>

      <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
        <h3 className="text-lg font-bold text-textPrimary mb-6 flex items-center gap-2">
          <TrendingUp size={20} className="text-primary" />
          Monthly Growth Trend
        </h3>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trends} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <defs>
                <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis 
                dataKey="period_date" 
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', year: '2y' })}
                tick={{fontSize: 11, fill: '#64748b'}}
              />
              <YAxis tickFormatter={(val) => `PKR ${val/1000}k`} tick={{fontSize: 11, fill: '#64748b'}} />
              <Tooltip formatter={(val: number) => `PKR ${val.toLocaleString()}`} />
              <Area type="monotone" dataKey="total_sales" name="Sales" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#colorSales)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
          <h3 className="text-lg font-bold text-textPrimary mb-6 flex items-center gap-2">
            <CalendarIcon size={20} className="text-secondary" />
            Performance by Day of Week
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dowTrends}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="day_name" tick={{fontSize: 11, fill: '#64748b'}} />
                <YAxis tickFormatter={(val) => `PKR ${val/1000}k`} tick={{fontSize: 11, fill: '#64748b'}} />
                <Tooltip formatter={(val: number) => `PKR ${val.toLocaleString()}`} />
                <Bar dataKey="total_sales" radius={[4, 4, 0, 0]}>
                  {dowTrends.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
          <h3 className="text-lg font-bold text-textPrimary mb-6 flex items-center gap-2">
            <Clock size={20} className="text-success" />
            Hourly Sales Distribution
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={hourlyTrends}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="hour" tickFormatter={(h) => `${h}:00`} tick={{fontSize: 11, fill: '#64748b'}} />
                <YAxis tickFormatter={(val) => `PKR ${val/1000}k`} tick={{fontSize: 11, fill: '#64748b'}} />
                <Tooltip formatter={(val: number) => `PKR ${val.toLocaleString()}`} />
                <Area type="monotone" dataKey="total_sales" stroke="#10b981" fill="#10b981" fillOpacity="0.1" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrendsAnalyticsTab;
