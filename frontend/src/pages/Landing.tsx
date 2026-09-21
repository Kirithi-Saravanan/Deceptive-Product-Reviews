import { Link } from 'react-router-dom';
import { ShieldCheck, ArrowRight, CheckCircle } from 'lucide-react';

const checks = [
  'Real ML inference — no hardcoded rules',
  'Each result tied to your account only',
  'Probability scores, not binary verdicts',
  'Analysis history saved for review',
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Nav */}
      <header className="border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-indigo-600" strokeWidth={1.75} />
            <span className="font-semibold text-slate-800">ReviewGuard AI</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
              Sign in
            </Link>
            <Link
              to="/register"
              className="text-sm bg-slate-900 text-white px-4 py-2 rounded-md hover:bg-slate-700 transition-colors"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1 flex items-center">
        <div className="max-w-5xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2 text-xs text-indigo-700 bg-indigo-50 border border-indigo-100 px-3 py-1.5 rounded-full mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
              Machine learning · Logistic Regression · Phase 3B
            </div>

            <h1 className="text-4xl font-bold text-slate-900 leading-tight mb-4">
              Detect deceptive reviews before they influence your decision.
            </h1>

            <p className="text-slate-500 text-lg leading-relaxed mb-8">
              ReviewGuard AI uses a trained ML model to estimate the probability that a
              product review is deceptive. Submit a review, get a probability score, and
              keep a personal analysis history.
            </p>

            <div className="flex items-center gap-4 mb-10">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                Start analyzing
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/login"
                className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                Sign in to existing account
              </Link>
            </div>

            <ul className="space-y-2">
              {checks.map((c) => (
                <li key={c} className="flex items-center gap-2.5 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0" strokeWidth={1.75} />
                  {c}
                </li>
              ))}
            </ul>
          </div>

          {/* Stats card */}
          <div className="border border-slate-200 rounded-lg p-8 bg-slate-50">
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-6">Model performance</p>
            <div className="space-y-5">
              {[
                { label: 'Deceptive-class recall', value: '85.2%', note: 'of deceptive reviews detected' },
                { label: 'Deceptive-class precision', value: '66.5%', note: 'when flagged, likely deceptive' },
                { label: 'Decision threshold', value: '0.40', note: 'probability cutoff' },
                { label: 'False-positive rate', value: '41.3%', note: 'known limitation', warn: true },
              ].map(({ label, value, note, warn }) => (
                <div key={label} className="flex justify-between items-start gap-4">
                  <div>
                    <p className="text-sm font-medium text-slate-700">{label}</p>
                    <p className="text-xs text-slate-400">{note}</p>
                  </div>
                  <span className={`text-lg font-semibold ${warn ? 'text-amber-600' : 'text-slate-900'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-6 leading-relaxed">
              The model achieves high deceptive-review recall but has a relatively high false-positive rate.
              Results are estimates, not definitive verdicts.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200 py-6">
        <div className="max-w-5xl mx-auto px-6 text-xs text-slate-400">
          ReviewGuard AI · Phase 4 · ML pipeline built in Phase 3B
        </div>
      </footer>
    </div>
  );
}
