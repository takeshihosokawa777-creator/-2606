import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import requests
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# --- 設定：A4サイズ (300dpi) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE, GOLD, BLACK, RED, PINK = (255, 255, 255), (184, 134, 11), (30, 30, 30), (220, 0, 0), (255, 0, 127)

# --- フォント準備 (確実にダウンロード) ---
@st.cache_resource
def load_font_path():
    font_filename = "NotoSansJP-Bold.ttf"
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/OTC/NotoSansCJKjp-Bold.otf"
    if not os.path.exists(font_filename):
        try:
            response = requests.get(url, timeout=30)
            with open(font_filename, "wb") as f: f.write(response.content)
        except: return None
    return font_filename

def get_font(size):
    path = load_font_path()
    try:
        if path: return ImageFont.truetype(path, size)
    except: pass
    return ImageFont.load_default()

# --- グラフ作成関数 (日本語対応) ---
def create_graph(rate, monthly):
    font_path = load_font_path()
    prop = fm.FontProperties(fname=font_path) if font_path else None
    
    plt.figure(figsize=(10, 6.5), dpi=150)
    months = np.arange(30 * 12 + 1)
    r = (rate / 100) / 12
    principal = monthly * months
    assets = monthly * ((1 + r)**months - 1) / r if r > 0 else principal
    
    plt.fill_between(months/12, assets, color="#FFD700", alpha=0.2, label="運用収益")
    plt.plot(months/12, assets, color="#FF4500", linewidth=5, label="資産合計")
    plt.plot(months/12, principal, color="#4169E1", linewidth=4, linestyle="--", label="投資元金")
    
    plt.title(f"30年間の利回り {rate}% シミュレーション", fontsize=18, fontproperties=prop)
    plt.xlabel("経過年数 (年)", fontsize=14, fontproperties=prop)
    plt.ylabel("資産額 (円)", fontsize=14, fontproperties=prop)
    plt.grid(True, linestyle=":", alpha=0.6)
    if prop: plt.legend(prop=prop, loc="upper left", fontsize=12)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    return Image.open(buf)

# --- メイン画面 ---
st.title("📄 FPコンサル用 A4両面チラシ生成")

with st.sidebar:
    st.header("👤 掲載情報")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)
final_amount_man = int(33000 * (( (rate/100/12) + 1)**360 - 1) / (rate/100/12)) // 10000

# --- チラシ作成ロジック ---
def create_pages():
    f = get_font
    
    # --- PAGE 1 (表) ---
    p1 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d1 = ImageDraw.Draw(p1)
    d1.rectangle([0, 0, WIDTH, 450], fill=GOLD)
    d1.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 320), "日本人の９割が知らない", font=f(150), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 700), "お金の超基本", font=f(450), fill=BLACK, anchor="mm")
    
    # グラフ配置
    graph = create_graph(rate, 33000).resize((2100, 1300))
    p1.paste(graph, (WIDTH//2 - 1050, 1000))
    
    # 下部インパクト
    d1.rectangle([0, 2400, WIDTH, 2800], fill=PINK)
    d1.text((WIDTH//2, 2600), f"つみたてだけで老後 {final_amount_man}万円 を作れます！", font=f(140), fill=WHITE, anchor="mm")
    
    txt1 = "「iDeCoだけで老後2000万円作る」をコンセプトに、\n長期・積立・分散投資の重要性をお伝えしています。"
    d1.multiline_text((WIDTH//2, 3100), txt1, font=f(90), fill=BLACK, anchor="mm", align="center", spacing=30)

    # --- PAGE 2 (裏) ---
    p2 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d2 = ImageDraw.Draw(p2)
    d2.text((WIDTH//2, 250), "なぜ「長期つみたて」が最強なのか？", font=f(120), fill=GOLD, anchor="mm")
    
    story = (
        "過去20年間を振り返ると、ITバブル崩壊、リーマンショック、\n"
        "東日本大震災、コロナショックなど、多くの暴落がありました。\n\n"
        "しかし、長期投資はそれらの暴落を乗り越える効果があります。\n"
        "2019年の老後2000万円問題により、多くの人が年金だけでは\n"
        "不足することを認識しました。\n\n"
        "これぞ複利の効果であり、「複利が起こす奇跡の価値」です。\n"
        "正しいつみたてを知っていただき、国の制度であるNISAやiDeCoを\n"
        "活用し、家族を守れる最適な資産形成をご案内いたします。"
    )
    d2.multiline_text((200, 500), story, font=f(85), fill=BLACK, spacing=50)

    # プロフィールエリア (下部)
    d2.rectangle([0, 2400, WIDTH, HEIGHT], fill=(245, 245, 245)) # 薄いグレー
    if user_photo:
        photo = ImageOps.fit(Image.open(user_photo).convert("RGBA"), (700, 700), centering=(0.5, 0.5))
        mask = Image.new("L", (700, 700), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 700, 700), fill=255)
        photo.putalpha(mask)
        p2.paste(photo, (200, 2550), photo)
    
    if qr_code:
        qr = Image.open(qr_code).resize((550, 550))
        p2.paste(qr, (WIDTH - 800, 2600))
        d2.text((WIDTH - 525, 3250), "公式LINEはこちら", font=f(75), fill=BLACK, anchor="mm")

    d2.text((1000, 2750), title, font=f(80), fill=BLACK)
    d2.text((1000, 2950), name, font=f(180), fill=BLACK)

    # PDF保存
    pdf_buf = io.BytesIO()
    p1.save(pdf_buf, format="PDF", save_all=True, append_images=[p2], resolution=300.0)
    return pdf_buf.getvalue()

if st.button("🚀 A4両面チラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("写真とQRコードが必要です")
    else:
        with st.spinner("高品質な両面PDFを生成中..."):
            pdf = create_pages()
            st.success("✅ 両面チラシが完成しました！")
            st.download_button("📥 両面PDFをダウンロード", pdf, f"FP_Flyer_{name}.pdf", "application/pdf")
