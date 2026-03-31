import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { Search, Download, DollarSign, ShoppingBag, TrendingUp, CheckCircle, XCircle, QrCode } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';

interface QRReportItem {
  shop_id: number;
  shop_name: string;
  employee_id: number;
  employee_code: string;
  employee_name: string;
  total_transactions_all: number;
  total_sales_all: number;
  total_transactions_blinkco: number;
  total_sales_blinkco: number;
  indoge_blink_sales: number;
  total_sales_without_blinkco: number;
  blink_match_pct: number;
  blink_match_ok: boolean;
  commission_total_sales: number;
  commission_blinkco_sales: number;
  commission_without_blinkco_sales: number;
}

const QRCommissionTab: React.FC = () => {
  const [report, setReport] = useState<QRReportItem[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [commissionRate, setCommissionRate] = useState(2.0);
  const [searchTerm, setSearchTerm] = useState('');
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();

  useEffect(() => {
    const fetchData = async () => {
      if (selectedBranches.length === 0) {
        setReport([]);
        setTransactions([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const branchParams = selectedBranches.map(id => `branch_ids=${id}`).join('&');
        const commonParams = `start_date=${startDate}&end_date=${endDate}&${branchParams}&commission_rate=${commissionRate}&data_mode=${dataMode}`;
        
        const [reportRes, transRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/qr-commission/report?${commonParams}`),
          axios.get(`${API_BASE_URL}/qr-commission/detailed-transactions?${commonParams}`)
        ]);

        setReport(reportRes.data);
        setTransactions(transRes.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, commissionRate, dataMode]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading commission data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const filteredReport = report.filter(item => 
    item.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.employee_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalSales = report.reduce((acc, curr) => acc + curr.total_sales_all, 0);
  const totalBlinkSales = report.reduce((acc, curr) => acc + curr.total_sales_blinkco, 0);
  const totalComm = report.reduce((acc, curr) => acc + curr.commission_total_sales, 0);

  return (
    <div className="space-y-8">
      {/* Commission Control */}
      <div className="bg-surface p-6 rounded-lg shadow-card border border-border flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex-1 max-w-xs space-y-2">
          <label className="text-xs font-bold text-textSecondary uppercase">Commission Rate (%)</label>
          <input 
            type="number"
            value={commissionRate}
            onChange={(e) => setCommissionRate(parseFloat(e.target.value))}
            className="w-full bg-background border border-border rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
            step="0.1"
          />
        </div>
        <div className="flex gap-4">
          <Card title="Total Sales" value={`PKR ${totalSales.toLocaleString()}`} icon={<DollarSign size={20} />} />
          <Card title="Blink Sales" value={`PKR ${totalBlinkSales.toLocaleString()}`} icon={<QrCode size={20} />} />
          <Card title="Total Comm" value={`PKR ${totalComm.toLocaleString()}`} icon={<TrendingUp size={20} />} />
        </div>
      </div>

      {/* Split Report Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-4 bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">QR Commission Split Report</h3>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
              <input 
                type="text"
                placeholder="Search employee..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-background border border-border rounded-md pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <button 
              onClick={() => exportToCSV(report, 'qr_commission_split')}
              className="flex items-center space-x-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors text-sm font-semibold"
            >
              <Download size={16} />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[11px]">
            <thead className="bg-background text-textSecondary uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-4 py-3 border-b border-border">Employee</th>
                <th className="px-4 py-3 border-b border-border">Branch</th>
                <th className="px-4 py-3 border-b border-border text-right">All Tx</th>
                <th className="px-4 py-3 border-b border-border text-right">Blink Tx</th>
                <th className="px-4 py-3 border-b border-border text-right">All Sales</th>
                <th className="px-4 py-3 border-b border-border text-right text-primary">Blink (Cand)</th>
                <th className="px-4 py-3 border-b border-border text-right text-secondary">Blink (Indo)</th>
                <th className="px-4 py-3 border-b border-border text-right">Match %</th>
                <th className="px-4 py-3 border-b border-border text-right bg-success/5">Total Comm</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredReport.sort((a, b) => b.total_sales_all - a.total_sales_all).map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-bold text-textPrimary">{item.employee_name}</div>
                    <div className="text-[9px] text-textSecondary font-mono">{item.employee_code}</div>
                  </td>
                  <td className="px-4 py-3 text-textSecondary">{item.shop_name}</td>
                  <td className="px-4 py-3 text-right">{item.total_transactions_all}</td>
                  <td className="px-4 py-3 text-right">{item.total_transactions_blinkco}</td>
                  <td className="px-4 py-3 text-right font-medium">PKR {item.total_sales_all.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-primary font-bold">PKR {item.total_sales_blinkco.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-secondary">PKR {item.indoge_blink_sales.toLocaleString()}</td>
                  <td className={`px-4 py-3 text-right font-black ${item.blink_match_ok ? 'text-success' : 'text-danger'}`}>
                    {item.blink_match_pct}%
                  </td>
                  <td className="px-4 py-3 text-right font-black text-success bg-success/5">PKR {item.commission_total_sales.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transaction Matching */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Transaction-Level Price Match</h3>
        </div>
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left text-[10px]">
            <thead className="bg-background text-textSecondary uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-4 py-3 border-b border-border">Ref ID</th>
                <th className="px-4 py-3 border-b border-border">Date</th>
                <th className="px-4 py-3 border-b border-border">Branch</th>
                <th className="px-4 py-3 border-b border-border">Employee</th>
                <th className="px-4 py-3 border-b border-border text-right">POS Sale</th>
                <th className="px-4 py-3 border-b border-border text-right">Indoge Sale</th>
                <th className="px-4 py-3 border-b border-border text-right">Diff</th>
                <th className="px-4 py-3 border-b border-border text-right">Match</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {transactions.map((tx, idx) => {
                const isMatch = Math.abs(tx.difference || 0) < 1;
                return (
                  <tr key={idx} className="hover:bg-background transition-colors">
                    <td className="px-4 py-3 font-mono text-primary">{tx.external_ref_id}</td>
                    <td className="px-4 py-3 text-textSecondary">{new Date(tx.sale_date).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-textSecondary">{tx.shop_name}</td>
                    <td className="px-4 py-3 font-medium">{tx.employee_name}</td>
                    <td className="px-4 py-3 text-right font-bold">PKR {tx.total_sale.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-secondary">PKR {tx.Indoge_total_price?.toLocaleString() || 0}</td>
                    <td className={`px-4 py-3 text-right font-bold ${isMatch ? 'text-success' : 'text-danger'}`}>
                      PKR {(tx.difference || 0).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {isMatch ? <CheckCircle size={14} className="text-success ml-auto" /> : <XCircle size={14} className="text-danger ml-auto" />}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default QRCommissionTab;
