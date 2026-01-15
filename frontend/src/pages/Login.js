import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { FaGoogle } from 'react-icons/fa';

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await axios.post('http://localhost:8000/api/auth/google', {
        token: credentialResponse.credential
      });

      login(response.data.access_token, response.data.user);
      navigate('/');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Đăng nhập thất bại. Vui lòng thử lại.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <Card className="w-full max-w-md bg-slate-800/50 border-slate-700/50">
        <CardHeader className="text-center space-y-4">
          <div className="text-6xl mx-auto">🧾</div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            AI Tax Assistant
          </CardTitle>
          <CardDescription className="text-slate-400 text-lg">
            Hệ thống hỗ trợ thuế cho hộ kinh doanh
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <p className="text-center text-slate-300">
              Đăng nhập để quản lý thuế, chi phí và hóa đơn của bạn
            </p>
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => alert('Đăng nhập thất bại')}
                useOneTap
                theme="filled_black"
                size="large"
                text="signin_with"
                shape="rectangular"
              />
            </div>
          </div>
          
          <div className="pt-6 border-t border-slate-700">
            <div className="space-y-2 text-sm text-slate-400">
              <p className="flex items-center gap-2">
                ✅ Quản lý hóa đơn & chi phí
              </p>
              <p className="flex items-center gap-2">
                ✅ Tính thuế tự động
              </p>
              <p className="flex items-center gap-2">
                ✅ Chatbot tư vấn thuế AI
              </p>
              <p className="flex items-center gap-2">
                ✅ Báo cáo tài chính
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default Login;
