import { useState } from 'react'
import { motion } from 'framer-motion'

const SCORE_RANGES = {
  high:   { min: 0.70, label: 'HIGH',   cls: 'score-high'   },
  medium: { min: 0.40, label: 'MEDIUM', cls: 'score-medium' },
  low:    { min: 0,    label: 'LOW',    cls: 'score-low'    },
}

function getScoreBadge(score) {
  if (score >= 0.70) return SCORE_RANGES.high
  if (score >= 0.40) return SCORE_RANGES.medium
  return SCORE_RANGES.low
}

const fmt = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })

const PAGE_SIZE = 15

export default function FraudTable({ transactions }) {
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')

  if (!transactions || transactions.length === 0) {
    return (
      <div className="glass p-8 text-center text-slate-500">
        No fraud transactions to display.
      </div>
    )
  }

  const filtered = search
    ? transactions.filter(t =>
        t.transaction_id?.toLowerCase().includes(search.toLowerCase()) ||
        t.user_id?.toLowerCase().includes(search.toLowerCase()) ||
        t.city?.toLowerCase().includes(search.toLowerCase())
      )
    : transactions

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const slice = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
      <div className="glass overflow-hidden">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 border-b"
          style={{ borderColor: 'rgba(245,200,66,0.12)' }}>
          <div>
            <h3 className="font-bold text-slate-100 text-lg">Fraud Transaction Log</h3>
            <p className="text-slate-500 text-xs mt-0.5">{filtered.length} flagged records</p>
          </div>
          <input
            id="fraud-table-search"
            type="text"
            placeholder="Search by ID, user, city…"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            className="px-4 py-2 rounded-lg text-sm outline-none w-full sm:w-64 transition-all"
            style={{
              background: 'rgba(14,40,71,0.70)',
              border: '1px solid rgba(245,200,66,0.18)',
              color: '#E2E8F0',
            }}
          />
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full fraud-table">
            <thead>
              <tr>
                <th>Txn ID</th>
                <th>User ID</th>
                <th>Amount</th>
                <th>City</th>
                <th>Hour</th>
                <th>Score</th>
                <th className="min-w-64">Reason</th>
              </tr>
            </thead>
            <tbody>
              {slice.map((txn, i) => {
                const badge = getScoreBadge(txn.fraud_score || 0)
                return (
                  <motion.tr
                    key={txn.transaction_id || i}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                  >
                    <td className="font-mono text-xs text-slate-300">{txn.transaction_id}</td>
                    <td className="font-medium text-slate-200">{txn.user_id}</td>
                    <td className="font-semibold" style={{ color: '#FB7185' }}>
                      {typeof txn.amount === 'number' ? fmt.format(txn.amount) : txn.amount}
                    </td>
                    <td>{txn.city || '—'}</td>
                    <td>{txn.hour != null ? `${txn.hour}:00` : '—'}</td>
                    <td>
                      <span className={`score-badge ${badge.cls}`}>
                        {badge.label} · {((txn.fraud_score || 0) * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="text-xs text-slate-400 max-w-xs whitespace-normal leading-relaxed">
                      {txn.reason || '—'}
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-4 border-t"
            style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
            <p className="text-xs text-slate-500">
              Page {page + 1} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                id="table-prev-btn"
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-30 transition-all hover:scale-105"
                style={{ background: 'rgba(14,40,71,0.8)', border: '1px solid rgba(245,200,66,0.20)', color: '#F5C842' }}
              >
                ← Prev
              </button>
              <button
                id="table-next-btn"
                disabled={page >= totalPages - 1}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-30 transition-all hover:scale-105"
                style={{ background: 'rgba(14,40,71,0.8)', border: '1px solid rgba(245,200,66,0.20)', color: '#F5C842' }}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
