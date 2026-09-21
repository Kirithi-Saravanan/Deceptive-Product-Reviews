import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { modelApi, type ModelInfo } from '@/lib/api';
import { Info } from 'lucide-react';

function Metric({ label, value, note, warn }: { label: string; value: string; note?: string; warn?: boolean }) {
  return (
    <div className="border border-slate-100 rounded-md p-4">
      <p className="text-xs text-slate-400 mb-0.5">{label}</p>
      <p className={`text-xl font-semibold ${warn ? 'text-amber-600' : 'text-slate-800'}`}>{value}</p>
      {note && <p className="text-xs text-slate-400 mt-0.5">{note}</p>}
    </div>
  );
}

function pct(v: number) {
  return (v * 100).toFixed(1) + '%';
}

export default function ModelPage() {
  const [info, setInfo] = useState<ModelInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    modelApi.getInfo()
      .then((r) => setInfo(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Model Information</h1>
        <p className="text-sm text-slate-500 mt-1">
          Details about the Phase 3B ML model. Loaded directly from locked artifacts.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-5 h-5 border-2 border-slate-300 border-t-slate-700 rounded-full animate-spin" />
        </div>
      ) : !info ? (
        <p className="text-sm text-slate-500">Could not load model information.</p>
      ) : (
        <div className="space-y-6">
          {/* Config */}
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h2 className="text-sm font-semibold text-slate-700 mb-5">Configuration</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <Metric label="Model" value={info.selected_model} />
              <Metric label="Decision threshold" value={info.selected_threshold.toFixed(2)} note="Probability cutoff" />
              <Metric label="Feature set" value="Combined" note={info.features} />
              <Metric label="Training samples" value={info.train_size.toLocaleString()} />
              <Metric label="Validation samples" value={info.val_size.toLocaleString()} />
              <Metric label="Test samples" value={info.test_size.toLocaleString()} />
            </div>
          </div>

          {/* Validation metrics */}
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h2 className="text-sm font-semibold text-slate-700 mb-1">Validation Metrics</h2>
            <p className="text-xs text-slate-400 mb-5">Used for model selection. Macro F1 was the primary metric.</p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Metric label="Macro F1" value={pct(info.validation_metrics.f1_macro)} note="Primary selection metric" />
              <Metric label="Deceptive F1" value={pct(info.validation_metrics.f1_deceptive)} note="Tie-breaker metric" />
              <Metric label="Accuracy" value={pct(info.validation_metrics.accuracy)} />
              <Metric label="Genuine F1" value={pct(info.validation_metrics.f1_genuine)} />
            </div>
          </div>

          {/* Test metrics */}
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h2 className="text-sm font-semibold text-slate-700 mb-1">Test Set Performance</h2>
            <p className="text-xs text-slate-400 mb-5">Held-out test set results using the locked threshold.</p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <Metric label="Accuracy" value={pct(info.test_metrics.accuracy)} />
              <Metric label="Macro F1" value={pct(info.test_metrics.f1_macro)} />
              <Metric label="ROC AUC" value={info.test_metrics.roc_auc.toFixed(4)} />
              <Metric label="Deceptive recall" value={pct(info.test_metrics.deceptive.recall)} note="% of deceptive reviews caught" />
              <Metric label="Deceptive precision" value={pct(info.test_metrics.deceptive.precision)} />
              <Metric label="False-positive rate" value={pct(info.test_metrics.false_positive_rate)} note="Genuine reviews flagged as deceptive" warn />
            </div>
          </div>

          {/* Limitations notice */}
          <div className="bg-amber-50 border border-amber-100 rounded-lg p-5 flex items-start gap-3">
            <Info className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" strokeWidth={1.75} />
            <p className="text-sm text-amber-800 leading-relaxed">
              <strong>Important limitation:</strong> The model achieves high deceptive-review recall (
              {pct(info.test_metrics.deceptive.recall)}) but has a relatively high false-positive rate (
              {pct(info.test_metrics.false_positive_rate)}), meaning some genuine reviews are incorrectly classified as deceptive.
              This motivates future improvements such as better calibration, additional training data, and improved feature engineering.
              All results shown are probabilistic estimates, not definitive verdicts.
            </p>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
