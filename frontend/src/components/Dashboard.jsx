import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity, AlertTriangle, CheckCircle2, Layers, Star, Shield,
  ChevronDown, ChevronUp, Database, Download,
} from 'lucide-react'
import KpiCard from './KpiCard.jsx'
import PatternCard from './PatternCard.jsx'
import FraudTable from './FraudTable.jsx'
import { FraudByDateChart, FraudByCityChart, TopUsersChart } from './Charts.jsx'

const fmt = new Intl.NumberFormat('en-IN')

function JudgingScorecard({ fraudCount, patternCount, processingTime }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
    >
      {[
        { label: 'Fraud Identified', value: fraudCount, sub: 'High Confidence Flags', icon: AlertTriangle, color: 'var(--accent-error)' },
        { label: 'Patterns Detected', value: patternCount, sub: 'Behavioral Clusters', icon: Layers, color: 'var(--accent-warning)' },
        { label: 'Processing Latency', value: `${processingTime}s`, sub: 'Real-time Pipeline', icon: Activity, color: 'var(--accent-primary)' },
      ].map((m, i) => (
        <div key={i} className="glass p-6 flex items-center justify-between group hover:border-white/20 transition-all">
          <div>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.15em] mb-2">{m.label}</p>
            <p className="text-4xl font-black text-white tracking-tight">{m.value}</p>
            <p className="text-[11px] text-slate-400 mt-2 font-medium flex items-center gap-1.5 line-clamp-1">
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: m.color }}></span>
              {m.sub}
            </p>
          </div>
          <div className="p-3 rounded-xl bg-navy-900/50 border border-white/5 group-hover:scale-110 transition-transform">
            <m.icon size={24} style={{ color: m.color }} />
          </div>
        </div>
      ))}
    </motion.div>
  )
}

