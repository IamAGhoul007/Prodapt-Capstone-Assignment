import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Activity, MapPin, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

const API = "http://localhost:8000";

const Dashboard = () => {
  const [data, setData] = useState({ summary: null, peak: null, region: null, prediction: null });
  const [loading, setLoading] = useState(true);
  const [region, setRegion] = useState('Centro');
  const [form, setForm] = useState({ region: 'Centro', avg_usage: 1500, growth_rate: 0.1, variability: 0.2 });

  useEffect(() => {
    const init = async () => {
      try {
        const [s, p] = await Promise.all([axios.get(`${API}/usage/summary`), axios.get(`${API}/usage/peak`)]);
        const r = await axios.get(`${API}/usage/region/Centro`);
        setData(prev => ({ ...prev, summary: s.data, peak: p.data, region: r.data }));
      } catch (e) { console.error(e); } finally { setLoading(false); }
    };
    init();
  }, []);

  const search = async () => {
    const r = await axios.get(`${API}/usage/region/${region}`);
    setData(prev => ({ ...prev, region: r.data }));
  };

  const predict = async (e) => {
    e.preventDefault();
    const res = await axios.post(`${API}/predict-usage-risk`, form);
    setData(prev => ({ ...prev, prediction: res.data }));
  };

  if (loading) return <div className="flex items-center justify-center h-screen bg-slate-900 text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="mb-10">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">Network Intelligence</h1>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <Card title="Calls" val={data.summary?.total_calls.toLocaleString()} ic={<Activity className="text-blue-400"/>}/>
        <Card title="SMS" val={data.summary?.total_sms.toLocaleString()} ic={<Activity className="text-indigo-400"/>}/>
        <Card title="Internet" val={Math.round(data.summary?.total_internet_mb).toLocaleString()} ic={<Activity className="text-purple-400"/>}/>
        <Card title="Peak" val={`${data.summary?.peak_hour}:00`} ic={<Clock className="text-orange-400"/>}/>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2"><MapPin/> Explorer</h2>
            <div className="flex gap-2">
              <input value={region} onChange={e=>setRegion(e.target.value)} className="bg-slate-800 border border-slate-700 px-3 py-1 rounded-lg"/>
              <button onClick={search} className="bg-blue-600 px-3 py-1 rounded-lg">Go</button>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer><LineChart data={data.region?.hourly_distribution}><CartesianGrid stroke="#1e293b"/><XAxis dataKey="hour"/><YAxis/><Tooltip/><Line dataKey="calls" stroke="#60a5fa" dot={false}/></LineChart></ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2"><Clock/> Top Regions</h2>
          <div className="h-64">
            <ResponsiveContainer><BarChart data={data.peak?.top_regions}><CartesianGrid stroke="#1e293b"/><XAxis dataKey="region"/><YAxis/><Tooltip/><Bar dataKey="total_usage" fill="#818cf8" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl lg:col-span-2">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2"><ShieldCheck/> Predictor</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <form onSubmit={predict} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input label="Region" val={form.region} set={v=>setForm({...form, region:v})}/>
                <Input label="Usage" val={form.avg_usage} set={v=>setForm({...form, avg_usage:v})} type="number"/>
                <Input label="Growth" val={form.growth_rate} set={v=>setForm({...form, growth_rate:v})} type="number" step="0.01"/>
                <Input label="Var" val={form.variability} set={v=>setForm({...form, variability:v})} type="number" step="0.01"/>
              </div>
              <button type="submit" className="w-full bg-blue-600 py-3 rounded-xl font-medium">Analyze</button>
            </form>
            <div className={`p-6 rounded-2xl border flex flex-col items-center justify-center ${data.prediction ? 'bg-slate-800/50' : 'bg-slate-900/30'}`}>
              {data.prediction ? (
                <>
                  <div className={`text-4xl font-bold ${data.prediction.congestion_risk === 'HIGH' ? 'text-red-400' : 'text-green-400'}`}>{data.prediction.congestion_risk}</div>
                  <div className="text-slate-400">Score: {(data.prediction.score*100).toFixed(1)}%</div>
                  {data.prediction.anomaly_flag && <div className="mt-4 text-red-500 flex items-center gap-2"><AlertTriangle/> Anomaly</div>}
                </>
              ) : "Ready"}
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
