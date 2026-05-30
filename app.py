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
SAFE_L = 250  
SAFE_R = 2230 
CONTENT_W = SAFE_R - SAFE_L

WHITE, GOLD, BLACK, RED, PINK = (255, 255, 255), (184, 134, 11), (30, 30, 30), (220, 0, 0), (255, 0, 127)

# --- フォント準備 ---
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

# --- 改行関数 ---
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
        lines.append(current_line)
    return "\n".join(lines)

# --- グラフ作成 ---
def create_graph(rate, monthly):
    font_path = load_font_path()
    prop = fm.FontProperties(fname=font_path) if font_path else None
    plt.figure(figsize=(10, 6), dpi=150)
    months = np.arange(30 * 12 + 1)
    r = (rate / 100) / 12
    p_val = monthly * (30 * 12)
    assets = monthly * ((1 + r)**months - 1) / r if r > 0 else monthly * months
    f_assets = assets[-1]
    plt.fill_between(months/12, assets, color="#FFD700", alpha=0.3)
    plt.plot(months/12, assets, color="#FF4500", linewidth=8, label="資産合計")
    plt.plot(months/12, [monthly * m for m in months], color="#4169E1", linewidth=5, linestyle="--", label="投資元金")
    plt.annotate(f'資産合計\n{int(f_assets//10000):,}万円', xy=(30, f_assets), xytext=(21, f_assets*0.8),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontproperties=prop, fontsize=14, weight='bold')
    plt.annotate(f'投資元金\n{int(p_val//10000):,}万円', xy=(30, p_val), xytext=(22, p_val*0.35),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontproperties=prop, fontsize=14)
    plt.grid(True, linestyle=":", alpha=0.6)
    if prop: plt.legend(prop=prop, loc="upper left", fontsize=13)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    return Image.open(buf)

# --- アプリ画面 ---
st.title("📄 FPチラシ生成システム【レイアウト最終修正版】")

with st.sidebar:
    st.header("👤 掲載情報")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)
final_man = int(33000 * (((rate/100/12) + 1)**360 - 1) / (rate/100/12)) // 10000
profit_man = final_man - 1188

def create_pages():
    f = get_font
    
    # --- PAGE 1 (表面) ---
    p1 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d1 = ImageDraw.Draw(p1)
    
    # ヘッダー (上部の余白を拡大)
    d1.rectangle([0, 0, WIDTH, 550], fill=GOLD)
    d1.text((WIDTH//2, 200), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 380), "日本人の９割が知らない", font=f(150), fill=WHITE, anchor="mm")
    
    # タイトル (サイズを微調整して切れ防止)
    d1.text((WIDTH//2, 800), "お金の超基本", font=f(430), fill=BLACK, anchor="mm")
    
    # グラフ
    graph = create_graph(rate, 33000).resize((2000, 1200))
    p1.paste(graph, (WIDTH//2 - 1000, 1050))
    
    # グラフ下の説明文
    msg1 = f"毎月3.3万円の積立でも、30年後には {final_man:,}万円 に。\n投資元本1,188万円に対し、運用益だけで {profit_man:,}万円以上 の利益になります！"
    d1.multiline_text((WIDTH//2, 2400), wrap_text(msg1, f(85), CONTENT_W), font=f(85), fill=BLACK, anchor="mm", align="center", spacing=30)

    # ピンクの帯
    d1.rectangle([0, 2650, WIDTH, 3000], fill=PINK)
    d1.text((WIDTH//2, 2825), f"つみたてだけで老後 {final_man}万円 を作れます！", font=f(125), fill=WHITE, anchor="mm")
    
    # 1P最下部 (細川 3 に修正)
    h_info = "細川 3 の運用実績から、利回りが7.5%に収斂するという確信を得て、このサービスを開始しました。"
    d1.text((WIDTH//2, 3250), wrap_text(h_info, f(75), CONTENT_W), font=f(75), fill=BLACK, anchor="mm", align="center")

    # --- PAGE 2 (裏面) ---
    p2 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d2 = ImageDraw.Draw(p2)
    d2.text((WIDTH//2, 250), "なぜ今、資産形成が必要なのか？", font=f(120), fill=GOLD, anchor="mm")
    
    # 本文 (（細川）を削除)
    story = (
        "過去20年間を振り返れば、ITバブル、リーマンショック、コロナショックと多くの暴落がありましたが、長期投資はそれらを乗り越える力があります。\n\n"
        f"私は自らの運用実績を通じ、長期利回りが7.5%へと収斂していく事実を目の当たりにしました。毎月3.3万円の積立が、30年後には{final_man}万円、つまり元本から{profit_man}万円以上の純利益を生み出す。この実体験に基づいた確信が私の原動力です。\n\n"
        "これぞ複利の効果であり、「複利が起こす奇跡の価値」と呼ばれるものです。正しいつみたてを知り、新NISAやiDeCoを賢く活用することで、家族が安心して暮らせる未来を共に作っていきましょう。"
    )
    d2.multiline_text((SAFE_L, 550), wrap_text(story, f(85), CONTENT_W), font=f(85), fill=BLACK, spacing=55)

    # プロフィールエリア (配置をさらに離して重なりを回避)
    d2.rectangle([0, 2450, WIDTH, HEIGHT], fill=(245, 245, 245))
    
    if user_photo:
        photo = ImageOps.fit(Image.open(user_photo).convert("RGBA"), (700, 700), centering=(0.5, 0.5))
        mask = Image.new("L", (700, 700), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 700, 700), fill=255)
        photo.putalpha(mask)
        p2.paste(photo, (SAFE_L, 2550), photo)
    
    # テキスト (写真から大きく離して配置 X=1250)
    d2.text((1250, 2750), title, font=f(85), fill=BLACK)
    d2.text((1250, 2950), name, font=f(180), fill=BLACK)
    
    # QRコード (右端 X=1850)
    if qr_code:
        qr = Image.open(qr_code).resize((480, 480))
        qr_x = 1850 
        p2.paste(qr, (qr_x, 2600))
        d2.text((qr_x + 240, 3200), "公式LINEはこちら", font=f(70), fill=BLACK, anchor="mm")

    pdf_buf = io.BytesIO()
    p1.save(pdf_buf, format="PDF", save_all=True, append_images=[p2], resolution=300.0)
    return pdf_buf.getvalue()

if st.button("🚀 完成版チラシを生成する"):
    if not user_photo or not qr_code:
        st.warning("写真とQRコードが必要です")
    else:
        with st.spinner("プロ品質のチラシを生成中..."):
            pdf = create_pages()
            st.success("✅ 全ての修正を反映したチラシが完成しました！")
            st.download_button("📥 両面PDFを保存", pdf, f"FP_Perfect_Flyer.pdf", "application/pdf")
