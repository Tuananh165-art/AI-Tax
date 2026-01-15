import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const invoiceAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/invoices/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getAll: () => api.get('/api/invoices'),
  getById: (id) => api.get(`/api/invoices/${id}`)
};

export const expenseAPI = {
  create: (data) => api.post(`/api/expenses?description=${data.description}&amount=${data.amount}&date=${data.date}`),
  getAll: () => api.get('/api/expenses')
};

export const taxAPI = {
  calculate: (data) => api.post('/api/tax/calculate', data)
};

export const reportAPI = {
  getSummary: () => api.get('/api/reports/summary')
};

export const chatbotAPI = {
  ask: (question) => api.post('/api/chatbot/ask', { question }),
  getAdvice: (data) => api.post('/api/chatbot/advice', data)
};

export default api;
