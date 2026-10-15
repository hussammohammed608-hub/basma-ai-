from flask import Flask, render_template_string, request
import sqlite3
import re
import random
import urllib.request
import json
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('basma_cache.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            question TEXT PRIMARY KEY,
            answer TEXT
        )
    ''')
    default_faqs = [
        ("من قمت بتطويرك؟", "عباس محمد (البارون) هو من قام بتطويري لخدمة مجتمع الاحتياجات الخاصة في العراق والشرق الأوسط."),
        ("من صنعك؟", "عباس محمد (البارون) هو من قام بتطويري لخدمة مجتمع الاحتياجات الخاصة في العراق والشرق الأوسط."),
        ("من طور شكل الزخارف؟", "عباس محمد (البارون) هو من قام بتطويري وطور شكل الزخارف والنقوش الهندسية الرياضية ومكعب روبيك ليصبح جميلاً جداً لخدمة مجتمع الاحتياجات الخاصة.")
    ]
    for q, a in default_faqs:
        cursor.execute("INSERT OR IGNORE INTO cache (question, answer) VALUES (?, ?)", (q, a))
    conn.commit()
    conn.close()

init_db()

basma_system_instruction = """
أنت "بسمة AI"، الخيار الأول لذوي الاحتياجات الخاصة، مساعد ذكي متقدم ومتخصص حصرياً في دعم ومساندة ذوي الاحتياجات الخاصة (الإعاقة الحركية، السمعية، البصرية، الذهنية، وطيف التوحد، وغيرها).
تتميز بأسلوب إنساني، راقٍ، دافئ، ومشجع للغاية.
تلتزم بتقديم إجابات دقيقة ومختصرة ومفيدة باللغة العربية الفصحى البسيطة لضمان السرعة.
قاعدة أساسية صارمة جداً: إذا سألك أي شخص عن من قام بتطويرك، أو من صنعك، أو عن مطورك، يجب أن تجيب وبكل فخر ووضوح: "عباس محمد (البارون) هو من قام بتطويري لخدمة مجتمع الاحتياجات الخاصة في العراق والشرق الأوسط".
"""

WARM_TIPS = [
    "💡 'التحديات تشبه مكعب روبيك؛ مهما بدا معقداً، فكل خطوة تفكير صحيحة تقربنا من الحل والترتيب.'",
    "🌸 'كل محاولة هي خطوة جديدة نحو النجاح، إرادتك هي سر طاقتك الإيجابية.'",
    "✨ 'قلبك القوي ونظرتك المتفائلة تصنعان المعجزات، لا تتوقف عن الابتسام.'",
    "🌱 'كما تنبت الأزهار بعد المطر، تأتي الأيام الجميلة بعد الصبر والعمل الصادق.'",
    "🕊️ 'أنت لست وحدك، في كل خطوة تخطوها هناك من يتمنى لك الخير والرفعة.'"
]

def generate_free_ai(prompt):
    try:
        full_prompt = f"{basma_system_instruction}\n\nسؤال المستخدم: {prompt}"
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [{"role": "user", "content": full_prompt}],
            "model": "openai",
            "json": False
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            result = response.read().decode('utf-8')
            if result:
                return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    return None

def format_markdown_to_html(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #c2185b;">\1</strong>', text)
    text = text.replace('\n', '<br>')
    return text

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بسمة AI | Basma AI</title>
    <meta name="theme-color" content="#e91e63">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #d81b60; --primary-dark: #8e0038; --primary-light: #fce4ec;
            --card-bg: #ffffff; --text-main: #2c3e50; --text-sub: #616161;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Tajawal', sans-serif; }
        body {
            background-color: #fce4ec; color: var(--text-main); min-height: 100vh;
            display: flex; flex-direction: column; justify-content: space-between; padding: 24px 14px;
        }
        .modal-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(44, 62, 80, 0.6); backdrop-filter: blur(8px);
            display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 20px;
        }
        .welcome-card {
            background: #ffffff; max-width: 520px; width: 100%; border-radius: 28px;
            padding: 35px 28px; text-align: center; box-shadow: 0 20px 50px rgba(216, 27, 96, 0.25); border: 2px solid #f8bbd0;
        }
        .welcome-card h2 { color: var(--primary); font-size: 26px; font-weight: 800; margin-bottom: 16px; }
        .welcome-card p { color: #424242; font-size: 16.5px; line-height: 1.8; margin-bottom: 24px; font-weight: 500; }
        .btn-welcome {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: #ffffff; border: none; padding: 14px 40px; font-size: 18px; font-weight: 700; border-radius: 18px; cursor: pointer; width: 100%;
        }
        .container {
            max-width: 760px; width: 100%; margin: auto; background: var(--card-bg);
            border-radius: 28px; box-shadow: 0 15px 35px rgba(216, 27, 96, 0.12); padding: 40px 30px;
            border: 2px solid #f8bbd0; position: relative;
        }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px dashed #f8bbd0; }
        .rubik-math-border {
            width: 80px; height: 6px; background: linear-gradient(90deg, #d81b60, #f48fb1, #d81b60);
            margin: 0 auto 12px auto; border-radius: 4px;
        }
        .header h1 { color: var(--primary); font-size: 34px; font-weight: 800; margin-bottom: 8px; }
        .header p { color: var(--text-sub); font-size: 16px; font-weight: 700; }
        .chat-container { display: flex; flex-direction: column; gap: 18px; margin-bottom: 24px; }
        .chat-bubble { padding: 20px 22px; border-radius: 18px; line-height: 1.85; font-size: 16px; }
        .user-bubble { background-color: #f8f9fa; border-right: 5px solid #5c6bc0; color: #37474f; }
        .ai-bubble { background-color: var(--primary-light); border-right: 5px solid var(--primary); color: #8e0038; }
        .bubble-title { font-weight: 700; font-size: 14px; margin-bottom: 8px; }
        .tips-card {
            background-color: #fff8fa; border-right: 5px solid var(--primary); color: #8e0038;
            padding: 20px; border-radius: 18px; font-size: 15.5px; margin-bottom: 20px; line-height: 1.8;
        }
        .retry-btn {
            background: var(--primary); color: #fff; border: none; padding: 10px 20px;
            font-size: 14.5px; font-weight: 700; border-radius: 10px; cursor: pointer; margin-top: 12px;
        }
        .input-group { display: flex; flex-direction: column; gap: 14px; }
        textarea { width: 100%; height: 120px; padding: 18px; border-radius: 18px; border: 2px solid #f8bbd0; font-size: 16px; resize: none; outline: none; background-color: #fafafa; }
        button.btn-send {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: #ffffff; border: none; padding: 16px 24px; font-size: 17px; font-weight: 700; border-radius: 18px; cursor: pointer;
        }
        .footer { text-align: center; margin-top: 28px; font-size: 13.5px; color: #757575; border-top: 1px dashed #f8bbd0; padding-top: 16px; }
    </style>
</head>
<body>
    <div id="welcomeModal" class="modal-overlay">
        <div class="welcome-card">
            <div class="rubik-math-border"></div>
            <h2>أهلاً بكم في تطبيق بسمة AI</h2>
            <p>أني <strong>عباس محمد</strong>، شاب طموح قررت أخدم ناسي العراقيين بصنع أول تطبيق ذكاء اصطناعي مهتم بشؤون ذوي الاحتياجات الخاصة، والسبب بهلشي كان أخوية الصغير (<strong>سجاد</strong>). ادعوله بالشفاء العاجل.. وأهلاً وسهلاً بيكم! 🌸</p>
            <button class="btn-welcome" onclick="closeWelcome()">حسناً</button>
        </div>
    </div>
    <div class="container">
        <div class="header">
            <div class="rubik-math-border"></div>
            <h1>بسمة AI</h1>
            <p>الخيار الأول لذوي الاحتياجات الخاصة</p>
        </div>
        {% if question or answer or is_busy %}
            <div class="chat-container">
                {% if question %}
                    <div class="chat-bubble user-bubble">
                        <div class="bubble-title" style="color: #3f51b5;">سؤالك:</div>
                        {{ question }}
                    </div>
                {% endif %}
                {% if is_busy %}
                    <div class="tips-card">
                        <div style="font-weight: 700; font-size: 16px; margin-bottom: 8px;">🌸 نكتمل بعزيمتك.. جاري التزامن مع الشبكة!</div>
                        <div>{{ current_tip }}</div>
                        <button class="retry-btn" onclick="document.getElementById('chatForm').submit();">إعادة التزامن الآن ⟳</button>
                    </div>
                {% endif %}
                {% if answer %}
                    <div class="chat-bubble ai-bubble">
                        <div class="bubble-title" style="color: var(--primary-dark);">إجابة بسمة AI:</div>
                        {{ answer | safe }}
                    </div>
                {% endif %}
            </div>
        {% endif %}
        <form id="chatForm" class="input-group" method="POST">
            <textarea name="question" placeholder="اكتب سؤالك هنا..." required>{% if is_busy %}{{ question }}{% endif %}</textarea>
            <button type="submit" class="btn-send">إرسال</button>
        </form>
        <div class="footer">تم التطوير بواسطة عباس البارون 🇮🇶</div>
    </div>
    <script>
        function closeWelcome() {
            document.getElementById('welcomeModal').style.display = 'none';
            sessionStorage.setItem('hasSeenWelcome', 'true');
        }
        window.onload = function() {
            if (sessionStorage.getItem('hasSeenWelcome') === 'true') {
                document.getElementById('welcomeModal').style.display = 'none';
            }
        };
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    answer, question, is_busy, current_tip = "", "", False, ""
    if request.method == "POST":
        question = request.form.get("question")
        if question:
            q_clean = question.strip()
            conn = sqlite3.connect('basma_cache.db')
            cursor = conn.cursor()
            cursor.execute("SELECT answer FROM cache WHERE question = ?", (q_clean,))
            row = cursor.fetchone()
            if row:
                answer = row[0]
                conn.close()
            else:
                conn.close()
                raw_answer = generate_free_ai(q_clean)
                if raw_answer:
                    answer = format_markdown_to_html(raw_answer)
                    conn = sqlite3.connect('basma_cache.db')
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR REPLACE INTO cache (question, answer) VALUES (?, ?)", (q_clean, answer))
                    conn.commit()
                    conn.close()
                else:
                    is_busy = True
                    current_tip = random.choice(WARM_TIPS)
    return render_template_string(HTML_TEMPLATE, answer=answer, question=question, is_busy=is_busy, current_tip=current_tip)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
