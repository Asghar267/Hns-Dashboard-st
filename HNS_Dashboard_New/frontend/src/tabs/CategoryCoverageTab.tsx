import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { Layers, TrendingUp, DollarSign, Download } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';
const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#0ea5e9', '#dc2626', '#7c3aed'];

interface CategoryData {
  shop_name: string;
  category_name: string;
  category_sales: number;
}

const CategoryCoverageTab: React.FC = () => {
  const [data, setData] = useState<CategoryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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
        const response = await axios.get(`${API_BASE_URL}/category/coverage?start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`);
        setData(response.data);
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

  const totalSales = data.reduce((acc, curr) => acc + curr.category_sales, 0);
  const categoryCount = [...new Set(data.map(d => d.category_name))].length;
  const topCategory = [...data].sort((a, b) => b.category_sales - a.category_sales)[0];

  const branches = [...new Set(data.map(d => d.shop_name))];
  const categories = [...new Set(data.map(d => d.category_name))].slice(0, 10);
  
  const chartData = branches.map(branch => {
    const entry: any = { name: branch };
    categories.forEach(cat => {
      const match = data.find(d => d.shop_name === branch && d.category_name === cat);
      entry[cat] = match ? match.category_sales : 0;
    });
    return entry;
  });

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Total Category Sales" value={`PKR ${totalSales.toLocaleString()}`} icon={<DollarSign size={24} />} />
        <Card title="Active Categories" value={categoryCount.toString()} icon={<Layers size={24} />} />
        <Card title="Top Performing Category" value={topCategory?.category_name || 'N/A'} icon={<TrendingUp size={24} />} />
      </div>

      <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
        <h3 className="text-lg font-bold text-textPrimary mb-6 flex items-center gap-2">
          <Layers size={20} className="text-primary" />
          Category Sales by Branch (Top 10)
        </h3>
        <div className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{fontSize: 11, fill: '#64748b'}} />
              <YAxis tickFormatter={(val) => `PKR ${val/1000}k`} tick={{fontSize: 11, fill: '#64748b'}} />
              <Tooltip formatter={(val: number) => `PKR ${val.toLocaleString()}`} />
              <Legend wrapperStyle={{fontSize: '11px'}} />
              {categories.map((cat, idx) => (
                <Bar key={cat} dataKey={cat} stackId="a" fill={COLORS[idx % COLORS.length]} radius={[2, 2, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex justify-between items-center bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Detailed Category Coverage</h3>
          <button 
            onClick={() => exportToCSV(data, 'category_coverage')}
            className="flex items-center space-x-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors text-sm font-semibold"
          >
            <Download size={16} />
            <span>Export CSV</span>
          </button>
        </div>
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-6 py-3 border-b border-border">Branch</th>
                <th className="px-6 py-3 border-b border-border">Category</th>
                <th className="px-6 py-3 border-b border-border text-right">Sales</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 text-textSecondary">{item.shop_name}</td>
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.category_name}</td>
                  <td className="px-6 py-4 text-right font-black text-primary">PKR {item.category_sales.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CategoryCoverageTab;
