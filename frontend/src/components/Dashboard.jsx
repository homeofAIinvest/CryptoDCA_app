import React, {useState} from 'react'

export default function Dashboard(){
  const [tickers, setTickers] = useState(['BTC','ETH','SOL'])
  const [monthly, setMonthly] = useState(50)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  async function runSim(){
    setLoading(true)
    try{
      const res = await fetch('http://localhost:8000/simulate', {
        method: 'POST',
        headers: {'Content-Type':'application/json', 'Authorization': 'Bearer demo'},
        body: JSON.stringify({tickers, monthly})
      })
      const data = await res.json()
      setResult(data)
    }catch(e){
      setResult({error: e.toString()})
    }
    setLoading(false)
  }

  return (
    <div className="bg-white p-4 rounded shadow">
      <label className="block mb-2">Tickers (comma separated)</label>
      <input className="border p-2 mb-2 w-full" value={tickers.join(',')} onChange={e=>setTickers(e.target.value.split(',').map(t=>t.trim().toUpperCase()))} />
      <label className="block mb-2">Monthly £</label>
      <input type="number" className="border p-2 mb-2 w-32" value={monthly} onChange={e=>setMonthly(Number(e.target.value))} />
      <div>
        <button className="bg-indigo-600 text-white px-4 py-2 rounded" onClick={runSim} disabled={loading}>{loading? 'Running...':'Run Simulation'}</button>
      </div>

      {result && (
        <div className="mt-4">
          <h3 className="font-semibold">Results</h3>
          <pre className="bg-slate-100 p-2 rounded text-sm overflow-auto max-h-64">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
