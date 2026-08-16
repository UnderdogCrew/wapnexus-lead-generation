import React, { useEffect, useState } from "react";
import LeadDashboard from "./LeadDashboard.jsx";
import Login from "./Login.jsx";
import { TOKEN_KEY, login as apiLogin } from "./api";

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");

  useEffect(() => {
    const onLogout = () => setToken("");
    window.addEventListener("auth:logout", onLogout);
    return () => window.removeEventListener("auth:logout", onLogout);
  }, []);

  const handleLogin = async (username, password) => {
    const data = await apiLogin(username, password);
    localStorage.setItem(TOKEN_KEY, data.token);
    setToken(data.token);
  };

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken("");
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return <LeadDashboard onLogout={handleLogout} />;
}
