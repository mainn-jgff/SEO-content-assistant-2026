const BASE_URL = '/api'; // Đường dẫn tương đối trên Vercel
let currentSessionData = {};

// Ghi nhận giờ bắt đầu khi reload trang
currentSessionData.start_time = new Date().toISOString();

// UI Elements
const chatHistory = document.getElementById('chat-history');
const interactionArea = document.getElementById('interaction-area');
const loadingIndicator = document.getElementById('loading-indicator');

const state1Form = document.getElementById('state1-form');
const state2Container = document.getElementById('state2-container');
const state3Container = document.getElementById('state3-container');
const state45Container = document.getElementById('state4-5-container');

function showLoading() {
    Array.from(interactionArea.children).forEach(child => {
        if (child.id !== 'loading-indicator') child.classList.add('hidden');
    });
    loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

function appendUserMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'message user-message fade-in';
    msg.innerHTML = `
        <div class="avatar">U</div>
        <div class="content"><p>${text}</p></div>
    `;
    chatHistory.appendChild(msg);
}

function appendBotMessage(title, text) {
    const msg = document.createElement('div');
    msg.className = 'message bot-message fade-in';
    msg.innerHTML = `
        <div class="avatar">AI</div>
        <div class="content">
            ${title ? `<h3>${title}</h3>` : ''}
            <div>${text}</div>
        </div>
    `;
    chatHistory.appendChild(msg);
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

// Hiển thị/ẩn ô nhập tuỳ chỉnh khi chọn kênh "Khác"
document.getElementById('channel').addEventListener('change', (e) => {
    const customGroup = document.getElementById('custom-length-group');
    if (e.target.value === 'Khác') {
        customGroup.classList.remove('hidden');
    } else {
        customGroup.classList.add('hidden');
    }
});

// STATE 1: Bắt đầu
state1Form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    currentSessionData.topic = document.getElementById('topic').value;
    currentSessionData.goal = document.getElementById('goal').value;
    currentSessionData.product_usp = document.getElementById('product_usp').value;
    currentSessionData.audience = document.getElementById('audience').value;
    currentSessionData.voice = document.querySelector('input[name="voice"]:checked').value;
    currentSessionData.channel = document.getElementById('channel').value;
    
    if (currentSessionData.channel === 'Khác') {
        currentSessionData.custom_length = document.getElementById('custom_length').value || '2000';
    }

    appendUserMessage(`Bắt đầu phân tích chủ đề: **${currentSessionData.topic}** (Kênh: ${currentSessionData.channel})`);
    showLoading();

    try {
        const response = await fetch(`${BASE_URL}/state1`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(currentSessionData)
        });
        const resData = await response.json();
        if (resData.error) throw new Error(resData.error);
        if (!resData.data || resData.data.trim() === '') throw new Error('AI không trả về nội dung. Vui lòng thử lại.');
        
        currentSessionData.suggested_keywords = resData.data; // Lưu lại
        appendBotMessage("Phân tích & Ma trận từ khóa 📊", "Tôi đã phân tích xong Search Intent và đề xuất ma trận từ khóa. Bạn hãy xem chi tiết ở khung bên dưới và chọn từ khóa phù hợp nhé!");
        
        hideLoading();
        state2Container.classList.remove('hidden');
        document.getElementById('keywords-render').innerHTML = marked.parse(resData.data);
        
    } catch (err) {
        alert("Lỗi: " + err.message);
        hideLoading();
        state1Form.classList.remove('hidden');
    }
});

// STATE 2: Gửi từ khóa
document.getElementById('btn-submit-keywords').addEventListener('click', async () => {
    const selected = document.getElementById('selected_keywords').value;
    if (!selected) return alert("Vui lòng nhập từ khóa bạn chọn!");

    currentSessionData.selected_keywords = selected;
    appendUserMessage(`Từ khóa: ${selected}`);
    showLoading();

    try {
        const response = await fetch(`${BASE_URL}/state2`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(currentSessionData)
        });
        const resData = await response.json();
        if (resData.error) throw new Error(resData.error);

        appendBotMessage("Dàn ý Đề xuất 📝", "Tôi đã lập dàn ý theo cấu trúc Kim Tự Tháp ngược. Bạn có thể xem và chỉnh sửa ở khung phía dưới.");
        
        hideLoading();
        state3Container.classList.remove('hidden');
        document.getElementById('outline-editor').value = resData.data;

    } catch (err) {
        alert("Lỗi: " + err.message);
        hideLoading();
        state2Container.classList.remove('hidden');
    }
});

// STATE 3: Sinh content & QA
document.getElementById('btn-approve-outline').addEventListener('click', async () => {
    currentSessionData.outline = document.getElementById('outline-editor').value;
    
    appendUserMessage("Đã duyệt dàn ý. Bắt đầu viết bài!");
    showLoading();

    try {
        const resContent = await fetch(`${BASE_URL}/state3`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(currentSessionData)
        });
        const dataContent = await resContent.json();
        if (dataContent.error) throw new Error(dataContent.error);

        currentSessionData.final_content = dataContent.data;
        document.getElementById('content-tab').innerHTML = marked.parse(dataContent.data);
        appendBotMessage("Đã hoàn thành Bài Viết ✨", "Đang tiến hành chạy Auto-QA...");

        const resQA = await fetch(`${BASE_URL}/state4`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(currentSessionData)
        });
        const dataQA = await resQA.json();
        if (dataQA.error) throw new Error(dataQA.error);

        document.getElementById('qa-tab').innerHTML = marked.parse(dataQA.data);
        
        hideLoading();
        state45Container.classList.remove('hidden');
        appendBotMessage("Báo cáo QA 🎯", "Xin mời bạn kiểm tra bài viết và báo cáo QA ở bên dưới. Hãy để lại feedback cuối cùng để lưu vào bộ nhớ.");

    } catch (err) {
        alert("Lỗi: " + err.message);
        hideLoading();
        state3Container.classList.remove('hidden');
    }
});

// STATE 6: User Feedback
document.getElementById('btn-submit-feedback').addEventListener('click', async () => {
    currentSessionData.user_feedback = document.getElementById('user-feedback').value;
    
    document.getElementById('btn-submit-feedback').disabled = true;
    document.getElementById('btn-submit-feedback').innerText = "Đang lưu...";

    try {
        await fetch(`${BASE_URL}/state5`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(currentSessionData)
        });
        
        document.getElementById('success-modal').classList.remove('hidden');
        
    } catch (err) {
        alert("Lỗi khi lưu dữ liệu. " + err.message);
        document.getElementById('btn-submit-feedback').disabled = false;
        document.getElementById('btn-submit-feedback').innerText = "✅ Hoàn tất & Gửi lên CMS (Google Sheets)";
    }
});

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});
