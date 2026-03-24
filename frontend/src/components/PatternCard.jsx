import { motion } from 'framer-motion'
import { TrendingUp, Zap, Smartphone, MapPin, Share2, Target } from 'lucide-react'

const PATTERN_ICONS = {
  'High-Value Spike Fraud':       TrendingUp,
  'Rapid Micro-Transaction Fraud': Zap,
  'New Device Fraud':             Smartphone,
  'Location Anomaly Fraud':       MapPin,
  'Shared Device Fraud':          Share2,
  'Rapid Burst Fraud':            Target,
}

const PATTERN_COLORS = {
  'High-Value Spike Fraud':       'var(--accent-error)',
  'Rapid Micro-Transaction Fraud':'var(--accent-warning)',
  'New Device Fraud':             'var(--accent-primary)',
  'Location Anomaly Fraud':       'var(--accent-secondary)',
  'Shared Device Fraud':          'var(--accent-success)',
  'Rapid Burst Fraud':            'var(--accent-error)',
}

export default function PatternCard({ pattern, index, totalFraud }) {
  const { pattern_name, count, description, dominant_feature } = pattern
  const Icon   = PATTERN_ICONS[pattern_name] || Target
  const color  = PATTERN_COLORS[pattern_name] || 'var(--accent-primary)'
  const pct    = totalFraud > 0 ? Math.round((count / totalFraud) * 100) : 0

  return (
    <motion.div
      id={`pattern-card-${index}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 * index }}
      whileHover={{ y: -4, borderColor: 'rgba(255,255,255,0.1)' }}
      className="glass p-6 group transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-navy-900 border border-white/5 flex items-center justify-center transition-transform group-hover:scale-110">
            <Icon size={24} style={{ color }} />
          </div>
          <div>
            <h4 className="font-black text-white text-sm tracking-tight">{pattern_name}</h4>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400 font-mono tracking-wider border border-white/5 uppercase">
                {dominant_feature}
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-black text-white leading-none">{count}</div>
          <div className="text-[10px] text-slate-500 font-bold uppercase mt-1">Events</div>
        </div>
      </div>

      <p className="text-slate-400 text-xs leading-relaxed mb-6 font-medium">
        {description}
      </p>

      <div className="space-y-3">
        <div className="flex justify-between items-end">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Incident Density</span>
          <span className="text-xs font-black" style={{ color }}>{pct}%</span>
        </div>
        <div className="h-1.5 w-full bg-navy-900 rounded-full overflow-hidden border border-white/5">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ delay: 0.4 + index * 0.1, duration: 0.8 }}
            className="h-full rounded-full"
            style={{ background: color, boxShadow: `0 0 12px ${color}40` }}
          />
        </div>
      </div>
    </motion.div>
  )
}
