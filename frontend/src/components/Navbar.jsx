import { motion } from 'framer-motion'
import { Scan, RefreshCw, Eye } from 'lucide-react'

export default function Navbar({ hasResult, onReset }) {
  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="relative z-20 flex items-center justify-between px-8 py-5 border-b border-white/5 bg-navy-900/80 backdrop-blur-md"
    >
      {/* Logo */}
      <div className="flex items-center gap-4">
        <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary p-[1px]">
          <div className="w-full h-full bg-navy-900 rounded-[11px] flex items-center justify-center">
            <Scan size={22} className="text-accent-primary" />
          </div>
        </div>
        <div>
          <h1 className="font-black text-2xl leading-none tracking-tight text-white flex items-center gap-2">
            FraudLens <span className="text-accent-primary font-medium text-lg">AI</span>
          </h1>
          <p className="text-[10px] text-slate-500 leading-none mt-1.5 uppercase tracking-[0.2em] font-bold">Enterprise Intelligence Unit</p>
        </div>
      </div>

      {/* Status + actions */}
      <div className="flex items-center gap-4">
        {hasResult && (
          <motion.button
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold border border-navy-600 bg-navy-700 text-white transition-all hover:bg-white hover:text-black"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            id="navbar-new-analysis-btn"
          >
            <RefreshCw size={14} /> Reset
          </motion.button>
        )}
      </div>
    </motion.nav>
  )
}
