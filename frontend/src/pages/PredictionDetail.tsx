import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AppLayout } from '@/components/AppLayout';
import { predictionsApi, type Prediction } from '@/lib/api';
import { AlertTriangle, CheckCircle, ChevronLeft, Trash2, Info } from 'lucide-react';

export default function PredictionDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!id) return;
    predictionsApi.getById(id)
      .then((r) => setPrediction(r.data))
      .catch(() => navigate('/history'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleDelete = async () => {
    if (!id || !window.confirm('Delete this analysis?')) return;
    setDeleting(true);
    try {
      await predictionsApi.delete(id);
      navigate('/history');
    } catch {
      setDeleting(false);
    }
  };

  const isDeceptive = prediction?.predicted_class === 1;
  const pct = prediction ? Math.round(prediction.probability_deceptive * 100) : 0;

  return (
    <AppLayout>
      <div className="mb-6">
        <Link to="/history" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 transition-colors mb-4">
          <ChevronLeft className="h-4 w-4" />
          Back to History
        </Link>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{prediction?.product_name}</h1>
            <p className="text-sm text-slate-500 mt-0.5">{prediction && new Date(prediction.created_at).toLocaleString()}</p>
          </div>
          {prediction && (
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="flex items-center gap-1.5 text-xs text-red-500 border border-red-200 rounded-md px-3 py-1.5 hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              <Trash2 className="h-3.5 w-3.5" />
              Delete
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-5 h-5 border-2 border-slate-300 border-t-slate-700 rounded-full animate-spin" />
        </div>
      ) : prediction && (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Result panel */}
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-5">
              {isDeceptive
                ? <AlertTriangle className="h-6 w-6 text-amber-500" strokeWidth={1.75} />
                : <CheckCircle className="h-6 w-6 text-emerald-500" strokeWidth={1.75} />
              }
              <div>
                <p className="font-semibold text-slate-900">{isDeceptive ? 'Likely deceptive' : 'Likely genuine'}</p>
                <p className="text-xs text-slate-400">{prediction.rating} ★</p>
              </div>
            </div>

            <div className="mb-5">
              <div className="flex justify-between text-xs text-slate-500 mb-1.5">
                <span>Deceptive probability</span>
                <span className="font-medium text-slate-700">{pct}%</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${isDeceptive ? 'bg-amber-400' : 'bg-emerald-400'}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>

            <div className="space-y-2.5 text-sm">
              {[
                ['Prob. deceptive', `${(prediction.probability_deceptive * 100).toFixed(1)}%`],
                ['Prob. genuine', `${(prediction.probability_genuine * 100).toFixed(1)}%`],
                ['Decision threshold', prediction.threshold_used.toFixed(2)],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <span className="text-slate-500">{k}</span>
                  <span className="font-medium text-slate-800">{v}</span>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100 flex items-start gap-2 text-xs text-slate-400">
              <Info className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" strokeWidth={1.75} />
              <span>Estimate only. Model FPR is 41.3%.</span>
            </div>
          </div>

          {/* Review content */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white border border-slate-200 rounded-lg p-6">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Review title</p>
              <p className="text-slate-800 font-medium">{prediction.review_title}</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-lg p-6">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">Review text</p>
              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{prediction.review_text}</p>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
