import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { Database, TrendingUp, AlertCircle } from 'lucide-react';

interface DashboardProps {
  data: any | null;
  chartInfo: any | null;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#8dd1e1', '#a4de6c'];

export function Dashboard({ data, chartInfo }: DashboardProps) {
  if (!data && !chartInfo) {
    return (
      <div className="dashboard-empty">
        <Database size={64} className="empty-icon" />
        <h2>დეშბორდი ცარიელია</h2>
        <p>დაუსვით კითხვა ასისტენტს და აქ მონაცემები გამოჩნდება</p>
      </div>
    );
  }

  const renderChart = () => {
    if (!chartInfo || chartInfo.chart_type === 'none' || !data || !data.rows || data.rows.length === 0) {
      return null;
    }

    const { chart_type, x_axis, y_axis, title } = chartInfo;
    const chartData = data.rows;

    return (
      <div className="chart-container">
        {title && <h3 className="chart-title">{title}</h3>}
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height="100%">
            {chart_type === 'bar' ? (
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey={x_axis} tick={{fill: '#e2e8f0'}} angle={-45} textAnchor="end" />
                <YAxis tick={{fill: '#e2e8f0'}} />
                <Tooltip contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff'}} />
                <Legend />
                <Bar dataKey={y_axis} fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : chart_type === 'pie' ? (
              <PieChart>
                <Tooltip contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff'}} />
                <Legend />
                <Pie 
                  data={chartData} 
                  dataKey={y_axis} 
                  nameKey={x_axis} 
                  cx="50%" 
                  cy="50%" 
                  outerRadius={120} 
                  label
                >
                  {chartData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            ) : (
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey={x_axis} tick={{fill: '#e2e8f0'}} angle={-45} textAnchor="end" />
                <YAxis tick={{fill: '#e2e8f0'}} />
                <Tooltip contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff'}} />
                <Legend />
                <Line type="monotone" dataKey={y_axis} stroke="#10b981" strokeWidth={3} dot={{r: 6}} activeDot={{r: 8}} />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  const renderTable = () => {
    if (!data || !data.rows || data.rows.length === 0) return null;

    return (
      <div className="table-container">
        <h3 className="table-title">დეტალური მონაცემები</h3>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {data.columns.map((col: string, idx: number) => (
                  <th key={idx}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row: any, idx: number) => (
                <tr key={idx}>
                  {data.columns.map((col: string, colIdx: number) => (
                    <td key={colIdx}>{row[col]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-footer">
          სულ: {data.row_count} ჩანაწერი
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard-content">
      <div className="dashboard-header">
        <TrendingUp size={28} className="text-purple-400" />
        <h2>ანალიტიკის დაფა</h2>
      </div>
      
      <div className="dashboard-widgets">
        {renderChart()}
        {renderTable()}
      </div>
    </div>
  );
}
