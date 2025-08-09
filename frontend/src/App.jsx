import React from 'react'
import Dashboard from './components/Dashboard'

export default function App(){
  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">CryptoDCA.ai — Demo</h1>
        <Dashboard />
      </div>
    </div>
  )
}
