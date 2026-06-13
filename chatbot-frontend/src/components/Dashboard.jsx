import React from "react";
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
  Clock
} from "lucide-react";
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from "recharts";

export default function Dashboard({ data, loading, onRefresh }) {
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

  // Formatting metrics
  const cardData = [
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

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 glass p-6 rounded-2xl border border-white/20 dark:border-white/5">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight flex items-center gap-2">
            <Activity className="h-8 w-8 text-hospital-500 animate-pulse" />
            Hospital Audit Command Center
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Reallist Quality & Compliance Intelligence Dashboard (Dynamic CSV Analysis)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={onRefresh}
            className="flex items-center gap-2 px-5 py-2.5 bg-hospital-600 text-white hover:bg-hospital-700 transition-all font-semibold rounded-xl text-sm shadow-md hover:shadow-hospital-500/25"
          >
            Refresh Logs
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cardData.map((card, idx) => (
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

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Monthly Trend Area Chart */}
        <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-hospital-500" />
              Monthly Compliance & Risk Trends
            </h3>
            <span className="text-xs px-2.5 py-1 bg-hospital-500/10 text-hospital-600 dark:text-hospital-400 font-semibold rounded-full">
              Time Series Forecast Enabled
            </span>
          </div>
          <div className="h-72 w-full flex-grow">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.charts?.monthly || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCompliance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                    borderColor: '#cbd5e1', 
                    borderRadius: '8px', 
                    color: '#1e293b' 
                  }}
                  itemStyle={{ fontSize: '13px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', marginTop: '10px' }} />
                <Area 
                  type="monotone" 
                  dataKey="compliance" 
                  name="Compliance %" 
                  stroke="#10b981" 
                  fillOpacity={1} 
                  fill="url(#colorCompliance)" 
                  strokeWidth={2}
                />
                <Area 
                  type="monotone" 
                  dataKey="risk" 
                  name="Risk Level" 
                  stroke="#ef4444" 
                  fillOpacity={1} 
                  fill="url(#colorRisk)" 
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Floor-wise Risk & Compliance Bar Chart */}
        <div className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <Layers className="h-5 w-5 text-hospital-500" />
              Risk vs Compliance by Floor
            </h3>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Floor {data.high_risk_floor} has highest risk
            </span>
          </div>
          <div className="h-72 w-full flex-grow">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.charts?.floor || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                <XAxis dataKey="floor" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                    borderColor: '#cbd5e1', 
                    borderRadius: '8px', 
                    color: '#1e293b' 
                  }}
                  itemStyle={{ fontSize: '13px' }}
                />
                <Legend iconType="rect" wrapperStyle={{ fontSize: '12px', marginTop: '10px' }} />
                <Bar dataKey="compliance" name="Avg Compliance %" fill="#0e8ee9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="risk" name="Avg Risk Score" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
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
