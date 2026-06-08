import React, { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard";
import Chatbot from "./components/Chatbot";
import { Sun, Moon, Shield } from "lucide-react";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/api/dashboard");
      if (!res.ok) throw new Error("HTTP error " + res.status);
      const d = await res.json();
      setData(d);
    } catch (e) {
      console.error("Failed to connect to backend:", e);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Sync dark mode class
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-200">
      {/* Navbar */}
      <nav className="sticky top-0 z-40 w-full border-b border-slate-200/50 dark:border-slate-800/60 bg-white/70 dark:bg-slate-900/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-hospital-500 to-hospital-700 flex items-center justify-center text-white shadow-md shadow-hospital-500/10">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <span className="font-extrabold text-lg text-slate-800 dark:text-white tracking-tight">
                Reallist <span className="text-hospital-600 dark:text-hospital-400">Audit</span>
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Status indicator */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200/40 dark:border-slate-800/40 bg-slate-100/20 dark:bg-slate-950/20 text-xs font-semibold">
              <span className={`h-2 w-2 rounded-full ${data ? 'bg-emerald-500' : 'bg-red-500 animate-pulse'}`}></span>
              <span className="text-slate-500 dark:text-slate-400">
                {data ? 'Backend Active' : 'Backend Offline'}
              </span>
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2.5 rounded-xl border border-slate-200/50 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all text-slate-600 dark:text-slate-300"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Dashboard data={data} loading={loading} onRefresh={fetchDashboardData} />
      </main>

      {/* Floating Chatbot Assistant */}
      <Chatbot />
    </div>
  );
}

export default App;
