import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Activity, MapPin, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

const API = "http://localhost:8000";

const Dashboard = () => {
  const [data, setData] = useState({ summary: null, peak: null, region: null, prediction: null, regions: [] });
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [region, setRegion] = useState('VICENZA');
  const [form, setForm] = useState({ region: 'VICENZA', avg_usage: 1500, growth_rate: 0.1, variability: 0.2 });

  useEffect(() => {
    const init = async () => {
      try {
        console.log("Starting dashboard initialization...");
        const [s, p, r_list] = await Promise.all([
          axios.get(`${API}/usage/summary`).catch(e => { console.error("Summary failed:", e); return { data: null }; }),
          axios.get(`${API}/usage/peak`).catch(e => { console.error("Peak failed:", e); return { data: null }; }),
          axios.get(`${API}/regions`).catch(e => { console.error("Regions failed:", e); return { data: ['VICENZA', 'MILANO', 'ROMA'] }; })
        ]);
        const r = await axios.get(`${API}/usage/region/VICENZA`).catch(e => { console.error("Initial region failed:", e); return { data: null }; });
        
        const regions = (r_list.data && r_list.data.length > 0) ? r_list.data : ['VICENZA', 'MILANO', 'ROMA'];
        setData({ summary: s.data, peak: p.data, region: r.data, prediction: null, regions: regions });
      } catch (e) {
        console.error("Initialization error:", e);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const search = async (selectedRegion) => {
    const target = selectedRegion || region;
    setLoading(true);
    try {
      const r = await axios.get(`${API}/usage/region/${target}`);
      setData(prev => ({ ...prev, region: r.data }));
      setRegion(target);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const predict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    try {
      // Ensure numeric types for the backend
      const payload = {
        ...form,
        avg_usage: parseFloat(form.avg_usage),
        growth_rate: parseFloat(form.growth_rate),
        variability: parseFloat(form.variability)
      };
      const res = await axios.post(`${API}/predict-usage-risk`, payload);
      setData(prev => ({ ...prev, prediction: res.data }));
    } catch (e) { 
      console.error("Prediction error:", e);
      alert("Prediction failed. Please check the console for details.");
    } finally { 
      setPredicting(false); 
    }
  };

  if (loading && !data.summary) return <div className="flex items-center justify-center h-screen bg-slate-900 text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="mb-10 flex justify-between items-center">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">Network Intelligence</h1>
        <div className="text-slate-500 text-sm">Real-time Data Active</div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <Card title="Calls" val={data.summary?.total_calls?.toLocaleString() || "0"} ic={<Activity className="text-blue-400"/>}/>
        <Card title="SMS" val={data.summary?.total_sms?.toLocaleString() || "0"} ic={<Activity className="text-indigo-400"/>}/>
        <Card title="Internet" val={Math.round(data.summary?.total_internet_mb || 0).toLocaleString()} ic={<Activity className="text-purple-400"/>}/>
        <Card title="Peak" val={`${data.summary?.peak_hour || "00"}:00`} ic={<Clock className="text-orange-400"/>}/>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2"><MapPin/> Explorer</h2>
            <div className="flex gap-2">
              <select value={region} onChange={e=>search(e.target.value)} className="bg-slate-800 border border-slate-700 px-3 py-1 rounded-lg text-sm w-48">
                {data.regions.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center">
            {loading ? <div className="text-slate-500 italic">Updating chart...</div> : (
              <ResponsiveContainer><LineChart data={data.region?.hourly_distribution}><CartesianGrid stroke="#1e293b"/><XAxis dataKey="hour"/><YAxis/><Tooltip/><Line dataKey="calls" stroke="#60a5fa" dot={false} strokeWidth={2}/></LineChart></ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2"><Clock/> Top Regions</h2>
          <div className="h-64">
            <ResponsiveContainer><BarChart data={data.peak?.top_regions}><CartesianGrid stroke="#1e293b"/><XAxis dataKey="region" tick={{fontSize: 10}}/><YAxis/><Tooltip/><Bar dataKey="total" fill="#818cf8" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl lg:col-span-2">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2"><ShieldCheck/> Predictor</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <form onSubmit={predict} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Region</label>
                  <select value={form.region} onChange={v=>setForm({...form, region:v.target.value})} className="w-full bg-slate-800 border border-slate-700 p-2 rounded-lg text-sm">
                    {data.regions.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>
                <Input label="Usage" val={form.avg_usage} set={v=>setForm({...form, avg_usage:v})} type="number"/>
                <Input label="Growth" val={form.growth_rate} set={v=>setForm({...form, growth_rate:v})} type="number" step="0.01"/>
                <Input label="Var" val={form.variability} set={v=>setForm({...form, variability:v})} type="number" step="0.01"/>
              </div>
              <button type="submit" disabled={predicting} className={`w-full bg-blue-600 py-3 rounded-xl font-medium transition ${predicting ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}>
                {predicting ? "Predicting..." : "Analyze"}
              </button>
            </form>
            <div className={`p-6 rounded-2xl border flex flex-col items-center justify-center transition ${data.prediction ? 'bg-slate-800/50 border-blue-500/50' : 'bg-slate-900/30 border-slate-800'}`}>
              {predicting ? <div className="text-blue-400 animate-pulse">Calculating Risk...</div> : data.prediction ? (
                <>
                  <div className={`text-4xl font-bold mb-2 ${data.prediction.congestion_risk === 'HIGH' ? 'text-red-400' : data.prediction.congestion_risk === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400'}`}>{data.prediction.congestion_risk}</div>
                  <div className="text-slate-400">Certainty: {(data.prediction.score*100).toFixed(1)}%</div>
                  {data.prediction.anomaly_flag && <div className="mt-4 text-red-500 flex items-center gap-2 bg-red-500/10 px-4 py-2 rounded-full border border-red-500/20"><AlertTriangle size={16}/> Anomaly Detected</div>}
                </>
              ) : <div className="text-slate-600 italic">Adjust parameters and Analyze</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Card = ({ title, val, ic }) => (
  <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl flex justify-between items-start">
    <div><h3 className="text-slate-400 text-sm">{title}</h3><div className="text-2xl font-bold">{val}</div></div>
    <div className="p-2 bg-slate-800 rounded-lg">{ic}</div>
  </div>
);

const Input = ({ label, val, set, ...props }) => (
  <div><label className="block text-xs text-slate-400 mb-1">{label}</label><input value={val} onChange={e=>set(e.target.value)} className="w-full bg-slate-800 border border-slate-700 p-2 rounded-lg" {...props}/></div>
);

export default Dashboard;
