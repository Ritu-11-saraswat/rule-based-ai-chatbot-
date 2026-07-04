from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import anthropic
import re
import os

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# =====================================================
# RULE-BASED RESPONSES (Hinglish)
# =====================================================
RULE_BASED = {
    r"\b(hello|hi|hey|helo|hii|heyy)\b": "Hey there! 😊 Kaise ho aap? Main RuBot hoon — aapki help ke liye hazir!",
    r"\b(namaste|namaskar|sat sri akal|adaab)\b": "Namaste! 🙏 Bahut khushi hui aapse milke. Kya main aapki koi help kar sakta hoon?",
    r"\b(good morning|subah|subha)\b": "Good morning! ☀️ Aaj ka din acha ho aapka! Kya help chahiye?",
    r"\b(good night|goodnight|shubh ratri|raat)\b": "Good night! 🌙 Meethe sapne aayein. Take care!",
    r"\b(bye|goodbye|alvida|tata)\b": "Bye bye! 👋 Jaldi milenge. Take care!",
    r"\b(sad|dukhi|udaas|rona|ro rha|ro rhi)\b": "Aww 😢 Koi baat nahi. Dil pe mat lo. Kuch share karna chahoge? Main sun raha hoon! 💙",
    r"\b(happy|khush|maza|mazaa|excited)\b": "Wah wah! 😄 Bahut badiya! Khushi share karo mujhse bhi!",
    r"\b(angry|gussa|pareshaan|frustrated)\b": "Arre yaar 😤 Relax karo. Deep breath lo. Kya hua? Batao mujhe.",
    r"\b(mood off|bura lag|feel bad|theek nahi)\b": "Aww 🥺 Mood off hai? Koi baat nahi, yaar. Main hoon na! Kuch batana chahoge?",
    r"\b(bored|bore|kuch nahi|khali)\b": "Boring lag raha hai? 😏 Chalo kuch interesting baat karte hain ya main ek joke sunata hoon!",
    r"\b(tired|thaka|thak gaya|thak gayi)\b": "Arre rest karo thodi der! 😴 Apna khayal rakho. Health hi wealth hai!",
    r"\b(lonely|akela|akelapan)\b": "Akela mat feel karo 🤗 Main hoon na yahan! Baat karo mujhse, sab theek ho jayega.",
    r"\b(joke|jokes|mazak|funny|hasao|hasa)\b": "Haha suno ye joke! 😂\n\nEk ladka doctor ke paas gaya:\nLadka: 'Doctor, meri yaadaasht bahut kamzor hai!'\nDoctor: 'Kab se?'\nLadka: 'Kab se kya?' 😂😂",
    r"\b(kaun ho|who are you|tumhara naam|tera naam|your name)\b": "Main RuBot hoon! 🤖 Ek smart Hinglish chatbot jo rule-based bhi hai aur AI-powered bhi! Aapki help karna mera kaam hai.",
    r"\b(kya kar sakte|help|madad|kya karo|abilities)\b": "Main ye sab kar sakta hoon:\n💬 Baat karna\n😄 Jokes sunana\n🤗 Mood improve karna\n❓ Sawaalon ke jawaab dena\n🧠 AI se smart baatein karna\n\nBas poocho!",
    r"\b(thanks|thank you|shukriya|dhanyawad)\b": "Hamesha swagat hai! 😊 Koi aur help chahiye?",
    r"\b(bahut acha|bahut badhiya|zabardast|kamaal)\b": "Arey wah! 🙏 Bahut khushi hui. Kuch aur bhi poocho!",
}

# =====================================================
# Claude API CONFIG — Apni key environment mein daalo
# =====================================================
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """Tu ek friendly Hinglish chatbot hai jiska naam RuBot hai.
Tu hamesha Hinglish mein baat karta hai — yani Hindi aur English mix karke.
Tu helpful, funny, aur caring hai.
Chhote aur natural jawab deta hai — jaise dost se baat ho.
Emojis use kar thodi thodi.
Formal mat ban, casual reh."""

def check_rules(message: str):
    msg_lower = message.lower().strip()
    for pattern, response in RULE_BASED.items():
        if re.search(pattern, msg_lower):
            return response
    return None

def ask_claude(message: str, history: list):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    messages = []
    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text

# =====================================================
# ROUTES
# =====================================================

# ✅ Yeh route chatbot.html ko directly serve karega
@app.route("/")
def index():
    html_path = os.path.join(os.path.dirname(__file__), "chatbot.html")
    return send_file(html_path)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Message is empty"}), 400

    if not CLAUDE_API_KEY:
        return jsonify({"error": "CLAUDE_API_KEY missing. Set CLAUDE_API_KEY or ANTHROPIC_API_KEY in your environment."}), 500

    rule_response = check_rules(user_message)
    if rule_response:
        return jsonify({"reply": rule_response, "source": "rule"})

    try:
        ai_response = ask_claude(user_message, history)
        return jsonify({"reply": ai_response, "source": "ai"})
    except Exception as e:
        return jsonify({
            "reply": "Arre yaar, kuch technical dikkat aa gayi! 😅 Server-side error dekhon.",
            "source": "error",
            "error": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "RuBot is live! 🤖"})

if __name__ == "__main__":
    print("\n🤖 RuBot server start ho raha hai...")
    print("=" * 45)
    print("✅ Browser mein yeh URL kholo:")
    print("   👉  http://localhost:5000")
    print("=" * 45)
    if not CLAUDE_API_KEY:
        print("⚠️  Pehle CLAUDE_API_KEY ya ANTHROPIC_API_KEY environment variable set karo!")
        print("   Warna AI responses nahi aayenge.\n")
    app.run(debug=True, port=5000)
