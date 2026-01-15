import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { FaHome, FaFileInvoice, FaMoneyBill, FaCalculator, FaChartBar, FaComments, FaSignOutAlt } from 'react-icons/fa';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Home from './pages/Home';
import Invoices from './pages/Invoices';
import Expenses from './pages/Expenses';
import TaxCalculator from './pages/TaxCalculator';
import Reports from './pages/Reports';
import Chatbot from './pages/Chatbot';
import Login from './pages/Login';
import { cn } from './lib/utils';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID";

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      to={to}
      className={cn(
        "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200",
        isActive
          ? "bg-primary text-primary-foreground shadow-md"
          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      )}
    >
      <Icon className="w-4 h-4" />
      <span className="font-medium">{children}</span>
    </Link>
  );
}

function AppContent() {
  const { user, logout } = useAuth();
  const location = useLocation();

  if (location.pathname === '/login') {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
      </Routes>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-lg border-b border-slate-700/50 shadow-lg shadow-cyan-500/5">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="text-3xl">🧾</div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                AI Tax Assistant
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <NavLink to="/" icon={FaHome}>Trang chủ</NavLink>
                <NavLink to="/invoices" icon={FaFileInvoice}>Hóa đơn</NavLink>
                <NavLink to="/expenses" icon={FaMoneyBill}>Chi phí</NavLink>
                <NavLink to="/tax" icon={FaCalculator}>Tính thuế</NavLink>
                <NavLink to="/reports" icon={FaChartBar}>Báo cáo</NavLink>
                <NavLink to="/chatbot" icon={FaComments}>Chatbot</NavLink>
              </div>
              {user && (
                <div className="flex items-center gap-3 pl-4 border-l border-slate-700">
                  <span className="text-sm text-slate-300">{user.name}</span>
                  <button
                    onClick={logout}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:bg-red-500/10 hover:text-red-400 transition-all"
                  >
                    <FaSignOutAlt className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-8 animate-fade-in">
        <Routes>
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/invoices" element={<ProtectedRoute><Invoices /></ProtectedRoute>} />
          <Route path="/expenses" element={<ProtectedRoute><Expenses /></ProtectedRoute>} />
          <Route path="/tax" element={<ProtectedRoute><TaxCalculator /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
          <Route path="/chatbot" element={<ProtectedRoute><Chatbot /></ProtectedRoute>} />
        </Routes>
      </main>
      
      <footer className="mt-auto border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <p className="text-center text-sm text-slate-400">
            ⚠️ Thông tin mang tính tham khảo. Vui lòng kiểm tra với cơ quan thuế.
          </p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
