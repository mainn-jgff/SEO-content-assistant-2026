import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-pro-latest')

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

def generate_keyword_matrix(data):
    prompt = f"""{get_system_prompt()}
    
# USER INPUT
- Chủ đề bài viết: {data.get('topic')}
- Mục tiêu: {data.get('goal')}
- Thông tin sản phẩm/USP: {data.get('product_usp')}
- Chân dung khách hàng: {data.get('audience')}
- Tông giọng (Brand Voice): {data.get('voice')}

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

# TASK: XÂY DỰNG DÀN Ý KIM TỰ THÁP NGƯỢC
Hãy xây dựng Dàn ý chi tiết dựa trên những từ khóa đã được chọn:
1. Áp dụng mô hình "Kim tự tháp ngược" (Giải quyết trực diện Search Intent ngay ở H2 đầu tiên).
2. Sắp xếp cấu trúc H1, H2, H3 rõ ràng, logic theo luồng AIDA.
3. Ghi rõ [Vị trí dự kiến chèn ảnh], [Vị trí chèn External Links thẩm quyền], [CTA] tại các mục H2, H3 sao cho hợp lý.

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

# TASK: VIẾT BÀI CHUẨN 7C+6S THỰC THẾ
Dựa vào dàn ý trên, tiến hành viết nguyên bài viết hoàn chỉnh.
YỀU CẦU NGHIÊM NGẶT:
1. Straightforward: Trả lời thẳng thắc mắc ở đoạn đầu tiên (Direct Answer).
2. UX: Câu tối đa 30 từ, đoạn văn tối đa 4 dòng (Rất quan trọng).
3. Cấu trúc Markdown đầy đủ (H1, H2, H3, in đậm). 
4. E-E-A-T: Thêm một vài số liệu thực tế ảo hoặc case study tượng trưng vào bài để tăng độ tin cậy.
5. Sinh thêm MỘT BẢNG chứa: Meta Title (50-60 ký tự), Meta Description (120-150 ký tự), URL Slug ở CÚỐI BÀI.

Viết trực tiếp nội dung bài blog. Không cần chào hỏi.
"""
    response = model.generate_content(prompt)
    return response.text

def qa_content(data):
    prompt = f"""{get_system_prompt()}

# CONTENT TO QA:
{data.get('final_content')}

- Tông giọng mục tiêu: {data.get('voice')}

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
