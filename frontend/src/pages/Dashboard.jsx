import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { fetchHistory } from "../api/client";

export default function Dashboard() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchHistory()
      .then(setHistory)
      .catch(() => setError("Couldn't load your history."))
      .finally(() => setLoading(false));
  }, []);

  const chartData = history.map((item) => ({
    date: new Date(item.created_at).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    }),
    risk: Math.round(item.risk_score * 100),
    condition: item.condition,
  }));

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl text-teal-900">Your risk history</h1>
        <Link
          to="/questionnaire"
          className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700"
        >
          New assessment
        </Link>
      </div>

      {loading && <p className="text-teal-700">Loading...</p>}
      {error && <p className="text-risk-high">{error}</p>}

      {!loading && !error && history.length === 0 && (
        <div className="rounded-md border border-dashed border-teal-200 p-10 text-center text-teal-700">
          No assessments yet. Run your first one to start tracking your trend.
        </div>
      )}

      {chartData.length > 0 && (
        <div className="mb-8 h-72 rounded-md border border-teal-100 bg-white p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#D5E9E4" />
              <XAxis dataKey="date" stroke="#164A41" fontSize={12} />
              <YAxis
                stroke="#164A41"
                fontSize={12}
                domain={[0, 100]}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip formatter={(v) => `${v}%`} />
              <Line
                type="monotone"
                dataKey="risk"
                stroke="#1F6357"
                strokeWidth={2}
                dot={{ fill: "#1F6357" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {history.length > 0 && (
        <ul className="space-y-2">
          {[...history].reverse().map((item) => (
            <li key={item.assessment_id}>
              <Link
                to={`/results/${item.assessment_id}`}
                className="flex items-center justify-between rounded-md border border-teal-100 bg-white px-4 py-3 hover:border-teal-400"
              >
                <span className="capitalize">{item.condition.replace("_", " ")}</span>
                <span className="text-sm text-teal-700">
                  {new Date(item.created_at).toLocaleDateString()} &middot;{" "}
                  {(item.risk_score * 100).toFixed(0)}% ({item.risk_label})
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
