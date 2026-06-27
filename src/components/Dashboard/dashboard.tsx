import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { salesData } from "../../data/mockdata";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <h1 className="dashboard-title">დეშბორდი</h1>

      <div className="chart-card">
        <h2 className="chart-title">შემოსავალი (Revenue)</h2>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={salesData}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#4f46e5"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}