import React, { useState } from "react";
import { Loader2, Lock, MessageSquare } from "lucide-react";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password || loading) return;
    setLoading(true);
    setError("");
    try {
      await onLogin(username.trim(), password);
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex min-h-screen w-full items-center justify-center bg-slate-50 px-4 py-12"
      style={{ fontFamily: "'Segoe UI', 'Helvetica Neue', Arial, sans-serif" }}
    >
      <form
        onSubmit={submit}
        className="w-full max-w-sm rounded-2xl border border-slate-100 bg-white p-6 shadow-sm"
      >
        <div className="mb-6 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#11B780]">
            <MessageSquare size={16} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900">WapNexus Lead Pipeline</h1>
            <p className="text-xs text-slate-500">Admin sign-in required</p>
          </div>
        </div>

        <label className="block text-[11px] font-semibold uppercase tracking-wide text-slate-400">
          Username
        </label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          autoFocus
          className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-[#225AD6] focus:outline-none focus:ring-1 focus:ring-[#225AD6]/30"
        />

        <label className="mt-4 block text-[11px] font-semibold uppercase tracking-wide text-slate-400">
          Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-[#225AD6] focus:outline-none focus:ring-1 focus:ring-[#225AD6]/30"
        />

        {error && <p className="mt-3 text-xs text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={!username.trim() || !password || loading}
          className="mt-5 flex w-full items-center justify-center gap-1.5 rounded-md bg-[#225AD6] px-3 py-2 text-sm font-medium text-white hover:bg-[#1b48b0] disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Lock size={14} />}
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}
