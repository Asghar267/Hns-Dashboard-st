import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { Search, Info, AlertTriangle, CheckCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface KhaddaData {
  split_report: any[];
  daily_summary: any[];
}

const KhaddaDiagnosticsTab: React.FC = () => {
  const [data, setData] = useState<KhaddaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [commissionRate, setCommissionRate] = useState(2.0);
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();

  const isKhaddaSelected = selectedBranches.includes(2);

  useEffect(() => {
    const fetchData = async () => {
      if (!isKhaddaSelected) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const response = await axios.get(
          `${API_BASE_URL}/diagnostics/khadda?start_date=${startDate}&end_date=${endDate}&commission_rate=${commissionRate}&data_mode=${dataMode}`
        );
        setData(response.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isKhaddaSelected, dataMode, commissionRate]);

  if (!isKhaddaSelected) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-surface rounded-lg border border-dashed border-border p-8">
        <Info size={48} className="text-primary mb-4" />
        <h3 className="text-xl font-bold text-textPrimary">Khadda Main Branch Not Selected</h3>
        <p className="text-textSecondary mt-2">Please select 'Khadda Main Branch' (Shop ID: 2) in the filters to view diagnostics.</p>
      </div>
    );
  }

  if (loading && !data) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const filteredSplit = data?.split_report.filter(item => 
    item.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.employee_code?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const totalWithoutBlink = filteredSplit.reduce((acc, curr) => acc + curr.total_sales_without_blinkco, 0);
  const totalCommWithoutBlink = filteredSplit.reduce((acc, curr) => acc + curr.commission_without_blinkco_sales, 0);

  return (
    <div className="space-y-8">
      <div className="bg-surface p-6 rounded-lg shadow-card border border-border">
        <div className="flex flex-col md:flex-row gap-6 items-end">
          <div className="flex-1 space-y-2">
            <label className="text-xs font-bold text-textSecondary uppercase">Search Employee</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
              <input 
                type="text"
                placeholder="Name or Code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-background border border-border rounded-md pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
          </div>
          <div className="w-full md:w-48 space-y-2">
            <label className="text-xs font-bold text-textSecondary uppercase">Commission Rate (%)</label>
            <input 
              type="number"
              step="0.1"
              value={commissionRate}
              onChange={(e) => setCommissionRate(parseFloat(e.target.value))}
              className="w-full bg-background border border-border rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card 
          title="Sales Without Blinkco" 
          value={`PKR ${totalWithoutBlink.toLocaleString()}`}
          icon={<AlertTriangle size={24} className="text-warning" />}
        />
        <Card 
          title="Commission (Non-Blinkco)" 
          value={`PKR ${totalCommWithoutBlink.toLocaleString()}`}
          icon={<CheckCircle size={24} className="text-success" />}
        />
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Khadda Branch: Sales Split Report</h3>
        </div>
        <div className="overflow-x-auto max-h-[400px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-4 py-3 border-b border-border">Employee</th>
                <th className="px-4 py-3 border-b border-border text-right">Total Trans</th>
                <th className="px-4 py-3 border-b border-border text-right">Blinkco Trans</th>
                <th className="px-4 py-3 border-b border-border text-right">Total Sales</th>
                <th className="px-4 py-3 border-b border-border text-right">Blinkco Sales</th>
                <th className="px-4 py-3 border-b border-border text-right">Non-Blinkco Sales</th>
                <th className="px-4 py-3 border-b border-border text-right">Commission</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredSplit.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4">
                    <div className="font-bold text-textPrimary">{item.employee_name}</div>
                    <div className="text-[10px] text-textSecondary font-mono">{item.employee_code}</div>
                  </td>
                  <td className="px-4 py-4 text-right">{item.total_transactions_all}</td>
                  <td className="px-4 py-4 text-right">{item.total_transactions_blinkco}</td>
                  <td className="px-4 py-4 text-right">PKR {item.total_sales_all.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-primary">PKR {item.total_sales_blinkco.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right font-bold text-warning">PKR {item.total_sales_without_blinkco.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right font-bold text-success">PKR {item.commission_without_blinkco_sales.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Daily Employee Summary (Blinkco)</h3>
        </div>
        <div className="overflow-x-auto max-h-[400px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-4 py-3 border-b border-border">Date</th>
                <th className="px-4 py-3 border-b border-border">Employee</th>
                <th className="px-4 py-3 border-b border-border text-right">TX Count</th>
                <th className="px-4 py-3 border-b border-border text-right">Total Sale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data?.daily_summary.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-4 py-4 text-textSecondary font-mono text-[11px]">{item.sale_day}</td>
                  <td className="px-4 py-4 font-bold text-textPrimary">{item.employee_name}</td>
                  <td className="px-4 py-4 text-right">{item.tx_count}</td>
                  <td className="px-4 py-4 text-right font-bold text-primary">PKR {item.total_sale.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default KhaddaDiagnosticsTab;
