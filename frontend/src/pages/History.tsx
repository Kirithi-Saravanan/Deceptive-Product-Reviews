import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { predictionsApi, type Prediction } from '@/lib/api';
import { History as HistoryIcon, ChevronRight, Search, Trash2, Filter } from 'lucide-react';

export default function History() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'deceptive' | 'genuine'>('all');
  const [ratingFilter, setRatingFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date_desc' | 'date_asc' | 'rating_desc' | 'rating_asc' | 'prob_desc'>('date_desc');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fetchHistory = () => {
    setLoading(true);
    predictionsApi.list(0, 100)
      .then((r) => setPredictions(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (!window.confirm('Are you sure you want to delete this prediction?')) return;
    setDeletingId(id);
    try {
      await predictionsApi.delete(id);
      setPredictions((prev) => prev.filter((p) => p.id !== id));
    } catch {
      alert('Failed to delete prediction.');
    } finally {
      setDeletingId(null);
    }
  };

  const filteredPredictions = useMemo(() => {
    return predictions
      .filter((p) => {
        // Search filter
        const query = search.toLowerCase().trim();
        const matchesSearch =
          !query ||
          p.product_name.toLowerCase().includes(query) ||
          p.review_title.toLowerCase().includes(query);

        // Status filter
        const matchesStatus =
          statusFilter === 'all' ||
          (statusFilter === 'deceptive' && p.predicted_class === 1) ||
          (statusFilter === 'genuine' && p.predicted_class === 0);

        // Rating filter
        const matchesRating =
          ratingFilter === 'all' || p.rating === parseInt(ratingFilter, 10);

        return matchesSearch && matchesStatus && matchesRating;
      })
      .sort((a, b) => {
        if (sortBy === 'date_desc') {
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
        if (sortBy === 'date_asc') {
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        }
        if (sortBy === 'rating_desc') {
          return b.rating - a.rating;
        }
        if (sortBy === 'rating_asc') {
          return a.rating - b.rating;
        }
        if (sortBy === 'prob_desc') {
          return b.probability_deceptive - a.probability_deceptive;
        }
        return 0;
      });
  }, [predictions, search, statusFilter, ratingFilter, sortBy]);

  return (
    <AppLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Analysis History</h1>
        <p className="text-sm text-slate-500 mt-1">All reviews you have analyzed, strictly isolated to your account.</p>
      </div>

      {/* Controls: Search, Filter, Sort */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            id="history-search"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search product or title…"
            className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-md placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400 flex-shrink-0" />
          <select
            id="filter-status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="w-full text-sm border border-slate-200 rounded-md py-2 px-2.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All verdicts</option>
            <option value="deceptive">Deceptive only</option>
            <option value="genuine">Genuine only</option>
          </select>
        </div>

        {/* Rating Filter */}
        <div>
          <select
            id="filter-rating"
            value={ratingFilter}
            onChange={(e) => setRatingFilter(e.target.value)}
            className="w-full text-sm border border-slate-200 rounded-md py-2 px-2.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All ratings</option>
            <option value="5">5 stars</option>
            <option value="4">4 stars</option>
            <option value="3">3 stars</option>
            <option value="2">2 stars</option>
            <option value="1">1 star</option>
          </select>
        </div>

        {/* Sort */}
        <div>
          <select
            id="history-sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="w-full text-sm border border-slate-200 rounded-md py-2 px-2.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="date_desc">Newest first</option>
            <option value="date_asc">Oldest first</option>
            <option value="rating_desc">Highest rating</option>
            <option value="rating_asc">Lowest rating</option>
            <option value="prob_desc">Highest deceptive %</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-5 h-5 border-2 border-slate-300 border-t-slate-700 rounded-full animate-spin" />
        </div>
      ) : predictions.length === 0 ? (
        <div className="border border-slate-200 rounded-lg p-12 text-center bg-white">
          <HistoryIcon className="h-8 w-8 text-slate-300 mx-auto mb-3" strokeWidth={1.5} />
          <p className="text-slate-700 font-medium mb-1">No history yet</p>
          <p className="text-sm text-slate-400 mb-5">Your analyzed reviews will appear here.</p>
          <Link to="/analyze" className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">
            Analyze a review
          </Link>
        </div>
      ) : filteredPredictions.length === 0 ? (
        <div className="border border-slate-200 rounded-lg p-10 text-center bg-white">
          <p className="text-slate-700 font-medium mb-1">No matching analyses found</p>
          <p className="text-sm text-slate-400 mb-4">Try clearing or adjusting your search or filters.</p>
          <button
            onClick={() => { setSearch(''); setStatusFilter('all'); setRatingFilter('all'); }}
            className="text-xs text-indigo-600 font-medium hover:underline"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-100 bg-slate-50 flex justify-between items-center text-xs text-slate-500">
            <span>Showing {filteredPredictions.length} of {predictions.length} analyses</span>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/50">
                <th className="text-left text-xs font-medium text-slate-500 px-5 py-3">Product</th>
                <th className="text-left text-xs font-medium text-slate-500 px-4 py-3 hidden md:table-cell">Title</th>
                <th className="text-left text-xs font-medium text-slate-500 px-4 py-3 hidden sm:table-cell">Rating</th>
                <th className="text-left text-xs font-medium text-slate-500 px-4 py-3">Result</th>
                <th className="text-left text-xs font-medium text-slate-500 px-4 py-3 hidden lg:table-cell">Date</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredPredictions.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3.5">
                    <Link to={`/history/${p.id}`} className="font-medium text-slate-800 hover:text-indigo-600 transition-colors block truncate max-w-[180px]">
                      {p.product_name}
                    </Link>
                    <p className="text-xs text-slate-400 mt-0.5">{Math.round(p.probability_deceptive * 100)}% deceptive prob.</p>
                  </td>
                  <td className="px-4 py-3.5 hidden md:table-cell">
                    <p className="text-sm text-slate-600 truncate max-w-[200px]">{p.review_title}</p>
                  </td>
                  <td className="px-4 py-3.5 hidden sm:table-cell">
                    <span className="text-sm text-slate-700 font-medium">{p.rating} ★</span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                      p.predicted_class === 1
                        ? 'bg-amber-50 text-amber-700 border border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}>
                      {p.predicted_label}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 hidden lg:table-cell">
                    <p className="text-xs text-slate-400">{new Date(p.created_at).toLocaleDateString()}</p>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={(e) => handleDelete(p.id, e)}
                        disabled={deletingId === p.id}
                        title="Delete analysis"
                        className="text-slate-400 hover:text-red-500 p-1.5 rounded hover:bg-slate-100 transition-colors disabled:opacity-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                      <Link
                        to={`/history/${p.id}`}
                        title="View details"
                        className="text-slate-400 hover:text-indigo-600 p-1.5 rounded hover:bg-slate-100 transition-colors"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppLayout>
  );
}
