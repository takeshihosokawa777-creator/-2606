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
SAFE_L = 280  # 左余白を広げました
SAFE_R = 2200 # 右限界をさらに内側に設定
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

# --- グラフ作成 (重なりを徹底回避) ---
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
    
    # 資産合計ラベル (線の上に配置)
    plt.annotate(f'資産合計\n{int(f_assets//10000):,}万円', xy=(30, f_assets), xytext=(20, f_assets*0.85),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontproperties=prop, fontsize=14, weight='bold')
    
    if rate != 7.5:
        plt.text(20, f_assets*0.75, f"({rate}%で計算)", fontproperties=prop, fontsize=12, color="red")

    # 投資元金ラベル (重ならないよう線の下側に配置)
    plt.annotate(f'投資元金\n{int(p_val//10000):,}万円', xy=(30, p_val), xytext=(22, p_val*0.2),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontproperties=prop, fontsize=14)
    
    plt.grid(True, linestyle=":", alpha=0.6)
    if prop: plt.legend(prop=prop, loc="upper left", fontsize=13)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    return Image.open(buf)

# --- ページ作成ロジック ---
def create_pages(name, title, user_photo, qr_code, rate):
    f = get_font
    final_man_dyn = int(33000 * (((rate/100/12) + 1)**360 - 1) / (rate/100/12)) // 10000
    profit_man_dyn = final_man_dyn - 1188

    # --- PAGE 1 ---
    p1 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d1 = ImageDraw.Draw(p1)
    d1.rectangle([0, 0, WIDTH, 750], fill=GOLD)
    d1.text((WIDTH//2, 300), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 500), "日本人の９割が知らない", font=f(150), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 1000), "お金の超基本", font=f(350), fill=BLACK, anchor="mm")
    
    graph = create_graph(rate, 33000).resize((2000, 1200))
    p1.paste(graph, (WIDTH//2 - 1000, 1250))
    
    msg1 = f"毎月3.3万円の積立でも、30年後には {final_man_dyn:,}万円 に。\n投資元本1,188万円に対し、運用益だけで {profit_man_dyn:,}万円以上 になります！"
    d1.multiline_text((WIDTH//2, 2600), wrap_text(msg1, f(85), CONTENT_W), font=f(85), fill=BLACK, anchor="mm", align="center", spacing=30)
    d1.rectangle([0, 2850, WIDTH, 3200], fill=PINK)
    d1.text((WIDTH//2, 3025), f"つみたてだけで老後 {final_man_dyn}万円 を作れます！", font=f(125), fill=WHITE, anchor="mm")
    h_info = "細川さんの運用実績から、利回りが7.5%に収斂するという確信を得て、このサービスを開始しました。"
    d1.text((WIDTH//2, 3400), wrap_text(h_info, f(75), CONTENT_W), font=f(75), fill=BLACK, anchor="mm", align="center")

    # --- PAGE 2 ---
    p2 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d2 = ImageDraw.Draw(p2)
    d2.text((WIDTH//2, 350), "なぜ今、資産形成が必要なのか？", font=f(120), fill=GOLD, anchor="mm")
    
    story = (
        "過去20年間を振り返れば、ITバブル、リーマンショック、コロナショックと多くの暴落がありましたが、長期投資はそれらを乗り越える力があります。\n\n"
        "私は自らの運用実績を通じ、長期利回りが7.5%へと収斂していく事実を目の当たりにしました。毎月3.3万円の積立が、30年後には4446万円、つまり元本から3258万円以上の純利益を生み出す。この実体験に基づいた確信が私の原動力です。\n\n"
        "これぞ複利の効果であり、「複利が起こす奇跡の価値」と呼ばれるものです。正しいつみたてを知り、新NISAやiDeCoを賢く活用することで、家族が安心して暮らせる未来を共に作っていきましょう。"
    )
    # 開始位置を上げ(650->550)、行間を調整(50->42)
    d2.multiline_text((SAFE_L, 550), wrap_text(story, f(85), CONTENT_W), font=f(85), fill=BLACK, spacing=42)

    # プロフィールエリア (開始位置を下げて文章との距離を確保)
    d2.rectangle([0, 2550, WIDTH, HEIGHT], fill=(245, 245, 245))
    if user_photo:
        photo = ImageOps.fit(Image.open(user_photo).convert("RGBA"), (700, 700), centering=(0.5, 0.5))
        mask = Image.new("L", (700, 700), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 700, 700), fill=255)
        photo.putalpha(mask)
        p2.paste(photo, (SAFE_L, 2650), photo)
    
    # テキスト (写真の右に余裕を持って配置)
    d2.text((1050, 2800), title, font=f(70), fill=BLACK) # フォントを少し小さく
    d2.text((1050, 3000), name, font=f(180), fill=BLACK)
    
    # QRコード (右端の余裕を確保 X=1850)
    if qr_code:
        qr = Image.open(qr_code).resize((450, 450))
        qr_x = 1850 
        p2.paste(qr, (qr_x, 2750))
        d2.text((qr_x + 225, 3250), "公式LINEはこちら", font=f(65), fill=BLACK, anchor="mm")

    pdf_buf = io.BytesIO()
    p1.save(pdf_buf, format="PDF", save_all=True, append_images=[p2], resolution=300.0)
    return pdf_buf.getvalue()

# --- アプリメイン ---
st.title("📄 FPチラシ生成：最終確定・パーフェクト版")
if st.button("🚀 チラシを生成する"):
    if not user_photo or not qr_code:
        st.warning("写真とQRコードをセットしてください")
    else:
        with st.spinner("プロ品質のチラシを生成中..."):
            pdf = create_pages(name, title, user_photo, qr_code, rate)
            st.success("✅ 全てのレイアウト修正を完了しました！")
            st.download_button("📥 完成したPDFを保存", pdf, f"FP_Flyer_Perfect.pdf", "application/pdf")
