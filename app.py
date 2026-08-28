import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# --- 設定：A4サイズ (300dpi) ---
WIDTH, HEIGHT = 2480, 3508 
SAFE_L = 350  # 左余白を十分に確保
SAFE_R = 2130 # 右限界
CONTENT_W = SAFE_R - SAFE_L

WHITE, GOLD, BLACK, RED, PINK = (255, 255, 255), (184, 134, 11), (30, 30, 30), (220, 0, 0), (255, 0, 127)

# --- フォント準備 ---
@st.cache_resource
def load_font_path():
    font_filename = "NotoSansJP-Bold.ttf"
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf"
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

# --- 改行関数 (右端切れ防止) ---
def wrap_text(text, font, max_width):
    lines = []
    for line in text.splitlines():
        current_line = ""
        for char in line:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            if len(current_line) <= 1 and lines:
                lines[-1] = lines[-1] + current_line
            else:
                lines.append(current_line)
    return "\n".join(lines)

# --- グラフ作成 ---
def create_graph(rate, monthly):
    font_path = load_font_path()
    prop = fm.FontProperties(fname=font_path) if font_path else None
    plt.figure(figsize=(10, 5.5), dpi=150)
    months = np.arange(30 * 12 + 1)
    r = (rate / 100) / 12
    p_val = monthly * (30 * 12)
    assets = monthly * ((1 + r)**months - 1) / r if r > 0 else monthly * months
    f_assets = assets[-1]
    plt.fill_between(months/12, assets, color="#FFD700", alpha=0.3)
    plt.plot(months/12, assets, color="#FF4500", linewidth=8)
    plt.plot(months/12, [monthly * m for m in months], color="#4169E1", linewidth=5, linestyle="--")
    plt.annotate(f'資産合計\n{int(f_assets//10000):,}万円', xy=(30, f_assets), xytext=(20, f_assets*0.8),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontproperties=prop, fontsize=14, weight='bold')
    if rate != 7.5:
        plt.text(20, f_assets*0.72, f"({rate}%で計算)", fontproperties=prop, fontsize=12, color="red")
    plt.annotate(f'投資元金\n{int(p_val//10000):,}万円', xy=(30, p_val), xytext=(22, p_val*0.15),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontproperties=prop, fontsize=14)
    plt.grid(True, linestyle=":", alpha=0.6)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    return Image.open(buf)

# --- ページ生成 ---
def create_pages(name, title, user_photo, qr_code, rate):
    f = get_font
    f_dyn = int(33000 * (((rate/100/12) + 1)**360 - 1) / (rate/100/12)) // 10000
    p_dyn = f_dyn - 1188

    # --- PAGE 1 ---
    p1 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d1 = ImageDraw.Draw(p1)
    d1.rectangle([0, 0, WIDTH, 750], fill=GOLD)
    d1.text((WIDTH//2, 300), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 500), "日本人の９割が知らない", font=f(150), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 1000), "お金の超基本", font=f(350), fill=BLACK, anchor="mm")
    
    p1.paste(create_graph(rate, 33000).resize((2000, 1100)), (WIDTH//2 - 1000, 1300))
    
    msg_main = f"毎月3.3万円の積立でも、30年後には {f_dyn:,}万円に。\n投資元本1,188万円に対し、運用益だけで {p_dyn:,}万円以上 になります！"
    d1.multiline_text((WIDTH//2, 2600), wrap_text(msg_main, f(78), CONTENT_W), font=f(78), fill=BLACK, anchor="mm", align="center", spacing=35)

    d1.rectangle([0, 2850, WIDTH, 3200], fill=PINK)
    d1.text((WIDTH//2, 3025), f"つみたてだけで老後 {f_dyn}万円 を作れます！", font=f(125), fill=WHITE, anchor="mm")
    
    # 1枚目下部：自動改行を適用
    h_info = "細川さんの運用実績から、利回りが7.5%に収斂するという確信を得て、このサービスを開始しました。"
    d1.multiline_text((WIDTH//2, 3400), wrap_text(h_info, f(70), CONTENT_W), font=f(70), fill=BLACK, anchor="mm", align="center")

    # --- PAGE 2 ---
    p2 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d2 = ImageDraw.Draw(p2)
    d2.text((WIDTH//2, 400), "なぜ今、資産形成が必要なのか？", font=f(120), fill=GOLD, anchor="mm")
    
    story = (
        "過去20年間を振り返れば、ITバブル、リーマンショック、コロナショックと多くの暴落がありましたが、長期投資はそれらを乗り越える力があります。\n\n"
        "私は自らの運用実績を通じ、長期利回りが7.5%へと収斂していく事実を目の当たりにしました。毎月3.3万円の積立が、30年後には4446万円、つまり元本から3258万円以上の純利益を生み出す。この実体験に基づいた確信が私の原動力です。\n\n"
        "これぞ複利の効果であり、「複利が起こす奇跡の価値」と呼ばれるものです。正しいつみたてを知り、新NISAやiDeCoを賢く活用することで、家族が安心して暮らせる未来を共に作っていきましょう。"
    )
    d2.multiline_text((SAFE_L, 700), wrap_text(story, f(75), CONTENT_W), font=f(75), fill=BLACK, spacing=45)

    # プロフィールエリア
    d2.rectangle([0, 2550, WIDTH, HEIGHT], fill=(245, 245, 245))
    if user_photo:
        photo = ImageOps.fit(Image.open(user_photo).convert("RGBA"), (700, 700), centering=(0.5, 0.5))
        mask = Image.new("L", (700, 700), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 700, 700), fill=255)
        photo.putalpha(mask)
        p2.paste(photo, (SAFE_L, 2650), photo)
    
    # 肩書き：2行に分けて重なりを防止
    if "ファイナンシャルプランナー" in title:
        d2.text((1050, 2750), "ファイナンシャル", font=f(70), fill=BLACK)
        d2.text((1050, 2835), "プランナー", font=f(70), fill=BLACK)
    else:
        d2.text((1050, 2750), title, font=f(70), fill=BLACK)
    
    d2.text((1050, 3000), name, font=f(180), fill=BLACK)
    
    if qr_code:
        qr = Image.open(qr_code).resize((450, 450))
        qr_x = 1880 # 少し左に寄せて文字切れ防止
        p2.paste(qr, (qr_x, 2750))
        d2.text((qr_x + 225, 3300), "公式LINEはこちら", font=f(65), fill=BLACK, anchor="mm")

    pdf_buf = io.BytesIO()
    p1.save(pdf_buf, format="PDF", save_all=True, append_images=[p2], resolution=300.0)
    return pdf_buf.getvalue()

# --- アプリメイン ---
st.title("📄 FPチラシ生成：最終確定パーフェクト版")
col_a, col_b = st.columns(2)
with col_a:
    input_name = st.text_input("お名前", "細川 豪")
    input_title = st.text_input("肩書き", "ファイナンシャルプランナー")
with col_b:
    input_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    input_qr = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

input_rate = st.select_slider("利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 13.0], value=10.0)

if st.button("🚀 チラシを生成する"):
    if not input_photo or not input_qr:
        st.warning("写真とQRコードをセットしてください")
    else:
        pdf = create_pages(input_name, input_title, input_photo, input_qr, input_rate)
        st.success("✅ 文章の切れ、重なりを全て解消しました！これで完成です。")
        st.download_button("📥 完成版PDFを保存", pdf, f"FP_Flyer_{input_name}_Final.pdf", "application/pdf")
