import React, { useState, useRef, useEffect } from 'react';
import { chatbotAPI } from '../api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { FaPaperPlane, FaRobot, FaUser, FaLightbulb } from 'react-icons/fa';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    "Doanh thu 200 triệu/năm phải nộp bao nhiêu thuế?",
    "Chi phí nào được khấu trừ?",
    "Khi nào phải dùng hóa đơn điện tử?",
    "Chậm nộp thuế bị phạt thế nào?",
    "Khi nào phải chuyển thành doanh nghiệp?"
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const askQuestion = async (q) => {
    setMessages(prev => [...prev, { type: 'user', text: q }]);
    setLoading(true);
    
    try {
      const res = await chatbotAPI.ask(q);
      setMessages(prev => [...prev, { 
        type: 'bot', 
        text: res.data.answer, 
        disclaimer: res.data.disclaimer 
      }]);
      
      if (res.data.suggested_questions) {
        setSuggestedQuestions(res.data.suggested_questions);
      }
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', text: 'Lỗi: ' + error.message }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;
    
    await askQuestion(question);
    setQuestion('');
  };

  const handleSuggestedClick = (suggested) => {
    if (!loading) askQuestion(suggested);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-full shadow-lg shadow-cyan-500/50">
              <FaRobot className="text-white text-2xl" />
            </div>
            <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Chatbot Tư Vấn Thuế
            </h2>
          </div>
          <p className="text-slate-400 text-lg">Hỏi tôi về thuế, chi phí, hóa đơn và các vấn đề kinh doanh khác</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6 mb-8">
          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col bg-gradient-to-br from-slate-800/80 to-slate-900/80 border-slate-700/50 shadow-2xl">
              <CardContent className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth">
                {messages.length === 0 && (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <div className="p-6 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-full w-32 h-32 mx-auto flex items-center justify-center border border-cyan-500/30">
                      <FaRobot className="w-16 h-16 text-cyan-400 opacity-80" />
                    </div>
                    <p className="text-slate-300 text-lg font-medium">Bắt đầu cuộc trò chuyện</p>
                    <p className="text-slate-400 text-sm max-w-xs">Hỏi những câu hỏi về thuế, chi phí kinh doanh, hoặc chọn từ các gợi ý bên cạnh</p>
                  </div>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3 animate-fade-in ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.type === 'bot' && (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500/30 to-blue-500/30 flex items-center justify-center flex-shrink-0 border border-cyan-500/50 shadow-lg shadow-cyan-500/20">
                      <FaRobot className="w-5 h-5 text-cyan-300" />
                    </div>
                  )}
                  <div className={`max-w-xs md:max-w-sm lg:max-w-md rounded-2xl p-4 ${
                    msg.type === 'user' 
                      ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/30 rounded-br-none' 
                      : 'bg-slate-700/60 text-slate-100 border border-slate-600/50 rounded-bl-none backdrop-blur-sm'
                  }`}>
                    <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</div>
                    {msg.disclaimer && (
                      <p className="text-xs mt-3 opacity-70 border-t border-current/20 pt-2">
                        ⚠️ {msg.disclaimer}
                      </p>
                    )}
                  </div>
                  {msg.type === 'user' && (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-cyan-500/40">
                      <FaUser className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-3 animate-fade-in">
                  <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0 border border-cyan-500/30">
                    <FaRobot className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600/50">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                  </div>
                </div>
                )}
                <div ref={messagesEndRef} />
              </CardContent>
            </Card>

            {/* Input Form */}
            <form onSubmit={handleAsk} className="flex gap-3 mt-6">
              <Input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Nhập câu hỏi của bạn..."
                disabled={loading}
                className="flex-1 bg-slate-700/50 border-slate-600/50 text-white placeholder-slate-400"
              />
              <Button 
                type="submit" 
                disabled={loading || !question.trim()} 
                size="lg"
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 shadow-lg shadow-cyan-500/25"
              >
                <FaPaperPlane className="w-4 h-4" />
              </Button>
            </form>
          </div>

          {/* Suggested Questions Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8 bg-gradient-to-br from-slate-800/80 to-slate-900/80 border-slate-700/50 shadow-2xl">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-lg bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                  <FaLightbulb className="text-yellow-400" /> Gợi ý
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 max-h-[600px] overflow-y-auto">
                {suggestedQuestions.map((sq, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestedClick(sq)}
                    disabled={loading}
                    className="w-full text-left p-4 rounded-lg border border-slate-600/50 bg-slate-700/30 hover:bg-gradient-to-r hover:from-cyan-500/20 hover:to-blue-500/20 hover:border-cyan-500/50 transition-all duration-300 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-cyan-500/20 text-slate-300 hover:text-cyan-300 font-medium"
                  >
                    ✨ {sq}
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
