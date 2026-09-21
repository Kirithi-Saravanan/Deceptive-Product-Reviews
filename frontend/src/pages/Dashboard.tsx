import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { AppLayout } from '@/components/AppLayout';
import { dashboardApi, type DashboardSummary, type DashboardTrends } from '@/lib/api';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  AreaChart,
  Area,
} from 'recharts';
import { Search, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

const PIE_COLORS = { Deceptive: '#f59e0b', Genuine: '#10b981' };

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<DashboardTrends | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardApi.getSummary().then((r) => r.data).catch(() => null),
      dashboardApi.getTrends().then((r) => r.data).catch(() => null),
    ])
      .then(([summaryData, trendsData]) => {
        setSummary(summaryData);
        setTrends(trendsData);
      })
      .finally(() => setLoading(false));
  }, []);

  const pieData = summary ? [
    { name: 'Deceptive', value: summary.deceptive_reviews },
    { name: 'Genuine', value: summary.genuine_reviews },
  ] : [];

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Welcome back, {user?.name}</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-5 h-5 border-2 border-slate-300 border-t-slate-700 rounded-full animate-spin" />
        </div>
      ) : summary?.total_reviews === 0 ? (
        <div className="border border-slate-200 rounded-lg p-12 text-center bg-white">
          <Search className="h-8 w-8 text-slate-300 mx-auto mb-3" strokeWidth={1.5} />
          <p className="text-slate-700 font-medium mb-1">No analyses yet</p>
          <p className="text-sm text-slate-400 mb-5">Analyze your first review to see your dashboard.</p>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            Analyze a review
          </Link>
        </div>
      ) : (
        <>
          {/* Key Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Total analyzed', value: summary!.total_reviews, icon: TrendingUp, color: 'text-slate-700' },
              { label: 'Flagged deceptive', value: summary!.deceptive_reviews, icon: AlertTriangle, color: 'text-amber-600' },
              { label: 'Likely genuine', value: summary!.genuine_reviews, icon: CheckCircle, color: 'text-emerald-600' },
              { label: 'Avg. rating', value: summary!.average_rating.toFixed(1), icon: TrendingUp, color: 'text-indigo-600' },
            ].map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="bg-white border border-slate-200 rounded-lg p-5">
                <div className={`${color} mb-2`}>
                  <Icon className="h-4 w-4" strokeWidth={1.75} />
                </div>
                <p className="text-2xl font-semibold text-slate-900">{value}</p>
                <p className="text-xs text-slate-500 mt-0.5">{label}</p>
              </div>
            ))}
          </div>

          {/* Charts Row 1: Pie Distribution & Recent Analyses */}
          <div className="grid lg:grid-cols-2 gap-6 mb-6">
            {/* Distribution chart */}
            <div className="bg-white border border-slate-200 rounded-lg p-6">
              <h2 className="text-sm font-semibold text-slate-700 mb-5">Prediction distribution</h2>
              {summary!.total_reviews > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={80}
                      dataKey="value"
                      strokeWidth={2}
                      stroke="#fff"
                    >
                      {pieData.map((entry) => (
                        <Cell key={entry.name} fill={PIE_COLORS[entry.name as keyof typeof PIE_COLORS]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => [v, 'Reviews']} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-slate-400">No data yet</p>
              )}
              <div className="flex gap-5 justify-center mt-3">
                {pieData.map((d) => (
                  <div key={d.name} className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ background: PIE_COLORS[d.name as keyof typeof PIE_COLORS] }} />
                    <span className="text-xs text-slate-600">{d.name} ({d.value})</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent analyses */}
            <div className="bg-white border border-slate-200 rounded-lg p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-slate-700">Recent analyses</h2>
                  <Link to="/history" className="text-xs text-indigo-600 hover:text-indigo-800">View all</Link>
                </div>
                <div className="space-y-3">
                  {summary!.recent_analyses.length === 0 ? (
                    <p className="text-sm text-slate-400">None yet</p>
                  ) : (
                    summary!.recent_analyses.map((a) => (
                      <Link
                        key={a.id}
                        to={`/history/${a.id}`}
                        className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0 hover:bg-slate-50 -mx-2 px-2 rounded transition-colors"
                      >
                        <div>
                          <p className="text-sm font-medium text-slate-700 truncate max-w-[200px]">{a.product_name}</p>
                          <p className="text-xs text-slate-400">{new Date(a.created_at).toLocaleDateString()}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400">{a.rating} ★</span>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            a.predicted_label === 'Deceptive'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          }`}>
                            {a.predicted_label}
                          </span>
                        </div>
                      </Link>
                    ))
                  )}
                </div>
              </div>
              <div className="pt-4 border-t border-slate-100 mt-4 text-center">
                <Link
                  to="/analyze"
                  className="text-xs text-indigo-600 font-medium hover:text-indigo-800"
                >
                  + Analyze another review
                </Link>
              </div>
            </div>
          </div>

          {/* Charts Row 2: Rating Distribution & Prediction Trends */}
          <div className="grid lg:grid-cols-2 gap-6 mb-8">
            {/* Rating distribution chart */}
            <div className="bg-white border border-slate-200 rounded-lg p-6">
              <h2 className="text-sm font-semibold text-slate-700 mb-1">Rating distribution</h2>
              <p className="text-xs text-slate-400 mb-4">Breakdown of submitted reviews by star rating.</p>
              {trends && trends.ratings_distribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={trends.ratings_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="rating" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{ fill: '#f8fafc' }} />
                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-slate-400">No rating distribution data available.</p>
              )}
            </div>

            {/* Daily prediction trends chart */}
            <div className="bg-white border border-slate-200 rounded-lg p-6">
              <h2 className="text-sm font-semibold text-slate-700 mb-1">Analysis trends over time</h2>
              <p className="text-xs text-slate-400 mb-4">Volume of reviews analyzed by date.</p>
              {trends && trends.prediction_trends.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={trends.prediction_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Area type="monotone" dataKey="total" name="Total" stroke="#6366f1" fill="#e0e7ff" strokeWidth={2} />
                    <Area type="monotone" dataKey="deceptive" name="Deceptive" stroke="#f59e0b" fill="#fef3c7" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-slate-400">No trend history available yet.</p>
              )}
            </div>
          </div>
        </>
      )}
    </AppLayout>
  );
}
