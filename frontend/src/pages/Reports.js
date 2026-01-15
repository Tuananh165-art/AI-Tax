import React, { useEffect, useState } from 'react';
import { reportAPI } from '../api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { FaChartBar, FaFileInvoice, FaMoneyBill, FaChartLine, FaPercentage } from 'react-icons/fa';

function Reports() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    reportAPI.getSummary().then(res => setSummary(res.data)).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2 text-white">
          <FaChartBar className="text-purple-400" /> Báo Cáo Tổng Hợp
        </h2>
        <p className="text-slate-400">Thống kê tài chính và phân tích kinh doanh</p>
      </div>
      
      {summary ? (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="bg-slate-800/50 border-slate-700/50 hover:shadow-xl hover:shadow-cyan-500/10 transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-300">Số hóa đơn</CardTitle>
                <div className="p-2 rounded-lg bg-cyan-500/10">
                  <FaFileInvoice className="h-4 w-4 text-cyan-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white">{summary.total_invoices}</div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800/50 border-slate-700/50 hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-300">Số chi phí</CardTitle>
                <div className="p-2 rounded-lg bg-emerald-500/10">
                  <FaMoneyBill className="h-4 w-4 text-emerald-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white">{summary.total_expenses}</div>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-slate-800/50 border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <FaChartLine /> Tài chính
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-lg border border-slate-600/30">
                  <span className="text-slate-300 font-medium">Doanh thu</span>
                  <span className="text-2xl font-bold text-cyan-400">
                    {summary.revenue.toLocaleString()} VNĐ
                  </span>
                </div>
                <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-lg border border-slate-600/30">
                  <span className="text-slate-300 font-medium">Chi phí</span>
                  <span className="text-2xl font-bold text-orange-400">
                    {summary.expenses.toLocaleString()} VNĐ
                  </span>
                </div>
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 rounded-lg border-2 border-emerald-500/30">
                  <span className="text-white font-bold text-lg">Lợi nhuận</span>
                  <span className={`text-3xl font-bold ${
                    summary.profit >= 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {summary.profit.toLocaleString()} VNĐ
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <FaPercentage /> Phân tích
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Tỷ lệ lợi nhuận</span>
                    <span className="font-semibold text-emerald-400">
                      {summary.revenue > 0 ? ((summary.profit / summary.revenue) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-2 rounded-full transition-all duration-500"
                      style={{width: `${summary.revenue > 0 ? Math.min(((summary.profit / summary.revenue) * 100), 100) : 0}%`}}
                    ></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Tỷ lệ chi phí</span>
                    <span className="font-semibold text-orange-400">
                      {summary.revenue > 0 ? ((summary.expenses / summary.revenue) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-500"
                      style={{width: `${summary.revenue > 0 ? Math.min(((summary.expenses / summary.revenue) * 100), 100) : 0}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card className="p-12 bg-slate-800/30 border-slate-700/30">
          <div className="text-center text-slate-400">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
            <p>Đang tải dữ liệu...</p>
          </div>
        </Card>
      )}
    </div>
  );
}

export default Reports;
