import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, AlertTriangle, CheckCircle, Zap, ShieldCheck } from 'lucide-react'
import axios from 'axios'

const UPLOAD_STEPS = [
  'Initializing secure ingestion…',
  'Normalizing transaction vectors…',
  'Executing behavioral feature engine…',
  'Running neural fraud detection…',
  'Synthesizing pattern intelligence…',
  'Generating explainability report…',
]

export default function UploadPage({ setResult, isUploading, setIsUploading }) {
  const [file, setFile]     = useState(null)
  const [progress, setProgress] = useState(0)
  const [stepIdx, setStepIdx]   = useState(0)
  const [error, setError]       = useState(null)
  const [isDone, setIsDone]     = useState(false)

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) { setFile(accepted[0]); setError(null) }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'application/vnd.ms-excel': ['.csv'] },
    maxFiles: 1,
    disabled: isUploading,
  })

  const formatBytes = (b) => {
    if (b < 1024) return `${b} B`
    if (b < 1_048_576) return `${(b/1024).toFixed(1)} KB`
    return `${(b/1_048_576).toFixed(1)} MB`
  }

  const handleAnalyse = async () => {
    if (!file) return
    setIsUploading(true)
    setProgress(0)
    setStepIdx(0)
    setError(null)
    setIsDone(false)

    // Simulate steps while waiting for the API
    const totalDuration = 12000  // 12s total simulated progress
    const stepDuration  = totalDuration / UPLOAD_STEPS.length
    let elapsed = 0
    const progressInterval = setInterval(() => {
      elapsed += 200
      const pct = Math.min(95, Math.round((elapsed / totalDuration) * 95))
      setProgress(pct)
      setStepIdx(Math.min(UPLOAD_STEPS.length - 1, Math.floor(elapsed / stepDuration)))
    }, 200)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await axios.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300_000,
      })
      clearInterval(progressInterval)
      setProgress(100)
      setStepIdx(UPLOAD_STEPS.length - 1)
      setIsDone(true)
      setTimeout(() => {
        setIsUploading(false)
        setResult(res.data)
      }, 800)
    } catch (err) {
      clearInterval(progressInterval)
      setIsUploading(false)
      setProgress(0)
      const msg = err.response?.data?.detail || err.message || 'Upload failed. Please try again.'
      setError(msg)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-20 bg-navy-950 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] bg-gradient-to-b from-accent-primary/5 to-transparent pointer-events-none" />
      
      {/* Hero text */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="text-center mb-16 relative z-10"
      >
        <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full mb-8 text-[10px] font-black tracking-[0.2em] uppercase border border-white/10 bg-white/5 text-accent-primary backdrop-blur-sm">
          <ShieldCheck size={14} />
          Military-Grade Analysis Engine
        </div>
        <h2 className="text-6xl sm:text-7xl font-black leading-tight mb-6 tracking-tighter">
          <span className="text-white">Secure Fraud</span> <br />
          <span className="text-slate-600">Intelligence.</span>
        </h2>
        <p className="text-slate-400 text-xl max-w-2xl mx-auto leading-relaxed font-medium">
          Deploy enterprise-grade behavioral heuristics and neural clustering to identify high-risk transactions in seconds. 
          Upload your data to begin the session.
        </p>
      </motion.div>

      {/* Upload card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass w-full max-w-2xl p-10 relative z-10 shadow-2xl"
      >
        <AnimatePresence mode="wait">
          {!isUploading ? (
            <motion.div key="dropzone" exit={{ opacity: 0, scale: 0.95 }} transition={{ duration: 0.3 }}>
              <div
                {...getRootProps()}
                id="csv-dropzone"
                className={`relative flex flex-col items-center justify-center p-16 rounded-2xl border-2 border-dashed border-white/10 cursor-pointer transition-all duration-500 bg-navy-900/50 hover:bg-navy-900/80 hover:border-accent-primary/30 ${isDragActive ? 'border-accent-primary bg-navy-900 shadow-2xl shadow-accent-primary/5' : ''}`}
              >
                <input {...getInputProps()} id="csv-file-input" />
                <div className="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 bg-navy-950 border border-white/5 shadow-inner">
                  <Upload size={32} className={isDragActive ? 'text-accent-primary' : 'text-slate-400'} />
                </div>
                <p className="text-white font-black text-2xl mb-2 tracking-tight">
                  {isDragActive ? 'Release to Scan' : 'Drop Dataset'}
                </p>
                <p className="text-slate-500 text-sm font-medium tracking-wide">or select CSV file · max 200 MB</p>

                {file && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-8 flex items-center gap-4 px-5 py-4 rounded-xl bg-accent-primary/10 border border-accent-primary/20 shadow-lg"
                  >
                    <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                      <FileText size={20} className="text-accent-primary" />
                    </div>
                    <div className="text-left">
                      <p className="text-accent-primary font-black text-sm leading-tight">{file.name}</p>
                      <p className="text-slate-500 text-[10px] font-bold uppercase mt-1 tracking-widest">{formatBytes(file.size)}</p>
                    </div>
                    <div className="ml-4 w-6 h-6 rounded-full bg-accent-primary flex items-center justify-center">
                      <CheckCircle size={14} className="text-navy-950" />
                    </div>
                  </motion.div>
                )}
              </div>

              <motion.button
                id="analyse-btn"
                onClick={handleAnalyse}
                disabled={!file}
                whileHover={file ? { scale: 1.01, y: -2 } : undefined}
                whileTap={file ? { scale: 0.99 } : undefined}
                className={`mt-10 w-full py-5 rounded-2xl font-black text-lg tracking-tight transition-all duration-300 ${file ? 'bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-xl shadow-accent-primary/20 hover:opacity-95' : 'bg-navy-800 text-slate-600 border border-white/5 cursor-not-allowed'}`}
              >
                {file ? 'Initialize Deep Scan' : 'Awaiting Data Source…'}
              </motion.button>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 flex items-start gap-4 p-5 rounded-2xl bg-accent-error/10 border border-accent-error/20"
                >
                  <AlertTriangle size={20} className="text-accent-error mt-0.5 flex-shrink-0" />
                  <p className="text-accent-error text-sm font-bold leading-relaxed">{error}</p>
                </motion.div>
              )}
            </motion.div>
          ) : (
            <motion.div key="processing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="py-6">
              <div className="flex items-end justify-between mb-6">
                <div>
                  <p className="text-[10px] font-black text-accent-primary uppercase tracking-[0.2em] mb-2">Neural Pipeline Status</p>
                  <h3 className="text-2xl font-black text-white tracking-tight">
                    {isDone ? 'Sequence Complete' : UPLOAD_STEPS[stepIdx]}
                  </h3>
                </div>
                <span className="text-4xl font-black text-white tracking-tighter" style={{ color: isDone ? 'var(--accent-success)' : 'white' }}>
                  {progress}%
                </span>
              </div>
              
              <div className="h-4 w-full bg-navy-900 rounded-full overflow-hidden border border-white/5 mb-10 shadow-inner p-1">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                  style={{ width: `${progress}%` }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                {UPLOAD_STEPS.map((step, i) => (
                  <div key={step} className={`flex items-center gap-3 text-[11px] font-bold uppercase tracking-wider transition-all duration-500 ${i <= stepIdx ? 'text-slate-300' : 'text-slate-600'}`}>
                    <div className={`w-2 h-2 rounded-full transition-all duration-300 ${i < stepIdx ? 'bg-accent-success shadow-[0_0_8px_var(--accent-success)]' : i === stepIdx ? 'bg-accent-primary animate-pulse' : 'bg-slate-800'}`} />
                    {step}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Feature pills */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-12 flex flex-wrap items-center justify-center gap-4"
      >
        {['Neural Heuristics', 'Vector Engine', 'Explainable AI', 'ISO 27001 Ready'].map(f => (
          <span key={f} className="px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-[0.1em] border border-white/5 bg-white/5 text-slate-500 backdrop-blur-sm">
            {f}
          </span>
        ))}
      </motion.div>
    </div>
  )
}
