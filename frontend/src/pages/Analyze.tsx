import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { predictionsApi, type Prediction } from '@/lib/api';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function Analyze() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ product_name: '', rating: '3', review_title: '', review_text: '' });
  const [result, setResult] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await predictionsApi.create({
        ...form,
        rating: parseInt(form.rating, 10),
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const isDeceptive = result?.predicted_class === 1;
  const pct = result ? Math.round(result.probability_deceptive * 100) : 0;

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Analyze a Review</h1>
        <p className="text-sm text-slate-500 mt-1">Submit a product review to receive an ML-based deception probability estimate.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-lg p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Product name</label>
            <input
              id="product-name"
              type="text"
              value={form.product_name}
              onChange={(e) => setForm({ ...form, product_name: e.target.value })}
              required
              placeholder="e.g. Wireless Headphones"
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Rating (1–5)</label>
            <select
              id="rating"
              value={form.rating}
              onChange={(e) => setForm({ ...form, rating: e.target.value })}
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
            >
              {[1, 2, 3, 4, 5].map((r) => (
                <option key={r} value={r}>{r} star{r !== 1 ? 's' : ''}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Review title</label>
            <input
              id="review-title"
              type="text"
              value={form.review_title}
              onChange={(e) => setForm({ ...form, review_title: e.target.value })}
              required
              placeholder="Short summary of the review"
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Review text</label>
            <textarea
              id="review-text"
              value={form.review_text}
              onChange={(e) => setForm({ ...form, review_text: e.target.value })}
              required
              rows={6}
              placeholder="Paste or type the review text here…"
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <button
            id="analyze-submit"
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white rounded-md py-2.5 text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                Analyzing…
              </>
            ) : 'Analyze review'}
          </button>
        </form>

        {/* Result */}
        <div>
          {result ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6">
              <div className={`flex items-center gap-3 mb-5 pb-5 border-b border-slate-100`}>
                {isDeceptive
                  ? <AlertTriangle className="h-6 w-6 text-amber-500 flex-shrink-0" strokeWidth={1.75} />
                  : <CheckCircle className="h-6 w-6 text-emerald-500 flex-shrink-0" strokeWidth={1.75} />
                }
                <div>
                  <p className="font-semibold text-slate-900">
                    {isDeceptive ? 'Likely deceptive' : 'Likely genuine'}
                  </p>
                  <p className="text-sm text-slate-400">{result.product_name}</p>
                </div>
              </div>

              {/* Probability bar */}
              <div className="mb-5">
                <div className="flex justify-between text-xs text-slate-500 mb-1.5">
                  <span>Estimated deceptive probability</span>
                  <span className="font-medium text-slate-700">{pct}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${isDeceptive ? 'bg-amber-400' : 'bg-emerald-400'}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>

              <div className="space-y-2.5 text-sm">
                {[
                  ['Prob. deceptive', `${(result.probability_deceptive * 100).toFixed(1)}%`],
                  ['Prob. genuine', `${(result.probability_genuine * 100).toFixed(1)}%`],
                  ['Decision threshold', result.threshold_used.toFixed(2)],
                  ['Rating submitted', `${result.rating} ★`],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between">
                    <span className="text-slate-500">{k}</span>
                    <span className="font-medium text-slate-800">{v}</span>
                  </div>
                ))}
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 flex items-start gap-2 text-xs text-slate-400">
                <Info className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" strokeWidth={1.75} />
                <span>
                  This is an ML estimate, not a definitive verdict. The model has a 41.3% false-positive rate.
                  Use this as one signal among many.
                </span>
              </div>

              <button
                onClick={() => navigate(`/history/${result.id}`)}
                className="mt-4 w-full text-sm border border-slate-200 text-slate-600 rounded-md py-2 hover:bg-slate-50 transition-colors"
              >
                View full details
              </button>
            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
              <Info className="h-6 w-6 text-slate-300 mb-3" strokeWidth={1.5} />
              <p className="text-sm text-slate-400">Results will appear here after you submit a review for analysis.</p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
