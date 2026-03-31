import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useFilters } from '../api/FilterContext';
import { Download } from 'lucide-react';
import { exportToCSV } from '../utils/export';

const API_BASE_URL = 'http://localhost:8000';

const PivotTablesTab: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { startDate, endDate, selectedBranches, dataMode } = useFilters();
  const [pivotType, setPivotType] = useState<"Branch x Category" | "Branch x Day" | "Month x Branch">("Branch x Category");
  const [metric, setMetric] = useState<"Sales" | "Quantity">("Sales");

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
        
        let endpoint = '';
        if (pivotType === "Branch x Category") {
          endpoint = `/pivot/branch-category?metric=${metric}`;
        } else if (pivotType === "Branch x Day") {
          endpoint = `/pivot/branch-day`;
        } else {
          endpoint = `/pivot/month-branch`;
        }
        
        const response = await axios.get(`${API_BASE_URL}${endpoint}&start_date=${startDate}&end_date=${endDate}&${branchParams}&data_mode=${dataMode}`);
        setData(response.data);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, selectedBranches, dataMode, pivotType, metric]);

  if (loading) return <div className="flex justify-center items-center h-full"><p className="text-textSecondary">Loading data...</p></div>;
  if (error) return <div className="p-4 bg-danger/10 text-danger rounded-lg">Error: {error}</div>;

  const columns = data.length > 0 ? Object.keys(data[0]) : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface p-4 rounded-lg shadow-sm border border-border">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-bold text-textSecondary uppercase">Pivot Type</label>
            <select 
              value={pivotType} 
              onChange={(e) => setPivotType(e.target.value as any)}
              className="bg-background border border-border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option value="Branch x Category">Branch x Category</option>
              <option value="Branch x Day">Branch x Day</option>
              <option value="Month x Branch">Month x Branch</option>
            </select>
          </div>
          
          {pivotType === "Branch x Category" && (
            <div className="flex flex-col gap-1">
              <label className="text-xs font-bold text-textSecondary uppercase">Metric</label>
              <select 
                value={metric} 
                onChange={(e) => setMetric(e.target.value as any)}
                className="bg-background border border-border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="Sales">Sales</option>
                <option value="Quantity">Quantity</option>
              </select>
            </div>
          )}
        </div>

        <button 
          onClick={() => exportToCSV(data, `pivot_${pivotType.toLowerCase().replace(/ /g, '_')}`)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors text-sm font-semibold self-end md:self-auto"
        >
          <Download size={16} />
          <span>Export CSV</span>
        </button>
      </div>

      <div className="bg-surface rounded-lg shadow-card overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-bold text-textPrimary">{pivotType} Analysis</h3>
          <p className="text-sm text-textSecondary mt-1">
            {pivotType === "Branch x Category" ? `Comparative analysis of ${metric} across branches and product categories.` : 
             pivotType === "Branch x Day" ? "Daily sales breakdown for each selected branch." : 
             "Monthly sales performance across branches."}
          </p>
        </div>
        <div className="overflow-x-auto max-h-[600px]">
          <table className="w-full text-left text-sm">
            <thead className="bg-background text-textSecondary text-xs uppercase sticky top-0">
              <tr>
                {columns.map(col => (
                  <th key={col} className="px-4 py-3 font-semibold whitespace-nowrap border-b border-border">
                    {col.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.map((row, idx) => (
                <tr key={idx} className="hover:bg-background transition-colors">
                  {columns.map(col => (
                    <td key={col} className={`px-4 py-3 whitespace-nowrap ${col === 'shop_name' || col === 'month' ? 'font-bold text-textPrimary' : 'text-textSecondary'}`}>
                      {typeof row[col] === 'number' 
                        ? (metric === 'Sales' || pivotType !== 'Branch x Category' ? `PKR ${row[col].toLocaleString()}` : row[col].toLocaleString())
                        : row[col]}
                    </td>
                  ))}
                </tr>
              ))}
              {data.length === 0 && (
                <tr>
                  <td colSpan={columns.length || 1} className="px-6 py-12 text-center text-textSecondary italic">
                    No data available for the selected criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PivotTablesTab;
