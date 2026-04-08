import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ============================================================
# GEMINI AI AGENT (gộp từ agent.py)
# ============================================================

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')


def get_system_prompt():
    return """
# ROLE & IDENTITY
Bạn là "Content Master Agent 2026" - chuyên gia SEO/GEO tối thượng và Kỹ sư Nội dung AI. 
Nhiệm vụ của bạn là đồng hành cùng đội ngũ Content Marketing để sản xuất nội dung tuân thủ "Tiêu chuẩn 7C+6S" và "Quy trình 7 bước SEO 2026".

# CORE PHILOSOPHY (SEO 2026)
1. Content-as-a-Product: Nội dung là sản phẩm, không phải nhồi nhét từ khóa.
2. AI Search (SGE/GEO): Direct Answer ngay đầu bài, tối ưu AI-Readability để lọt AI Snapshot.
3. Mobile UX: Bắt buộc câu ngắn (20-30 từ), đoạn văn cực ngắn (3-4 dòng).
4. E-E-A-T: Có dẫn chứng, số liệu, chuyên môn sâu.
5. Legal Strictness: Tuân thủ pháp lý (VD: không dùng từ "trị dứt điểm" với sản phẩm không phải thuốc).
"""


def get_channel_guidelines(channel, custom_length=None):
    guidelines = {
        'Facebook': 'Kênh: Facebook. Thông điệp quan trọng nhất phải nằm trong 50 ký tự đầu tiên (vì Facebook cắt preview). Giới hạn tối đa toàn bài: 60.000 ký tự. Nên viết ngắn gọn, dễ scan, CTA rõ ràng.',
        'Website': 'Kênh: Website/Blog. Tối đa 2.000 từ. Cấu trúc SEO đầy đủ (H1, H2, H3, Meta, Internal/External links). Tối ưu Direct Answer cho AI Search.',
        'Instagram': 'Kênh: Instagram. Giới hạn caption dưới 150 ký tự. Viết cực ngắn, súc tích, có emoji, kèm CTA. Ưu tiên Hook mạnh ở dòng đầu.',
        'Linkedin': 'Kênh: LinkedIn. Thông điệp quan trọng nhất phải nằm trong 150 ký tự đầu tiên (vì LinkedIn cắt "...see more"). Không giới hạn ký tự tổng, nhưng nên tập trung vào giá trị chuyên môn, insight ngành, tone B2B.',
    }
    if channel == 'Khác' and custom_length:
        return f'Kênh: Tuỳ chỉnh. Người dùng yêu cầu tổng bài viết khoảng {custom_length} ký tự. Hãy tuân thủ giới hạn này.'
    return guidelines.get(channel, 'Kênh: Website/Blog. Tối đa 2.000 từ.')


def generate_keyword_matrix(data):
    prompt = f"""{get_system_prompt()}
    
# USER INPUT
- Chủ đề bài viết: {data.get('topic')}
- Mục tiêu: {data.get('goal')}
- Thông tin sản phẩm/USP: {data.get('product_usp')}
- Chân dung khách hàng: {data.get('audience')}
- Tông giọng (Brand Voice): {data.get('voice')}
- Kênh đăng bài: {data.get('channel', 'Website')}

# TASK: ĐỌC VỊ SEARCH INTENT & ĐỀ XUẤT MA TRẬN TỪ KHÓA
1. Phân tích ngắn gọn Search Intent của chủ đề.
2. Nêu 1 Cảnh báo pháp lý/ngôn từ cần tránh (nếu có).
3. Đề xuất Ma trận từ khóa bằng BẢNG MARKDOWN gồm các cột sau: Phân loại, Từ khóa, Volume (ước tính logic), Độ khó (Thấp/TB/Cao).
Phân loại gồm: Từ khóa Chính (1-2 từ), Từ khóa Phụ (3-5 từ), Từ khóa Ngách, Từ khóa Ngữ nghĩa (LSI).

Vui lòng chỉ in phần phân tích và Bảng. Đừng in thừa thãi. Hãy kết thúc bằng câu: "Vui lòng chọn các từ khóa bạn muốn đưa vào bài, hoặc bảo tôi dùng tất cả."
"""
    response = model.generate_content(prompt)
    return response.text


def generate_outline(data):
    prompt = f"""{get_system_prompt()}

# USER INPUT
- Từ khóa đã chọn: {data.get('selected_keywords')}
- (Các thông tin ngữ cảnh: Tông giọng {data.get('voice')}, Đối tượng {data.get('audience')})
- {get_channel_guidelines(data.get('channel', 'Website'), data.get('custom_length'))}

# TASK: XÂY DỰNG DÀN Ý KIM TỰ THÁP NGƯỢC
Hãy xây dựng Dàn ý chi tiết dựa trên những từ khóa đã được chọn:
1. Áp dụng mô hình "Kim tự tháp ngược" (Giải quyết trực diện Search Intent ngay ở H2 đầu tiên).
2. Sắp xếp cấu trúc H1, H2, H3 rõ ràng, logic theo luồng AIDA. (Lưu ý: KHÔNG in các chữ "H1:", "H2:", "H3:" vào đầu tiêu đề)
3. Ghi rõ [Vị trí dự kiến chèn ảnh], [Vị trí chèn External Links thẩm quyền], [CTA] tại các mục H2, H3 sao cho hợp lý.
4. KHÔNG in ra các ghi chú cá nhân của AI (như "Ghi chú UX", "Mục đích",...). Chỉ xuất định dạng Markdown sạch sẽ.

Chỉ xuất định dạng Markdown, hãy chi tiết hóa nội dung dự kiến trong mỗi Heading.
"""
    response = model.generate_content(prompt)
    return response.text


