import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { ShoppingBag, DollarSign, Download } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';

interface RamzanSummary {
  shop_name: string;
  Product_code: string;
  item_name: string;
  total_qty: number;
  total_sales: number;
}

const RamzanDealsTab: React.FC = () => {
  const [data, setData] = useState<RamzanSummary[]>([]);
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
        const response = await axios.get(`${API_BASE_URL}/ramzan/summary?start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`);
        setData(response.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading Ramzan deals...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const totalSales = data.reduce((acc, curr) => acc + curr.total_sales, 0);
  const totalQty = data.reduce((acc, curr) => acc + curr.total_qty, 0);

  // Product-wise overall
  const productOverall = data.reduce((acc: any[], curr) => {
    const existing = acc.find(item => item.Product_code === curr.Product_code);
    if (existing) {
      existing.total_qty += curr.total_qty;
      existing.total_sales += curr.total_sales;
    } else {
      acc.push({ Product_code: curr.Product_code, item_name: curr.item_name, total_qty: curr.total_qty, total_sales: curr.total_sales });
    }
    return acc;
  }, []).sort((a, b) => b.total_sales - a.total_sales);

  return (
    <div className="space-y-8">
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Total Deals Sales" value={`PKR ${totalSales.toLocaleString()}`} icon={<DollarSign size={24} />} />
        <Card title="Total Quantity" value={totalQty.toLocaleString()} icon={<ShoppingBag size={24} />} />
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex justify-between items-center bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Branch-wise Sales Breakdown</h3>
          <button 
            onClick={() => exportToCSV(data, 'ramzan_deals_branch_wise')}
            className="flex items-center space-x-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors text-sm font-semibold"
          >
            <Download size={16} />
            <span>Export CSV</span>
          </button>
        </div>
        <div className="overflow-x-auto max-h-[400px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-6 py-3 border-b border-border">Branch</th>
                <th className="px-6 py-3 border-b border-border">Code</th>
                <th className="px-6 py-3 border-b border-border">Item Name</th>
                <th className="px-6 py-3 border-b border-border text-right">Quantity</th>
                <th className="px-6 py-3 border-b border-border text-right">Total Sales</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 text-textSecondary">{item.shop_name}</td>
                  <td className="px-6 py-4 font-mono text-[11px] text-textSecondary">{item.Product_code}</td>
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.item_name}</td>
                  <td className="px-6 py-4 text-right">{item.total_qty.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-black text-primary">PKR {item.total_sales.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex justify-between items-center bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Product-wise Overall Sales</h3>
          <button 
            onClick={() => exportToCSV(productOverall, 'ramzan_deals_product_wise')}
            className="flex items-center space-x-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors text-sm font-semibold"
          >
            <Download size={16} />
            <span>Export CSV</span>
          </button>
        </div>
        <div className="overflow-x-auto max-h-[400px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-6 py-3 border-b border-border">Code</th>
                <th className="px-6 py-3 border-b border-border">Item Name</th>
                <th className="px-6 py-3 border-b border-border text-right">Quantity</th>
                <th className="px-6 py-3 border-b border-border text-right">Total Sales</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {productOverall.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 font-mono text-[11px] text-textSecondary">{item.Product_code}</td>
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.item_name}</td>
                  <td className="px-6 py-4 text-right">{item.total_qty.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-black text-primary">PKR {item.total_sales.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );};

export default RamzanDealsTab;
