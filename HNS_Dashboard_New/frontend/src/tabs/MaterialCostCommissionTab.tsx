import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import Card from '../components/Card';
import { DollarSign, Package, TrendingUp, Search, Download, Info, ShoppingBag } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';

interface BranchSummary {
  shop_name: string;
  total_units_sold: number;
  total_sales: number;
  total_material_cost: number;
  total_commission: number;
  avg_commission_rate: number;
}

interface EmployeeSummary {
  employee_name: string;
  shop_name: string;
  total_units_sold: number;
  total_sales: number;
  total_material_cost: number;
  total_commission: number;
}

interface ProductSummary {
  product_code: number;
  product_name: string;
  material_cost: number;
  commission: number;
  total_units_sold: number;
  total_sales: number;
  total_material_cost: number;
  total_commission: number;
  commission_rate: number;
}

const MaterialCostCommissionTab: React.FC = () => {
  const [branchSummary, setBranchSummary] = useState<BranchSummary[]>([]);
  const [employeeSummary, setEmployeeSummary] = useState<EmployeeSummary[]>([]);
  const [productSummary, setProductSummary] = useState<ProductSummary[]>([]);
  const [setup, setSetup] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();
  const [showSetup, setShowSetup] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (selectedBranches.length === 0) {
        setBranchSummary([]);
        setEmployeeSummary([]);
        setProductSummary([]);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const branchParams = selectedBranches.map(id => `branch_ids=${id}`).join('&');
        const commonParams = `start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`;
        
        const [branchRes, empRes, prodRes, setupRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/material-cost/branch-summary?${commonParams}`),
          axios.get(`${API_BASE_URL}/material-cost/employee-summary?${commonParams}`),
          axios.get(`${API_BASE_URL}/material-cost/product-summary?${commonParams}`),
          axios.get(`${API_BASE_URL}/material-cost/setup`)
        ]);

        setBranchSummary(branchRes.data);
        setEmployeeSummary(empRes.data);
        setProductSummary(prodRes.data);
        setSetup(setupRes.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode]);

  if (loading && branchSummary.length === 0) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading commission data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const totalSales = branchSummary.reduce((acc, curr) => acc + curr.total_sales, 0);
  const totalCommission = branchSummary.reduce((acc, curr) => acc + curr.total_commission, 0);
  const totalMaterialCost = branchSummary.reduce((acc, curr) => acc + curr.total_material_cost, 0);
  const totalUnits = branchSummary.reduce((acc, curr) => acc + curr.total_units_sold, 0);

  return (
    <div className="space-y-8">
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card 
          title="Total Group Sales" 
          value={`PKR ${totalSales.toLocaleString()}`}
          icon={<DollarSign size={24} />}
        />
        <Card 
          title="Total Material Cost" 
          value={`PKR ${totalMaterialCost.toLocaleString()}`}
          icon={<Package size={24} />}
        />
        <Card 
          title="Total Commission" 
          value={`PKR ${totalCommission.toLocaleString()}`}
          icon={<TrendingUp size={24} />}
          trend={{ value: `${((totalCommission / (totalSales || 1)) * 100).toFixed(1)}% of Sales`, isPositive: true }}
        />
        <Card 
          title="Total Units Sold" 
          value={totalUnits.toLocaleString()}
          icon={<ShoppingBag size={24} />}
        />
      </div>

      {/* Branch Summary Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Branch Performance Split</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-6 py-3 border-b border-border">Branch</th>
                <th className="px-6 py-3 border-b border-border text-right">Units</th>
                <th className="px-6 py-3 border-b border-border text-right">Sales</th>
                <th className="px-6 py-3 border-b border-border text-right">Cost</th>
                <th className="px-6 py-3 border-b border-border text-right text-success">Commission</th>
                <th className="px-6 py-3 border-b border-border text-right">Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {branchSummary.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.shop_name}</td>
                  <td className="px-6 py-4 text-right text-textSecondary">{item.total_units_sold.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-medium">PKR {item.total_sales.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right text-textSecondary font-mono text-[11px]">PKR {item.total_material_cost.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-black text-success">PKR {item.total_commission.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right text-textSecondary">{item.avg_commission_rate}%</td>
                </tr>
              ))}
              {branchSummary.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-textSecondary italic">No data found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Employee Summary Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border flex justify-between items-center bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Employee Commission Breakdown</h3>
          <button 
            onClick={() => exportToCSV(employeeSummary, 'employee_commission_report')}
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
                <th className="px-6 py-3 border-b border-border">Employee</th>
                <th className="px-6 py-3 border-b border-border">Branch</th>
                <th className="px-6 py-3 border-b border-border text-right">Units</th>
                <th className="px-6 py-3 border-b border-border text-right">Sales</th>
                <th className="px-6 py-3 border-b border-border text-right text-success">Commission</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {employeeSummary.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.employee_name}</td>
                  <td className="px-6 py-4 text-textSecondary">{item.shop_name}</td>
                  <td className="px-6 py-4 text-right text-textSecondary">{item.total_units_sold.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-medium">PKR {item.total_sales.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-black text-success">PKR {item.total_commission.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Product Summary Table */}
      <div className="bg-surface rounded-lg shadow-card overflow-hidden border border-border">
        <div className="p-6 border-b border-border bg-background/50">
          <h3 className="text-lg font-bold text-textPrimary">Product-wise Commission Detail</h3>
        </div>
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-[10px] uppercase sticky top-0 font-black tracking-tighter">
              <tr>
                <th className="px-6 py-3 border-b border-border">Product Name</th>
                <th className="px-6 py-3 border-b border-border text-right">Units</th>
                <th className="px-6 py-3 border-b border-border text-right">Sales</th>
                <th className="px-6 py-3 border-b border-border text-right">Cost</th>
                <th className="px-6 py-3 border-b border-border text-right text-success">Commission</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {productSummary.map((item, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  <td className="px-6 py-4 font-bold text-textPrimary">{item.product_name}</td>
                  <td className="px-6 py-4 text-right text-textSecondary">{item.total_units_sold.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-medium">PKR {item.total_sales.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right text-textSecondary font-mono text-[11px]">PKR {item.total_material_cost.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right font-black text-success">PKR {item.total_commission.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MaterialCostCommissionTab;