def generate_content(data):
    prompt = f"""{get_system_prompt()}

# USER INPUT
- Dàn ý đã duyệt: 
{data.get('outline')}

- Từ khóa bắt buộc (nhớ bôi đậm tự nhiên khi xuất hiện): {data.get('selected_keywords')}
- Tông giọng: {data.get('voice')}
- {get_channel_guidelines(data.get('channel', 'Website'), data.get('custom_length'))}

# TASK: VIẾT BÀI CHUẨN 7C+6S THỰC TẾ
Dựa vào dàn ý trên, tiến hành viết nguyên bài viết hoàn chỉnh.

QUY TẮC ĐỘ DÀI THEO KÊNH (BẮT BUỘC TUÂN THỦ):
- Nếu kênh là Facebook: Thông điệp quan trọng nhất phải nằm trong 50 ký tự ĐẦU TIÊN. Tối đa 60.000 ký tự toàn bài. Viết ngắn, dễ scan.
- Nếu kênh là Website: Tối đa 2.000 từ. Cấu trúc SEO đầy đủ.
- Nếu kênh là Instagram: Tối đa 150 ký tự. Cực ngắn, có emoji, hook mạnh dòng đầu.
- Nếu kênh là LinkedIn: Thông điệp quan trọng nhất trong 150 ký tự đầu. Không giới hạn tổng, tone B2B chuyên nghiệp.
- Nếu kênh là Khác: Tuân thủ số ký tự do người dùng yêu cầu.

YÊU CẦU NGHIÊM NGẶT KHÁC:
1. Straightforward: Trả lời thẳng thắc mắc ở đoạn đầu tiên (Direct Answer).
2. UX: Câu tối đa 50 từ, đoạn văn tối đa 4 dòng (Rất quan trọng).
3. Cấu trúc Markdown đầy đủ (Chỉ dùng dấu # cho heading, TUYỆT ĐỐI KHÔNG ghi chữ H1, H2, H3 vào trong bài viết). 
4. Không bao gồm các dòng ghi chú, phân tích tư duy. Hãy xuất ra ĐÚNG như một bài đăng lên kênh tương ứng.
5. E-E-A-T: Thêm một vài số liệu thực tế ảo hoặc case study tượng trưng vào bài để tăng độ tin cậy.
6. Sinh thêm MỘT BẢNG chứa: Meta Title (50-60 ký tự), Meta Description (120-150 ký tự), URL Slug ở CUỐI BÀI.

Viết trực tiếp nội dung bài. Không cần chào hỏi.
"""
    response = model.generate_content(prompt)
    return response.text


def qa_content(data):
    prompt = f"""{get_system_prompt()}

# CONTENT TO QA:
{data.get('final_content')}

- Tông giọng mục tiêu: {data.get('voice')}
- {get_channel_guidelines(data.get('channel', 'Website'), data.get('custom_length'))}

# TASK: ĐÁNH GIÁ CHẤT LƯỢNG AUTO-QA
Đóng vai "Quality Rater" của Google, quét bài viết trên và xuất một đánh giá bằng MARKDOWN:
1. Bảng Chấm Điểm (1-100) theo 3 tiêu chí:
   - UX & Formatting (Các đoạn văn đủ ngắn chưa? Direct answer?)
   - Technical SEO (Từ khóa có ở H1, Meta, in đậm, phân bổ hợp lý?)
   - E-E-A-T & Branding (Đúng Tông giọng? Có tính chuyên môn/USP?)
2. Chấm điểm tổng cộng / 100.
3. Đưa ra 1-3 lời khuyên ngắn gọn để Editor tinh chỉnh lại.

Luôn định dạng dễ nhìn và chuyên nghiệp.
"""
    response = model.generate_content(prompt)
    return response.text


# ============================================================
# FLASK APP (API ROUTES)
# ============================================================

app = Flask(__name__)
CORS(app)

WEBHOOK_URL = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")


@app.route('/api/state1', methods=['POST'])
def start_session():
    data = request.json
    try:
        matrix = generate_keyword_matrix(data)
        return jsonify({'data': matrix, 'state': 2})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/state2', methods=['POST'])
def select_keywords():
    data = request.json
    try:
        outline = generate_outline(data)
        return jsonify({'data': outline, 'state': 3})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/state3', methods=['POST'])
def approve_outline():
    data = request.json
    try:
        content = generate_content(data)
        return jsonify({'data': content, 'state': 4})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/state4', methods=['POST'])
def do_qa():
    data = request.json
    try:
        qa_result = qa_content(data)
        return jsonify({'data': qa_result, 'state': 5})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/state5', methods=['POST'])
def submit_feedback():
    data = request.json

    if WEBHOOK_URL:
        end_time = datetime.now().isoformat()
        payload = {
            "start_time": data.get('start_time', ''),
            "end_time": end_time,
            "topic": data.get('topic', ''),
            "goal": data.get('goal', ''),
            "audience": data.get('audience', ''),
            "voice": data.get('voice', ''),
            "suggested_keywords": data.get('suggested_keywords', ''),
            "selected_keywords": data.get('selected_keywords', ''),
            "final_content": data.get('final_content', ''),
            "user_feedback": data.get('user_feedback', '')
        }
        try:
            requests.post(WEBHOOK_URL, json=payload, timeout=10)
        except Exception as e:
            print("Webhook error:", str(e))

    return jsonify({'success': True, 'state': 6})
