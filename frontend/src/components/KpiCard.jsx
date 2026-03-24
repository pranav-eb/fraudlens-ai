import { motion } from 'framer-motion'

export default function KpiCard({ label, value, sub, icon: Icon, color, delay = 0, id }) {
  return (
    <motion.div
      id={id}
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -4, borderColor: 'rgba(255,255,255,0.15)' }}
      className="glass p-6 flex items-center gap-5 transition-all duration-300 group"
    >
      <div
        className="flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110"
        style={{ background: 'rgba(15, 23, 42, 0.4)', border: `1px solid ${color}40` }}
      >
        <Icon size={24} style={{ color }} />
      </div>
      <div className="min-w-0">
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.15em] truncate mb-1">{label}</p>
        <p className="font-black text-3xl leading-tight tracking-tight text-white">
          {value}
        </p>
        {sub && <p className="text-[11px] text-slate-400 mt-1 font-medium truncate">{sub}</p>}
      </div>
    </motion.div>
  )
}
