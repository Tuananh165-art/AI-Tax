import React, { useState, useEffect } from 'react';
import { invoiceAPI } from '../api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FaFileInvoice, FaUpload, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

function Invoices() {
  const [file, setFile] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = () => {
    invoiceAPI.getAll().then(res => setInvoices(res.data)).catch(console.error);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return setMessage('Chọn file trước!');
    
    setLoading(true);
    try {
      await invoiceAPI.upload(file);
      setMessage('Upload thành công!');
      setFile(null);
      loadInvoices();
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
          <FaFileInvoice className="text-cyan-400" /> Quản Lý Hóa Đơn
        </h2>
        <p className="text-slate-400">Upload và quản lý hóa đơn của bạn</p>
      </div>
      
      <Card className="bg-slate-800/50 border-slate-700/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <FaUpload /> Upload Hóa Đơn
          </CardTitle>
          <CardDescription className="text-slate-400">Chọn file hóa đơn để tự động nhận diện thông tin</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Chọn file ảnh</label>
              <input 
                type="file" 
                accept="image/*" 
                onChange={(e) => setFile(e.target.files[0])} 
                className="flex h-10 w-full rounded-md border border-slate-600 bg-slate-700/50 px-3 py-2 text-sm text-slate-300 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-cyan-400 hover:file:text-cyan-300"
              />
            </div>
            <Button type="submit" disabled={loading || !file} className="w-full" size="lg">
              {loading ? 'Đang xử lý...' : 'Upload & OCR'}
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
        <h3 className="text-xl font-semibold text-white">Danh sách hóa đơn</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {invoices.map(inv => (
            <Card key={inv.id} className="bg-slate-800/50 border-slate-700/50 hover:shadow-xl hover:shadow-cyan-500/10 transition-all duration-300">
              <CardHeader>
                <CardTitle className="text-lg text-white">
                  {inv.invoice_number || 'Chưa có số HĐ'}
                </CardTitle>
                <CardDescription className="text-slate-400">{inv.seller_name || 'N/A'}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Ngày:</span>
                  <span className="font-medium text-slate-300">{inv.date}</span>
                </div>
                {inv.subtotal > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Tổng tiền hàng:</span>
                    <span className="font-medium text-slate-300">
                      {typeof inv.subtotal === 'number' 
                        ? inv.subtotal.toLocaleString('vi-VN') 
                        : '0'} VNĐ
                    </span>
                  </div>
                )}
                {inv.vat > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">VAT:</span>
                    <span className="font-medium text-slate-300">
                      {typeof inv.vat === 'number' 
                        ? inv.vat.toLocaleString('vi-VN') 
                        : '0'} VNĐ
                    </span>
                  </div>
                )}
                <div className="flex justify-between border-t border-slate-700 pt-2 mt-2">
                  <span className="text-slate-400 font-semibold">Tổng cộng:</span>
                  <span className="font-bold text-cyan-400">
                    {typeof inv.total === 'number' && inv.total > 0 
                      ? inv.total.toLocaleString('vi-VN') 
                      : '0'} VNĐ
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        {invoices.length === 0 && (
          <Card className="p-12 bg-slate-800/30 border-slate-700/30">
            <div className="text-center text-slate-400">
              <FaFileInvoice className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p>Chưa có hóa đơn nào. Hãy upload hóa đơn đầu tiên!</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

export default Invoices;
