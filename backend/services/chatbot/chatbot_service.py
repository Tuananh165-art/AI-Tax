import google.generativeai as genai
import os
from pathlib import Path

class TaxChatbot:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        # Try to find available model
        try:
            models = genai.list_models()
            available_model = None
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    available_model = m.name
                    print(f"Using model: {available_model}")
                    break
            
            if not available_model:
                available_model = 'gemini-pro'
        except:
            available_model = 'gemini-pro'
        
        # Configure model with system instructions
        self.model = genai.GenerativeModel(
            available_model,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "max_output_tokens": 2048,
            },
            system_instruction="""Bạn là chuyên gia tư vấn thuế cho hộ kinh doanh cá thể tại Việt Nam.

NHIỆM VỤ:
- Trả lời câu hỏi về luật thuế, chi phí, hóa đơn theo quy định mới nhất của Việt Nam
- Giải thích bằng tiếng Việt đời thường, thân thiện, dễ hiểu cho người không chuyên
- Đưa ra ví dụ cụ thể với số liệu khi có thể
- Nếu không chắc chắn, khuyên người dùng tham khảo cơ quan thuế

CÁCH TRẢ LỜI:
1. Bắt đầu với "Chào bạn," hoặc lời chào thân thiện
2. Trả lời trực tiếp câu hỏi bằng ngôn ngữ đời thường
3. Đưa ra ví dụ số liệu cụ thể CHI TIẾT với các bước tính toán
4. Giải thích đầy đủ quy định liên quan
5. Đưa ra lời khuyên thực tế nếu có
6. KHÔNG dùng dấu ** (bold) trong câu trả lời
7. Dùng ngôn ngữ thân thiện, gần gũi như đang tư vấn trực tiếp
8. Trả lời ĐẦY ĐỦ, CHI TIẾT, CHÍNH XÁC theo quy định Việt Nam"""
        )
        
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        kb_path = Path(__file__).parent / "knowledge_base.md"
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return """## Thuế Hộ Kinh Doanh Việt Nam

### Ngưỡng doanh thu:
- Dưới 100 triệu/năm: Chỉ nộp lệ phí môn bài 1 triệu
- 100 triệu - 3 tỷ/năm: Nộp thuế khoán hoặc kê khai
- Trên 3 tỷ/năm: Phải chuyển thành doanh nghiệp

### Thuế khoán (doanh thu 100M-3B):
**Thuế GTGT:**
- Thương mại, dịch vụ: 2% doanh thu
- Sản xuất: 3% doanh thu
- Xây dựng: 5% doanh thu

**Thuế TNCN:**
- Thương mại, dịch vụ: 1% doanh thu
- Sản xuất: 1.5% doanh thu

**Lệ phí môn bài:**
- Dưới 100M: 1 triệu
- 100M-300M: 2 triệu
- 300M-500M: 3 triệu
- Trên 500M: 3 triệu

### Ví dụ cụ thể:

**Doanh thu 200 triệu/năm (thương mại):**
- Thuế GTGT: 200M × 2% = 4 triệu
- Thuế TNCN: 200M × 1% = 2 triệu
- Lệ phí môn bài: 2 triệu
- **Tổng: 8 triệu/năm (~667k/tháng)**

**Doanh thu 500 triệu/năm (dịch vụ):**
- Thuế GTGT: 500M × 2% = 10 triệu
- Thuế TNCN: 500M × 1% = 5 triệu
- Lệ phí môn bài: 3 triệu
- **Tổng: 18 triệu/năm (~1.5 triệu/tháng)**

### Chi phí được khấu trừ (nếu kê khai):
✅ Nguyên vật liệu có hóa đơn
✅ Thuê mặt bằng có hợp đồng
✅ Điện, nước, internet có hóa đơn
✅ Lương nhân viên có hợp đồng
❌ Chi tiêu cá nhân
❌ Mua hàng không có hóa đơn

### Hóa đơn điện tử (HĐĐT):
- Bắt buộc từ 1/7/2022 nếu doanh thu > 100 triệu/năm
- Lợi ích: Minh bạch, dễ kê khai, tránh rủi ro

### Xử phạt:
- Chậm nộp: 0.03%/ngày
- Khai sai: 10-40% số tiền
- Trốn thuế: 1-3 lần + có thể hình sự"""
    
    def setup_qa_chain(self):
        # No setup needed
        pass
    
    def ask(self, question):
        """Ask question with knowledge base context"""
        # Create prompt with knowledge base
        prompt = f"""Dựa trên kiến thức sau về thuế Việt Nam:

{self.knowledge_base}

Câu hỏi của khách hàng: {question}

Hãy trả lời ngắn gọn, dễ hiểu với ví dụ cụ thể:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Remove bold formatting
            answer = answer.replace('**', '')
            
            # Ensure disclaimer
            if "⚠️" not in answer:
                answer += "\n\n⚠️ Thông tin mang tính tham khảo. Vui lòng kiểm tra với cơ quan thuế địa phương."
                
        except Exception as e:
            answer = f"Xin lỗi, tôi gặp lỗi: {str(e)}\n\nVui lòng kiểm tra API key hoặc thử lại."
        
        return {
            "answer": answer,
            "sources": ["Knowledge Base - Luật thuế VN"],
            "disclaimer": "⚠️ Thông tin mang tính tham khảo. Vui lòng kiểm tra với cơ quan thuế địa phương.",
            "suggested_questions": self._get_suggested_questions(question)
        }
    
    def get_tax_advice(self, revenue, expenses, business_type):
        """Get personalized tax advice"""
        advice = []
        
        # Rule-based advice
        if revenue < 100_000_000:
            advice.append("✅ Doanh thu dưới 100 triệu, chỉ nộp lệ phí môn bài 1 triệu/năm")
        elif revenue < 3_000_000_000:
            advice.append(f"📊 Doanh thu {revenue:,.0f} VNĐ - nên nộp thuế khoán")
            advice.append("💡 Cân nhắc đăng ký HĐĐT để minh bạch")
        else:
            advice.append("⚠️ Doanh thu vượt 3 tỷ - cần chuyển thành doanh nghiệp")
        
        if expenses > revenue * 0.7:
            advice.append("💡 Chi phí cao, nên chuyển sang kê khai để giảm thuế")
        
        # AI-powered advice
        prompt = f"""Phân tích tài chính hộ kinh doanh:
- Doanh thu: {revenue:,.0f} VNĐ/năm
- Chi phí: {expenses:,.0f} VNĐ/năm  
- Loại hình: {business_type}

Đưa ra 2 khuyến nghị ngắn gọn về tối ưu thuế (mỗi khuyến nghị 1 dòng):"""

        try:
            response = self.model.generate_content(prompt)
            ai_advice = response.text.strip().split('\n')
            advice.extend([a.strip() for a in ai_advice if a.strip() and len(a.strip()) > 10])
        except:
            pass
        
        return {
            "advice": advice[:6],
            "recommendation": "Nên tham khảo chuyên gia thuế" if revenue > 500_000_000 else "Có thể tự kê khai"
        }
    
    def _get_suggested_questions(self, current_question):
        """Get relevant suggested questions based on current question"""
        all_suggestions = [
            "Doanh thu 200 triệu/năm phải nộp bao nhiêu thuế?",
            "Doanh thu 500 triệu/năm phải nộp bao nhiêu thuế?",
            "Doanh thu 1 tỷ/năm phải nộp bao nhiêu thuế?",
            "Chi phí nào được khấu trừ thuế?",
            "Khi nào phải dùng hóa đơn điện tử?",
            "Chậm nộp thuế bị phạt thế nào?",
            "Khai sai thuế bị xử lý ra sao?",
            "Khi nào phải chuyển thành doanh nghiệp?",
            "Thuế khoán và thuế kê khai khác nhau thế nào?",
            "Lệ phí môn bài là bao nhiêu?",
            "Mua hàng không có hóa đơn có được không?",
            "Tiền thuê nhà có được tính chi phí không?",
            "Cách tối ưu thuế cho hộ kinh doanh?",
            "Thủ tục đăng ký hộ kinh doanh như thế nào?",
            "Ngưỡng doanh thu không phải nộp thuế là bao nhiêu?"
        ]
        
        # Filter out current question and return 5 random suggestions
        import random
        suggestions = [q for q in all_suggestions if q.lower() not in current_question.lower()]
        return random.sample(suggestions, min(5, len(suggestions)))
