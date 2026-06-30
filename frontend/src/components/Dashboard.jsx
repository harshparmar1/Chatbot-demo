import React, { useState } from "react";
import { 
  Activity, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp, 
  Users, 
  ShieldAlert, 
  Layers, 
  Award,
  Sparkles,
  ArrowUpRight,
  Clock,
  RefreshCw,
  Cpu,
  BarChart2,
  Calendar
} from "lucide-react";
import { 
  ComposedChart,
  Area, 
  BarChart, 
  Bar, 
  LineChart,
  Line,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from "recharts";

export default function Dashboard({ data, loading, onRefresh }) {
  const [isRetraining, setIsRetraining] = useState(false);
  const [retrainStatus, setRetrainStatus] = useState("");

  const handleRetrain = async () => {
    setIsRetraining(true);
    setRetrainStatus("Initiating ML training pipeline...");
    try {
      const res = await fetch("http://localhost:5000/api/retrain", {
        method: "POST",
      });
      const d = await res.json();
      if (d.success) {
        setRetrainStatus("Model retraining completed successfully!");
        onRefresh();
      } else {
        setRetrainStatus(d.message || "Failed to retrain models.");
      }
    } catch (e) {
      console.error(e);
      setRetrainStatus("Error connecting to training endpoint.");
    } finally {
      setTimeout(() => {
        setIsRetraining(false);
        setRetrainStatus("");
      }, 3000);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px]">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-hospital-500 mb-4"></div>
        <p className="text-slate-500 dark:text-slate-400 font-medium">Fetching hospital audit logs...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px] text-center p-6">
        <AlertTriangle className="h-16 w-16 text-red-500 mb-4 animate-bounce" />
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200 mb-2">Failed to Load Dashboard Data</h3>
        <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-md">
          Please check that your Flask backend server is running on port 5000 and the hospital CSV data is loaded.
        </p>
        <button 
          onClick={onRefresh}
          className="px-6 py-2.5 bg-hospital-600 hover:bg-hospital-700 text-white rounded-xl shadow-lg hover:shadow-hospital-500/25 transition-all duration-200 font-semibold"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Primary Metrics Card Data
  const primaryCards = [
    {
      title: "Overall Hospital Risk",
      value: `${data.overall_risk_score}/100`,
      icon: Activity,
      desc: `Highest Ward: ${data.high_risk_ward} (${data.high_risk_ward_score})`,
      color: "from-amber-500/10 to-red-500/10 border-red-500/20 text-red-600 dark:text-red-400",
      iconColor: "text-red-500"
    },
    {
      title: "Overall Compliance",
      value: `${data.compliance_score}%`,
      icon: CheckCircle,
      desc: `NABH Standard Compliance: ${data.nabh_compliance}%`,
      color: "from-emerald-500/10 to-teal-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400",
      iconColor: "text-emerald-500"
    },
    {
      title: "Pending / Failed Audits",
      value: `${data.pending_audits} / ${data.failed_audits}`,
      icon: FileText,
      desc: `Total logs: ${data.total_audits} records`,
      color: "from-blue-500/10 to-indigo-500/10 border-blue-500/20 text-blue-600 dark:text-blue-400",
      iconColor: "text-blue-500"
    },
    {
      title: "Active Escalations",
      value: data.open_escalations,
      icon: ShieldAlert,
      desc: `Critical Escalations: ${data.critical_issues}`,
      color: "from-violet-500/10 to-purple-500/10 border-violet-500/20 text-violet-600 dark:text-violet-400",
      iconColor: "text-violet-500"
    }
  ];

  // 11 AI Predictive Metrics Cards
  const aiCards = [
    {
      title: "Predicted Risk Score",
      value: `${data.predicted_risk_score}/100`,
      icon: Cpu,
      desc: "ML-computed average risk",
      color: "border-purple-500/20 bg-purple-500/5 text-purple-600 dark:text-purple-400",
      iconColor: "text-purple-500"
    },
    {
      title: "Predicted Compliance",
      value: `${data.predicted_compliance_score}%`,
      icon: TrendingUp,
      desc: "ML-computed average compliance",
      color: "border-cyan-500/20 bg-cyan-500/5 text-cyan-600 dark:text-cyan-400",
      iconColor: "text-cyan-500"
    },
    {
      title: "Highest Risk Location",
      value: data.highest_risk_location || "N/A",
      icon: ShieldAlert,
      desc: "Location with highest average risk",
      color: "border-red-500/20 bg-red-500/5 text-red-600 dark:text-red-400",
      iconColor: "text-red-500"
    },
    {
      title: "Lowest Compliance Loc",
      value: data.lowest_compliance_location || "N/A",
      icon: AlertTriangle,
      desc: "Location with lowest compliance",
      color: "border-orange-500/20 bg-orange-500/5 text-orange-600 dark:text-orange-400",
      iconColor: "text-orange-500"
    },
    {
      title: "Most Failed Checklist",
      value: data.most_failed_checklist || "N/A",
      icon: FileText,
      desc: "Checklist with most failed audits",
      color: "border-amber-500/20 bg-amber-500/5 text-amber-600 dark:text-amber-400",
      iconColor: "text-amber-500"
    },
    {
      title: "Top Performing User",
      value: data.top_performing_user || "N/A",
      icon: Award,
      desc: "User with highest audit pass rate",
      color: "border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400",
      iconColor: "text-emerald-500"
    },
    {
      title: "Most Pending Audits",
      value: data.most_pending_audits || "N/A",
      icon: Clock,
      desc: "User with most pending audits",
      color: "border-blue-500/20 bg-blue-500/5 text-blue-600 dark:text-blue-400",
      iconColor: "text-blue-500"
    },
    {
      title: "Most Failed Audits",
      value: data.most_failed_audits || "N/A",
      icon: AlertTriangle,
      desc: "User with most failed audits",
      color: "border-rose-500/20 bg-rose-500/5 text-rose-600 dark:text-rose-400",
      iconColor: "text-rose-500"
    },
    {
      title: "Daily Risk Trend",
      value: data.daily_trend || "Stable",
      icon: BarChart2,
      desc: "Day-over-day risk delta",
      color: "border-slate-500/20 bg-slate-500/5 text-slate-600 dark:text-slate-400",
      iconColor: "text-slate-500"
    },
    {
      title: "Weekly Risk Trend",
      value: data.weekly_trend || "Stable",
      icon: TrendingUp,
      desc: "Week-over-week risk delta",
      color: "border-teal-500/20 bg-teal-500/5 text-teal-600 dark:text-teal-400",
      iconColor: "text-teal-500"
    },
    {
      title: "Monthly Risk Trend",
      value: data.monthly_trend || "Stable",
      icon: Calendar,
      desc: "Month-over-month risk delta",
      color: "border-indigo-500/20 bg-indigo-500/5 text-indigo-600 dark:text-indigo-400",
      iconColor: "text-indigo-500"
    }
  ];

  return (
    <div className="space-y-10 animate-fade-in pb-16">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 glass p-6 rounded-2xl border border-white/20 dark:border-white/5">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight flex items-center gap-2">
            <Activity className="h-8 w-8 text-hospital-500 animate-pulse" />
            Hospital Audit Command Center
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Reallist AI Quality & Compliance Assistant (Sentence Transformers, XGBoost & Qwen RAG)
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Retrain Model Button */}
          <button
            onClick={handleRetrain}
            disabled={isRetraining}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 disabled:from-slate-400 disabled:to-slate-500 transition-all font-semibold rounded-xl text-sm shadow-md hover:shadow-purple-500/20"
          >
            <Cpu className={`h-4.5 w-4.5 ${isRetraining ? 'animate-spin' : ''}`} />
            {isRetraining ? "Retraining Models..." : "Retrain AI Models"}
          </button>

          <button 
            onClick={onRefresh}
            className="flex items-center gap-2 px-5 py-2.5 bg-hospital-600 text-white hover:bg-hospital-700 transition-all font-semibold rounded-xl text-sm shadow-md hover:shadow-hospital-500/25"
          >
            <RefreshCw className="h-4.5 w-4.5" />
            Refresh Logs
          </button>
        </div>
      </div>

      {/* Retrain Status Toast Banner */}
      {retrainStatus && (
        <div className="p-4 rounded-xl border border-purple-500/25 bg-purple-500/10 text-purple-700 dark:text-purple-300 font-semibold text-sm text-center flex items-center justify-center gap-2 animate-pulse">
          <Sparkles className="h-5 w-5 text-purple-500 animate-spin-slow" />
          {retrainStatus}
        </div>
      )}

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {primaryCards.map((card, idx) => (
          <div 
            key={idx}
            className={`glass border p-5 rounded-2xl flex flex-col justify-between hover:scale-[1.02] transition-all duration-300 shadow-sm ${card.color}`}
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-semibold text-slate-500 dark:text-slate-400 tracking-wide uppercase">
                  {card.title}
                </p>
                <h3 className="text-3xl font-bold text-slate-800 dark:text-white mt-2">
                  {card.value}
                </h3>
              </div>
              <div className={`p-2.5 rounded-xl bg-white/50 dark:bg-slate-800/50 border border-slate-200/20 shadow-inner ${card.iconColor}`}>
                <card.icon className="h-6 w-6" />
              </div>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-4 flex items-center gap-1 font-medium">
              <ArrowUpRight className="h-3.5 w-3.5" />
              {card.desc}
            </p>
          </div>
        ))}
      </div>

      {/* AI OPERATIONS SECTION */}
      <div className="space-y-6">
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
          <Cpu className="h-6 w-6 text-purple-500" />
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">AI Predictive Operations Metrics</h2>
        </div>

        {/* 11 AI Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {aiCards.map((card, idx) => (
            <div 
              key={idx}
              className={`glass border p-4.5 rounded-xl flex flex-col justify-between hover:shadow-md transition-all duration-200 ${card.color}`}
            >
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase block">
                    {card.title}
                  </span>
                  <div className="text-lg font-extrabold text-slate-800 dark:text-white truncate max-w-[220px]">
                    {card.value}
                  </div>
                </div>
                <div className={`p-1.5 rounded-lg bg-white/40 dark:bg-slate-800/40 border border-slate-200/10 ${card.iconColor}`}>
                  <card.icon className="h-4.5 w-4.5" />
                </div>
              </div>
              <span className="text-[10px] text-slate-400 mt-2 block font-medium">
                {card.desc}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Visualizations Section */}
      <div className="space-y-6">
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
          <BarChart2 className="h-6 w-6 text-hospital-500" />
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">AI Visualizations & Distribution Charts</h2>
        </div>

        {/* First Row of Charts (Trends) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Risk Trend Chart */}
          <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
            <h3 className="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
              <Activity className="h-5 w-5 text-red-500" />
              AI Predicted Risk Trend (Quartiles & Mean)
            </h3>
            <div className="h-64 w-full flex-grow">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data.charts?.risk_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis dataKey="date" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis domain={[0, 100]} stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', color: '#fff', borderRadius: '8px', border: 'none' }} />
                  <Legend iconType="rect" wrapperStyle={{ fontSize: '11px', marginTop: '10px' }} />
                  <Area type="monotone" dataKey="range" name="Quartile Range (Q1-Q3)" fill="#ef4444" stroke="none" fillOpacity={0.15} />
                  <Line type="monotone" dataKey="mean" name="Average Risk" stroke="#b91c1c" strokeWidth={2.5} dot={false} />
                  <Line type="monotone" dataKey="median" name="Median Risk" stroke="#f87171" strokeDasharray="3 3" strokeWidth={1.5} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Compliance Trend Chart */}
          <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
            <h3 className="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
              <CheckCircle className="h-5 w-5 text-emerald-500" />
              AI Predicted Compliance Trend (Quartiles & Mean)
            </h3>
            <div className="h-64 w-full flex-grow">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data.charts?.compliance_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis dataKey="date" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis domain={[0, 100]} stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', color: '#fff', borderRadius: '8px', border: 'none' }} />
                  <Legend iconType="rect" wrapperStyle={{ fontSize: '11px', marginTop: '10px' }} />
                  <Area type="monotone" dataKey="range" name="Quartile Range (Q1-Q3)" fill="#10b981" stroke="none" fillOpacity={0.15} />
                  <Line type="monotone" dataKey="mean" name="Average Compliance" stroke="#047857" strokeWidth={2.5} dot={false} />
                  <Line type="monotone" dataKey="median" name="Median Compliance" stroke="#34d399" strokeDasharray="3 3" strokeWidth={1.5} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Second Row of Charts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Status Distribution */}
          <div className="glass p-5 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
            <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4">Status Distribution</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.charts?.status_distribution || []} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis dataKey="status" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', color: '#fff', border: 'none', borderRadius: '6px' }} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Checklist Distribution */}
          <div className="glass p-5 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
            <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4">Top 5 Checklist Volumes</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.charts?.checklist_distribution?.slice(0, 5) || []} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis dataKey="name" stroke="#94A3B8" fontSize={8} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', color: '#fff', border: 'none', borderRadius: '6px' }} />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Location Distribution */}
          <div className="glass p-5 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
            <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4">Location Audit Distribution</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.charts?.location_distribution || []} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis dataKey="city" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', color: '#fff', border: 'none', borderRadius: '6px' }} />
                  <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Third Row of Charts */}
        <div className="grid grid-cols-1 gap-8">
          {/* Monthly Audits counts */}
          <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
            <h3 className="text-base font-bold text-slate-800 dark:text-white mb-4">Audit Volumes per Month</h3>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.charts?.monthly_audits || []} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                  <XAxis dataKey="month" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', color: '#fff', border: 'none', borderRadius: '6px' }} />
                  <Bar dataKey="count" name="Audits Count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations, Staff and Checklists grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Dynamic AI Recommendations */}
        <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col h-full col-span-1 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-amber-500 animate-spin-slow" />
              Dynamic Audit Recommendations
            </h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded">
              Rule Engine
            </span>
          </div>
          <div className="space-y-4 flex-grow overflow-y-auto max-h-80 pr-1">
            {data.recommendations?.map((rec, index) => (
              <div 
                key={index}
                className="p-4 rounded-xl border border-slate-200/50 dark:border-slate-800/50 bg-slate-50/50 dark:bg-slate-900/40 flex gap-3.5 items-start hover:shadow-md transition-all duration-200"
              >
                <div className={`p-2 rounded-lg mt-0.5 shrink-0 ${
                  rec.type === 'risk' ? 'bg-red-500/10 text-red-500 border border-red-500/20' :
                  rec.type === 'compliance' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' :
                  rec.type === 'escalation' ? 'bg-indigo-500/10 text-indigo-500 border border-indigo-500/20' :
                  'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                }`}>
                  <Clock className="h-4.5 w-4.5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300">
                    {rec.target} Focus Action
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                    {rec.recommendation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Staff & Leaderboard */}
        <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col h-full">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <Award className="h-5 w-5 text-emerald-500" />
              Top Staff Performance
            </h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded">
              Leaderboard
            </span>
          </div>
          <div className="space-y-3 flex-grow overflow-y-auto max-h-80 pr-1">
            {data.top_staff?.map((staff, idx) => (
              <div 
                key={idx}
                className="flex items-center justify-between p-3 rounded-xl border border-slate-200/50 dark:border-slate-800/40 bg-slate-50/20 dark:bg-slate-900/10 hover:bg-slate-100/30 transition-all duration-150"
              >
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-hospital-100 dark:bg-hospital-950/50 text-hospital-700 dark:text-hospital-300 font-bold text-xs flex items-center justify-center border border-hospital-200/25">
                    {idx + 1}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-800 dark:text-white">{staff.staff}</h4>
                    <p className="text-[10px] text-slate-400 font-medium">Audits: {staff.audits}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-emerald-500 block">{staff.pass_rate}% Pass</span>
                  <span className="text-[10px] text-slate-400 font-semibold block">Compliance: {staff.compliance}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Checklist Completion details */}
      <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5">
        <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
          <FileText className="h-5 w-5 text-hospital-500" />
          Checklist Performance Matrix
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {data.charts?.checklist?.map((item, idx) => (
            <div 
              key={idx}
              className="p-5 rounded-2xl border border-slate-200/40 dark:border-slate-800/50 bg-slate-50/20 dark:bg-slate-900/10 flex flex-col justify-between"
            >
              <div>
                <span className="text-xs font-bold text-hospital-600 dark:text-hospital-400 block tracking-wide uppercase">
                  {item.name}
                </span>
                <div className="flex items-baseline gap-2 mt-2">
                  <h4 className="text-2xl font-extrabold text-slate-800 dark:text-white">
                    {item.compliance}%
                  </h4>
                  <span className="text-xs text-slate-400 font-semibold">Avg Compliance</span>
                </div>
              </div>
              <div className="mt-5 space-y-2">
                <div className="flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span>Passed</span>
                  <span className="font-bold text-emerald-500">{item.passed}</span>
                </div>
                <div className="flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span>Failed</span>
                  <span className="font-bold text-red-500">{item.failed}</span>
                </div>
                <div className="flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span>Pending</span>
                  <span className="font-bold text-amber-500">{item.pending}</span>
                </div>
                {/* Visual mini progress bar */}
                <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-3">
                  <div 
                    className="bg-hospital-500 h-full rounded-full" 
                    style={{ width: `${(item.passed / item.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
