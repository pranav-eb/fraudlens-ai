import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area,
} from 'recharts'
import { motion } from 'framer-motion'

const CHART_CARD_STYLE = {
  background: 'rgba(30, 41, 59, 0.4)',
  backdropFilter: 'blur(12px)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: 16,
  padding: '24px',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass px-4 py-3 text-xs border-white/10 shadow-2xl">
      <p className="text-slate-400 font-bold mb-2 uppercase tracking-wider">{label}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }}></div>
          <p className="text-white font-black">{p.name}: {p.value?.toLocaleString()}</p>
        </div>
      ))}
    </div>
  )
}

export function FraudByDateChart({ data }) {
  if (!data || data.length < 2) return null
  const sorted = [...data].sort((a, b) => a.date > b.date ? 1 : -1).slice(-30)
  return (
    <motion.div initial={{ opacity:0,y:20 }} animate={{ opacity:1,y:0 }} transition={{ delay:0.2 }} style={CHART_CARD_STYLE} className="group hover:border-white/10 transition-colors">
      <div className="flex justify-between items-start mb-6">
        <div>
          <p className="font-black text-white text-lg tracking-tight">Temporal Velocity</p>
          <p className="text-slate-500 text-[11px] font-medium uppercase tracking-wider">Daily Signal Frequency (30D)</p>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={sorted} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="var(--accent-error)" stopOpacity={0.4} />
              <stop offset="95%" stopColor="var(--accent-error)" stopOpacity={0}   />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="0" vertical={false} stroke="rgba(255,255,255,0.03)" />
          <XAxis dataKey="date" tick={{ fill: '#475569', fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false}
            tickFormatter={d => d?.slice(8)} dy={10} />
          <YAxis tick={{ fill: '#475569', fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} />
          <Area type="monotone" dataKey="frauds" name="Detections" stroke="var(--accent-error)" strokeWidth={3}
            fill="url(#fraudGrad)" dot={false} activeDot={{ r: 6, fill: '#FFF', stroke: 'var(--accent-error)', strokeWidth: 2 }} />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function FraudByCityChart({ data }) {
  if (!data || data.length === 0) return null
  return (
    <motion.div initial={{ opacity:0,y:20 }} animate={{ opacity:1,y:0 }} transition={{ delay:0.3 }} style={CHART_CARD_STYLE} className="group hover:border-white/10 transition-colors">
      <div className="flex justify-between items-start mb-6">
        <div>
          <p className="font-black text-white text-lg tracking-tight">Geospatial Distribution</p>
          <p className="text-slate-500 text-[11px] font-medium uppercase tracking-wider">Top Risk Hotspots</p>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 30, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="0" horizontal={false} stroke="rgba(255,255,255,0.03)" />
          <XAxis type="number" hide />
          <YAxis type="category" dataKey="city" tick={{ fill: '#94A3B8', fontSize: 11, fontWeight: 700 }} tickLine={false} axisLine={false} width={90} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
          <Bar dataKey="count" name="Signals" fill="var(--accent-primary)" radius={[0, 4, 4, 0]} maxBarSize={16} barSize={16} />
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function TopUsersChart({ data }) {
  if (!data || data.length === 0) return null
  return (
    <motion.div initial={{ opacity:0,y:20 }} animate={{ opacity:1,y:0 }} transition={{ delay:0.4 }} style={CHART_CARD_STYLE} className="group hover:border-white/10 transition-colors">
      <div className="mb-6">
        <p className="font-black text-white text-lg tracking-tight">Behavioral Risk Profiles</p>
        <p className="text-slate-500 text-[11px] font-medium uppercase tracking-wider">High Frequency Anomalies by Identity</p>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="0" vertical={false} stroke="rgba(255,255,255,0.03)" />
          <XAxis dataKey="user_id" tick={{ fill: '#475569', fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false}
            tickFormatter={u => u?.slice(-6)} dy={10} />
          <YAxis tick={{ fill: '#475569', fontSize: 10, fontWeight: 600 }} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
          <Bar dataKey="fraud_count" name="Violations" fill="var(--accent-warning)" radius={[4,4,0,0]} maxBarSize={24} />
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}
