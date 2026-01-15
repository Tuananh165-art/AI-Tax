import React, { useState, useEffect } from 'react';
import { expenseAPI } from '../api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { FaMoneyBill, FaPlus, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState({ description: '', amount: '', date: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadExpenses();
  }, []);

  const loadExpenses = () => {
    expenseAPI.getAll().then(res => setExpenses(res.data)).catch(console.error);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await expenseAPI.create(form);
      setMessage('Thêm chi phí thành công!');
      setForm({ description: '', amount: '', date: '' });
      loadExpenses();
    } catch (error) {
      setMessage('Lỗi: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2 text-white">
          <FaMoneyBill className="text-emerald-400" /> Quản Lý Chi Phí
        </h2>
        <p className="text-slate-400">Thêm và quản lý các khoản chi phí kinh doanh</p>
      </div>
      
      <Card className="bg-slate-800/50 border-slate-700/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <FaPlus /> Thêm Chi Phí Mới
          </CardTitle>
          <CardDescription className="text-slate-400">Nhập thông tin chi phí của bạn</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Mô tả</label>
              <Input 
                type="text" 
                value={form.description} 
                onChange={(e) => setForm({...form, description: e.target.value})} 
                placeholder="Mua thực phẩm" 
                required 
                className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400"
              />
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Số tiền (VNĐ)</label>
                <Input 
                  type="number" 
                  value={form.amount} 
                  onChange={(e) => setForm({...form, amount: e.target.value})} 
                  placeholder="50000" 
                  required 
                  className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Ngày</label>
                <Input 
                  type="date" 
                  value={form.date} 
                  onChange={(e) => setForm({...form, date: e.target.value})} 
                  required 
                  className="bg-slate-700/50 border-slate-600 text-white"
                />
              </div>
            </div>
            <Button type="submit" disabled={loading} className="w-full" size="lg">
              {loading ? 'Đang xử lý...' : 'Thêm Chi Phí'}
            </Button>
          </form>
          
          {message && (
            <div className={`mt-4 p-4 rounded-lg flex items-center gap-2 ${
              message.includes('thành công') 
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                : 'bg-red-500/10 text-red-400 border border-red-500/20'
            }`}>
              {message.includes('thành công') ? <FaCheckCircle /> : <FaTimesCircle />}
              {message}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-white">Danh sách chi phí</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {expenses.map(exp => (
            <Card key={exp.id} className="bg-slate-800/50 border-slate-700/50 hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-300">
              <CardHeader>
                <CardTitle className="text-lg text-white">{exp.description}</CardTitle>
                <CardDescription className="text-slate-400">{exp.category}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Số tiền:</span>
                  <span className="font-bold text-emerald-400">{exp.amount.toLocaleString()} VNĐ</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Ngày:</span>
                  <span className="text-slate-300">{exp.date}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Khấu trừ:</span>
                  <span className={exp.is_deductible ? 'text-emerald-400' : 'text-red-400'}>
                    {exp.is_deductible ? '✅ Có' : '❌ Không'}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        {expenses.length === 0 && (
          <Card className="p-12 bg-slate-800/30 border-slate-700/30">
            <div className="text-center text-slate-400">
              <FaMoneyBill className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p>Chưa có chi phí nào. Hãy thêm chi phí đầu tiên!</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

export default Expenses;
