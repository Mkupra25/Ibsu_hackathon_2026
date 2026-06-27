import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from "recharts";
import { useDashboard } from "../../context/DashboardContext";
import "./dashboard.css";

// BeeEye Theme Colors (Golds, Ambers, Zincs)
const COLORS = ['#eab308', '#f59e0b', '#d97706', '#fbbf24', '#a1a1aa'];

export default function Dashboard() {
  const { widgets, clearWidgets } = useDashboard();

  return (
    <div className="dashboard">
      <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="dashboard-title">დეშბორდი</h1>
        {widgets.length > 0 && (
          <button 
            onClick={clearWidgets}
            style={{ 
              background: 'transparent', 
              color: 'var(--text-muted)', 
              border: '1px solid var(--border)',
              padding: '6px 12px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            გასუფთავება
          </button>
        )}
      </div>

      {widgets.length === 0 ? (
        <div className="empty-dashboard">
          <p>მონაცემები არ არის. გთხოვთ, გამოიყენოთ AI ჩატი მონაცემების მისაღებად და გრაფიკების ასაგებად.</p>
        </div>
      ) : (
        <div className="widgets-grid" style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
          {widgets.map((widget) => (
            <div key={widget.id} className="widget-container" style={{ paddingBottom: '30px', borderBottom: '1px solid var(--border)' }}>
              
              {/* გრაფიკის ბლოკი */}
              {widget.chartInfo && widget.chartInfo.chart_type !== "none" && widget.queryResult && (
                <div className="chart-card">
                  <h2 className="chart-title">{widget.chartInfo.chart_title || "გრაფიკი"}</h2>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                      {widget.chartInfo.chart_type === "bar" ? (
                        <BarChart data={widget.queryResult.rows} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                          <XAxis dataKey={widget.chartInfo.x_axis} tick={{ fill: "#64748b" }} angle={-45} textAnchor="end" />
                          <YAxis tick={{ fill: "#64748b" }} />
                          <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }} />
                          <Legend />
                          <Bar dataKey={widget.chartInfo.y_axis!} fill="#eab308" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      ) : widget.chartInfo.chart_type === "pie" ? (
                        <PieChart>
                          <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }} />
                          <Legend />
                          <Pie
                            data={widget.queryResult.rows}
                            dataKey={widget.chartInfo.y_axis!}
                            nameKey={widget.chartInfo.x_axis!}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label
                          >
                            {widget.queryResult.rows.map((_, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                        </PieChart>
                      ) : (
                        <LineChart data={widget.queryResult.rows} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                          <XAxis dataKey={widget.chartInfo.x_axis} tick={{ fill: "#64748b" }} angle={-45} textAnchor="end" />
                          <YAxis tick={{ fill: "#64748b" }} />
                          <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }} />
                          <Legend />
                          <Line type="monotone" dataKey={widget.chartInfo.y_axis!} stroke="#eab308" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                        </LineChart>
                      )}
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* ცხრილის ბლოკი */}
              {widget.queryResult && widget.queryResult.rows.length > 0 && (
                <div className="table-card" style={{ marginTop: '20px' }}>
                  <h2 className="table-title">მონაცემთა ცხრილი (სულ: {widget.queryResult.row_count})</h2>
                  <div className="table-wrapper">
                    <table className="data-table">
                      <thead>
                        <tr>
                          {widget.queryResult.columns.map((col, idx) => (
                            <th key={idx}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {widget.queryResult.rows.map((row, idx) => (
                          <tr key={idx}>
                            {widget.queryResult.columns.map((col, colIdx) => (
                              <td key={colIdx}>{row[col]}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              
              {/* SQL ბლოკი */}
              {widget.sqlQuery && (
                 <div className="sql-card" style={{ marginTop: '20px' }}>
                   <details style={{ background: '#18181b', padding: '10px', borderRadius: '8px', border: '1px solid #27272a' }}>
                     <summary style={{ cursor: 'pointer', color: '#a1a1aa' }}>🔍 გენერირებული SQL</summary>
                     <pre style={{ marginTop: '10px', color: '#eab308', whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                       <code>{widget.sqlQuery}</code>
                     </pre>
                   </details>
                 </div>
              )}

            </div>
          ))}
        </div>
      )}
    </div>
  );
}