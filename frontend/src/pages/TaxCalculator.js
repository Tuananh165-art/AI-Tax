import React, { useState } from 'react';
import { taxAPI } from '../api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { FaCalculator, FaMoneyBillWave, FaReceipt, FaExclamationTriangle } from 'react-icons/fa';

function TaxCalculator() {
  const [form, setForm] = useState({ revenue: '', expenses: '', business_type: 'food_service' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await taxAPI.calculate({
        revenue: parseFloat(form.revenue),
        expenses: parseFloat(form.expenses),
        business_type: form.business_type
      });
      setResult(res.data);
    } catch (error) {
      alert('Lỗi: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="space-y-2">
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2 text-white">
          <FaCalculator className="text-purple-400" /> Tính Thuế
        </h2>
        <p className="text-slate-400">Ước tính thuế phải nộp dựa trên doanh thu và chi phí</p>
      </div>
      
      <Card className="bg-slate-800/50 border-slate-700/50">
        <CardHeader>
          <CardTitle className="text-white">Thông tin kinh doanh</CardTitle>
          <CardDescription className="text-slate-400">Nhập thông tin để tính toán thuế</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Doanh thu (VNĐ)</label>
              <Input 
                type="number" 
                value={form.revenue} 
                onChange={(e) => setForm({...form, revenue: e.target.value})} 
                placeholder="200000000" 
                required 
                className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Chi phí (VNĐ)</label>
              <Input 
                type="number" 
                value={form.expenses} 
                onChange={(e) => setForm({...form, expenses: e.target.value})} 
                placeholder="150000000" 
                required 
                className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Loại hình kinh doanh</label>
              <select 
                value={form.business_type} 
                onChange={(e) => setForm({...form, business_type: e.target.value})}
                className="flex h-10 w-full rounded-md border border-slate-600 bg-slate-700/50 px-3 py-2 text-sm text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
              >
                <option value="food_service">Dịch vụ ăn uống</option>
                <option value="retail">Bán lẻ</option>
                <option value="service">Dịch vụ</option>
              </select>
            </div>
            <Button type="submit" disabled={loading} className="w-full" size="lg">
              {loading ? 'Đang tính...' : 'Tính Thuế'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card className="border-emerald-500/30 bg-slate-800/50 animate-fade-in">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <FaMoneyBillWave className="text-emerald-400" /> Kết quả tính thuế
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-700/30 rounded-lg border border-slate-600/30">
                <p className="text-sm text-slate-400">Doanh thu</p>
                <p className="text-2xl font-bold text-cyan-400">{result.estimated_revenue.toLocaleString()} VNĐ</p>
              </div>
              <div className="p-4 bg-slate-700/30 rounded-lg border border-slate-600/30">
                <p className="text-sm text-slate-400">Chi phí</p>
                <p className="text-2xl font-bold text-orange-400">{result.estimated_expenses.toLocaleString()} VNĐ</p>
              </div>
            </div>
            
            <div className="border-t border-slate-700 pt-4">
              <h4 className="font-semibold mb-3 flex items-center gap-2 text-white">
                <FaReceipt /> Thuế phải nộp:
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between p-2 bg-slate-700/30 rounded">
                  <span className="text-slate-300">VAT</span>
                  <span className="font-semibold text-slate-100">{result.estimated_tax.vat.toLocaleString()} VNĐ</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-700/30 rounded">
                  <span className="text-slate-300">TNCN</span>
                  <span className="font-semibold text-slate-100">{result.estimated_tax.pit.toLocaleString()} VNĐ</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-700/30 rounded">
                  <span className="text-slate-300">Lệ phí</span>
                  <span className="font-semibold text-slate-100">{result.estimated_tax.license_fee.toLocaleString()} VNĐ</span>
                </div>
                <div className="flex justify-between p-3 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-lg font-bold text-lg border border-cyan-500/30">
                  <span className="text-white">Tổng</span>
                  <span className="text-cyan-400">{result.estimated_tax.total.toLocaleString()} VNĐ</span>
                </div>
              </div>
            </div>
            
            {result.notes.length > 0 && (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 space-y-2">
                <div className="flex items-center gap-2 font-semibold text-yellow-400">
                  <FaExclamationTriangle /> Lưu ý
                </div>
                {result.notes.map((note, i) => (
                  <p key={i} className="text-sm text-yellow-300">• {note}</p>
                ))}
              </div>
            )}
            
            <p className="text-xs text-slate-400">{result.disclaimer}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default TaxCalculator;
