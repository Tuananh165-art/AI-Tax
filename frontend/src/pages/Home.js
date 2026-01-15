import React, { useEffect, useState } from 'react';
import { reportAPI } from '../api';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { FaFileInvoice, FaMoneyBill, FaChartLine, FaCoins, FaCamera, FaWallet, FaCalculator, FaComments } from 'react-icons/fa';

function Home() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    reportAPI.getSummary().then(res => setSummary(res.data)).catch(console.error);
  }, []);

  const stats = summary ? [
    { icon: FaFileInvoice, label: 'Hóa đơn', value: summary.total_invoices, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
    { icon: FaMoneyBill, label: 'Chi phí', value: summary.total_expenses, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
    { icon: FaChartLine, label: 'Doanh thu', value: `${(summary.revenue / 1000000).toFixed(1)}M`, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
    { icon: FaCoins, label: 'Lợi nhuận', value: `${(summary.profit / 1000000).toFixed(1)}M`, color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20' },
  ] : [];

  const features = [
    { to: '/invoices', icon: FaCamera, title: 'Upload Hóa Đơn', desc: 'Scan và OCR hóa đơn tự động', gradient: 'from-blue-500 to-cyan-500' },
    { to: '/expenses', icon: FaWallet, title: 'Quản Lý Chi Phí', desc: 'Phân loại chi phí tự động', gradient: 'from-green-500 to-emerald-500' },
    { to: '/tax', icon: FaCalculator, title: 'Tính Thuế', desc: 'Ước tính thuế phải nộp', gradient: 'from-purple-500 to-pink-500' },
    { to: '/chatbot', icon: FaComments, title: 'Chatbot Tư Vấn', desc: 'Hỏi đáp về luật thuế', gradient: 'from-orange-500 to-red-500' },
  ];

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Trang chủ</h2>
        <p className="text-muted-foreground">
          Chào mừng đến với AI Tax Assistant - Hệ thống hỗ trợ thuế cho hộ kinh doanh
        </p>
      </div>
      
      {summary && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, idx) => (
            <Card key={idx} className={`overflow-hidden hover:shadow-xl hover:shadow-cyan-500/10 transition-all duration-300 border-2 ${stat.border}`}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-300">{stat.label}</CardTitle>
                <div className={`p-2 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {features.map((feature, idx) => (
          <Link key={idx} to={feature.to} className="group">
            <Card className="h-full transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/20 hover:-translate-y-2 cursor-pointer border-slate-700/50 hover:border-cyan-500/50">
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                <CardDescription className="text-base text-slate-400">{feature.desc}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default Home;
