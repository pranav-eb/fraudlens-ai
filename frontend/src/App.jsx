import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import UploadPage from './components/UploadPage.jsx'
import Dashboard from './components/Dashboard.jsx'
import Navbar from './components/Navbar.jsx'

export default function App() {
  const [result, setResult] = useState(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleReset = () => setResult(null)

  return (
    <div className="min-h-screen">
      <Navbar hasResult={!!result} onReset={handleReset} />

      <main className="relative z-10 w-full">
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <UploadPage
                setResult={setResult}
                isUploading={isUploading}
                setIsUploading={setIsUploading}
              />
            </motion.div>
          ) : (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <Dashboard result={result} onReset={handleReset} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