function QualitySection({ report }) {
  const [open, setOpen] = useState(false)
  if (!report) return null

  const score = report.quality_score ?? 0
  const scoreColor = score >= 80 ? '#34D399' : score >= 60 ? '#F5C842' : '#FB7185'

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
      <div className="glass overflow-hidden">
        <button
          id="quality-section-toggle"
          onClick={() => setOpen(o => !o)}
          className="w-full flex items-center justify-between p-5 hover:bg-white/5 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Database size={18} style={{ color: scoreColor }} />
            <div className="text-left">
              <p className="font-bold text-slate-200 text-sm">Data Quality Report</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {report.total_rows_original?.toLocaleString()} rows processed → {report.clean_rows?.toLocaleString()} clean rows
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-black text-3xl leading-none" style={{ color: scoreColor }}>{score}</p>
              <p className="text-xs text-slate-500">/ 100</p>
            </div>
            {open ? <ChevronUp size={16} className="text-slate-500" /> : <ChevronDown size={16} className="text-slate-500" />}
          </div>
        </button>

        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="border-t px-5 pb-5"
            style={{ borderColor: 'rgba(245,200,66,0.12)' }}
          >
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
              {[
                { label: 'Missing Values',    value: fmt.format(report.missing_values?.total_missing ?? 0), color: '#FB7185' },
                { label: 'Duplicate Rows',    value: fmt.format(report.duplicates?.duplicate_rows_removed ?? 0), color: '#F5C842' },
                { label: 'Duplicate Txn IDs', value: fmt.format(report.duplicates?.duplicate_txn_ids_removed ?? 0), color: '#F5C842' },
                { label: 'Invalid IPs',       value: fmt.format(report.ip_quality?.invalid_ip_count ?? 0), color: '#FB7185' },
                { label: 'Imputed Amounts',   value: fmt.format(report.amount_imputed_count ?? 0), color: '#22D3EE' },
                { label: 'Bad Timestamps',    value: fmt.format(report.timestamp_issues ?? 0), color: '#A78BFA' },
              ].map(({ label, value, color }) => (
                <div key={label} className="glass-light p-3 text-center">
                  <p className="font-bold text-lg" style={{ color }}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5 leading-tight">{label}</p>
                </div>
              ))}
            </div>

            {/* Missing by column */}
            {report.missing_values?.per_column && Object.keys(report.missing_values.per_column).length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Missing per Column</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {Object.entries(report.missing_values.per_column).slice(0, 8).map(([col, cnt]) => (
                    <div key={col} className="flex justify-between px-3 py-2 rounded-lg text-xs"
                      style={{ background: 'rgba(14,40,71,0.60)', border: '1px solid rgba(255,255,255,0.06)' }}>
                      <span className="text-slate-400 font-mono">{col}</span>
                      <span className="text-rose-400 font-semibold">{fmt.format(cnt)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default function Dashboard({ result, onReset }) {
  const {
    total_transactions = 0,
    fraud_count        = 0,
    fraud_percentage   = 0,
    data_quality_report,
    fraud_patterns     = [],
    analytics          = {},
    metrics            = { processing_time: 0, pattern_count: 0 },
    top_fraud_transactions = [],
  } = result || {}

  const qualityScore = data_quality_report?.quality_score ?? 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Judging Scorecard (Criteria 1, 2, 3) */}
      <JudgingScorecard 
        fraudCount={fmt.format(fraud_count)} 
        patternCount={metrics.pattern_count} 
        processingTime={metrics.processing_time} 
      />


      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div>
          <h2 className="font-black text-3xl text-white">Analysis Results</h2>
          <p className="text-slate-400 text-sm mt-1">
            Engine detection complete — {fmt.format(total_transactions)} transactions analysed
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => { window.location.href = 'http://127.0.0.1:8000/download' }}
            className="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-accent-primary to-accent-secondary text-white transition-all hover:opacity-90 hover:shadow-xl hover:shadow-accent-primary/20"
          >
            <Download size={16} /> Export Intel
          </button>
          <button
            id="dashboard-new-analysis-btn"
            onClick={onReset}
            className="px-6 py-3 rounded-xl text-sm font-bold border border-white/10 bg-navy-800 text-white transition-all hover:bg-navy-700"
          >
            New Session
          </button>
        </div>
      </motion.div>

      {/* ── KPI cards ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard id="kpi-total-txns"   label="Volume"          value={fmt.format(total_transactions)} icon={Activity}      color="var(--accent-primary)" delay={0}   />
        <KpiCard id="kpi-fraud-count"  label="Detected"        value={fmt.format(fraud_count)}        icon={AlertTriangle}  color="var(--accent-error)"   delay={0.08} />
        <KpiCard id="kpi-fraud-pct"    label="Risk Rate"       value={`${fraud_percentage}%`}         icon={Shield}         color="var(--accent-warning)" delay={0.12} />
        <KpiCard id="kpi-quality"      label="Data Health"     value={`${qualityScore}%`}             icon={CheckCircle2}   color={qualityScore >= 80 ? 'var(--accent-success)' : qualityScore >= 60 ? 'var(--accent-warning)' : 'var(--accent-error)'} delay={0.16} />
      </div>

      {/* ── Data quality ────────────────────────────────────────────── */}
      <QualitySection report={data_quality_report} />

      {/* ── Fraud pattern cards ─────────────────────────────────────── */}
      {fraud_patterns.length > 0 && (
        <section id="fraud-patterns-section">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            <div className="flex items-center gap-2 mb-4">
              <Layers size={18} style={{ color: '#F5C842' }} />
              <h3 className="font-bold text-slate-100 text-xl">Fraud Pattern Intelligence</h3>
              <span className="px-2 py-0.5 rounded-full text-xs font-bold ml-1"
                style={{ background: 'rgba(251,113,133,0.15)', color: '#FB7185', border: '1px solid rgba(251,113,133,0.30)' }}>
                {fraud_patterns.length} clusters
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {fraud_patterns.map((p, i) => (
                <PatternCard key={p.pattern_name || i} pattern={p} index={i} totalFraud={fraud_count} />
              ))}
            </div>
          </motion.div>
        </section>
      )}

      {/* ── Charts ─────────────────────────────────────────────────── */}
      <section id="charts-section">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <div className="flex items-center gap-2 mb-4">
            <Star size={18} style={{ color: '#F5C842' }} />
            <h3 className="font-bold text-slate-100 text-xl">Analytics</h3>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <FraudByDateChart data={analytics.fraud_by_date} />
            <FraudByCityChart data={analytics.fraud_by_city} />
          </div>
          {analytics.top_risky_users?.length > 0 && (
            <div className="mt-5">
              <TopUsersChart data={analytics.top_risky_users} />
            </div>
          )}
        </motion.div>
      </section>

      {/* ── Fraud table ─────────────────────────────────────────────── */}
      <section id="fraud-table-section">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={18} style={{ color: '#FB7185' }} />
            <h3 className="font-bold text-slate-100 text-xl">Top Flagged Transactions</h3>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold ml-1"
              style={{ background: 'rgba(251,113,133,0.15)', color: '#FB7185', border: '1px solid rgba(251,113,133,0.30)' }}>
              top {top_fraud_transactions.length}
            </span>
          </div>
          <FraudTable transactions={top_fraud_transactions} />
        </motion.div>
      </section>

    </div>
  )
}
