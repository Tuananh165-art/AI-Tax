# AI Tax Assistant - Hệ thống hỗ trợ thuế cho HKD

## Tổng quan
Hệ thống AI hỗ trợ hộ kinh doanh cá thể tính thuế, quản lý chi phí và tuân thủ pháp luật Việt Nam.

## Cấu trúc dự án
```
AI-Tax/
├── backend/          # Backend API (FastAPI)
├── frontend/   # Web App (ReactJS)
└── prompt.md        # Tài liệu thiết kế hệ thống
```

## Cài đặt

### Backend

1. Tạo môi trường ảo:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình môi trường:
```bash
copy .env.example .env
# Chỉnh sửa .env với thông tin database của bạn
```

4. Chạy server:
```bash
uvicorn main:app --reload
```

API sẽ chạy tại: http://localhost:8000
API docs: http://localhost:8000/docs

## API Endpoints

### Invoices
- `POST /api/invoices/upload` - Upload và OCR hóa đơn
- `GET /api/invoices` - Lấy danh sách hóa đơn
- `GET /api/invoices/{id}` - Lấy chi tiết hóa đơn

### Expenses
- `POST /api/expenses` - Tạo chi phí mới
- `GET /api/expenses` - Lấy danh sách chi phí

### Tax
- `POST /api/tax/calculate` - Tính thuế ước tính

### Reports
- `GET /api/reports/summary` - Báo cáo tổng hợp

## Tính năng

✅ Upload và OCR hóa đơn (PaddleOCR)
✅ Phân loại chi phí tự động
✅ Tính thuế theo quy định VN
✅ Báo cáo doanh thu - chi phí
✅ Chatbot tư vấn thuế (RAG)
✅ Web App (ReactJS)
✅ Mobile App (React Native)
✅ API RESTful

## Roadmap

### Phase 1 ✅
- [x] Backend API (FastAPI)
- [x] OCR hóa đơn
- [x] Phân loại chi phí
- [x] Tính thuế

### Phase 2 ✅
- [x] Chatbot tư vấn thuế (RAG)
- [x] Knowledge base luật thuế
- [x] Tư vấn cá nhân hóa

### Phase 3 ✅
- [x] Web App (ReactJS)
- [x] Mobile App (React Native)
- [x] Camera integration

### Phase 4 (Future)
- [ ] Multi-user & authentication
- [ ] Xuất báo cáo PDF
- [ ] Tích hợp HĐĐT
- [ ] Offline mode
- [ ] Push notifications

## Lưu ý pháp lý

⚠️ Hệ thống chỉ mang tính tham khảo, không thay thế tư vấn thuế chính thức.
Kết quả phụ thuộc vào quyết định của cơ quan thuế.

## License
MIT


## Chatbot Tư Vấn Thuế (Phase 2)

### Tính năng mới
✅ Hỏi đáp về luật thuế VN
✅ Tư vấn cá nhân hóa theo doanh thu
✅ Knowledge base luật thuế

### Cài đặt Chatbot

```bash
setup-chatbot.bat
```

Hoặc thủ công:
```bash
cd backend
pip install -r requirements-chatbot.txt
python -c "from services.chatbot.chatbot_service import TaxChatbot; bot = TaxChatbot(); bot.create_vector_store()"
```

### API Chatbot

- `POST /api/chatbot/ask` - Hỏi đáp tự do
- `POST /api/chatbot/advice` - Tư vấn cá nhân

### Test Chatbot

```bash
python test_chatbot.py
```

### Ví dụ câu hỏi

- "Doanh thu 200 triệu/năm phải nộp bao nhiêu thuế?"
- "Chi phí nào được khấu trừ?"
- "Khi nào phải dùng hóa đơn điện tử?"
- "Chậm nộp thuế bị phạt thế nào?"

## Frontend (Phase 3)

### 🌐 Web App (ReactJS)

**Cài đặt:**
```bash
setup-react-web.bat
```

Hoặc thủ công:
```bash
cd frontend-react
npm install
npm start
```

App chạy tại: http://localhost:3000

**Lưu ý:** Sửa API_URL trong `api.js` với IP máy tính của bạn.

### Tính năng Frontend

- 📸 Upload/chụp hóa đơn
- 💰 Quản lý chi phí
- 🧮 Tính thuế
- 📊 Báo cáo tài chính
- 💬 Chatbot tư vấn
