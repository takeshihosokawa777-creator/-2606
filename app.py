import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import requests
import matplotlib.pyplot as plt
import numpy as np

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE, GOLD, BLACK, RED, PINK = (255, 255, 255), (184, 134, 11), (30, 30, 30), (220, 0, 0), (255, 0, 127)

# --- フォント準備 ---
@st.cache_resource
def load_font():
    font_filename = "font_bold.ttf"
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/OTC/NotoSansCJKjp-Bold.otf"
    if not os.path.exists(font_filename):
        try:
            response = requests.get(font_url, timeout=30)
            with open(font_filename, "wb") as f: f.write(response.content)
        except: return None
    return font_filename

def get_font(size):
    path = load_font()
    try:
        if path: return ImageFont.truetype(path, size)
    except: pass
    return ImageFont.load_default()

# --- グラフ作成関数 ---
def create_graph(rate, monthly, years=30):
    plt.figure(figsize=(10, 6), dpi=150)
    months = np.arange(years * 12 + 1)
    r = (rate / 100) / 12
    principal = monthly * months
    assets = monthly * ((1 + r)**months - 1) / r if r > 0 else principal
    
    plt.fill_between(months/12, assets, color="#FFD700", alpha=0.3, label="運用収益")
    plt.plot(months/12, assets, color="#FF4500", linewidth=4, label="資産合計")
    plt.plot(months/12, principal, color="#4169E1", linewidth=4, linestyle="--", label="投資元金")
    
    plt.title(f"利回り {rate}% での資産推移シミュレーション", fontsize=15, fontname="IPAexGothic" if os.path.exists("font.ttf") else None)
    plt.xlabel("経過年数", fontsize=12)
    plt.ylabel("資産額 (円)", fontsize=12)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    return Image.open(buf)

# --- メイン画面 ---
st.title("📊 FPコンサル用 本格チラシ生成システム")

with st.sidebar:
    st.header("👤 プロフィール設定")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

st.header("📈 運用プラン設定")
rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)

# 計算
monthly = 33000
years = 30
r = (rate / 100) / 12
final_amount = int(monthly * ((1 + r)**(years*12) - 1) / r)
final_amount_man = final_amount // 10000

def create_flyer():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(canvas)
    f = get_font

    # 1. ヘッダー
    draw.rectangle([0, 0, WIDTH, 450], fill=GOLD)
    draw.text((WIDTH//2, 150), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    draw.text((WIDTH//2, 300), "日本人の９割が知らない", font=f(140), fill=WHITE, anchor="mm")

    # 2. メインタイトル
    draw.text((WIDTH//2, 600), "お金の", font=f(300), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 950), "超基本", font=f(550), fill=BLACK, anchor="mm")
    draw.rectangle([WIDTH//2 - 500, 1150, WIDTH//2 + 500, 1170], fill=GOLD)

    # 3. コンセプト説明文
    concept_text = (
        "「iDeCoだけで老後2000万円作ります」がコンセプト！\n"
        "投資の利回りとして年平均7.5%～8%に収まると確信を持ち、\n"
        "FPコンサルをスタートさせました。このグラフは30年間の推移です。"
    )
    draw.multiline_text((WIDTH//2, 1350), concept_text, font=f(75), fill=BLACK, anchor="mm", align="center", spacing=20)

    # 4. グラフの生成と貼り付け
    graph_img = create_graph(rate, monthly).resize((2000, 1200))
    canvas.paste(graph_img, (WIDTH//2 - 1000, 1500))

    # 5. 強調帯
    draw.rectangle([0, 2750, WIDTH, 3050], fill=PINK)
    res_text = f"つみたてだけで老後 {final_amount_man}万円 を作れます！"
    draw.text((WIDTH//2, 2900), res_text, font=f(120), fill=WHITE, anchor="mm")

    # 6. プロフィール
    if user_photo:
        photo = Image.open(user_photo).convert("RGBA").resize((600, 600))
        mask = Image.new("L", (600, 600), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 600, 600), fill=255)
        photo_round = ImageOps.fit(photo, (600, 600), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (150, 2750), photo_round)

    if qr_code:
        qr = Image.open(qr_code).resize((450, 450))
        canvas.paste(qr, (WIDTH - 600, 2800))
        draw.text((WIDTH - 375, 3300), "公式LINEはこちら", font=f(60), fill=BLACK, anchor="mm")

    draw.text((WIDTH//2 + 100, 3150), title, font=f(70), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2 + 100, 3300), f"{name}", font=f(160), fill=BLACK, anchor="mm")

    pdf_buffer = io.BytesIO()
    canvas.save(pdf_buffer, format="PDF", resolution=300.0)
    return pdf_buffer.getvalue()

if st.button("🚀 この内容でチラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("⚠️ 写真とQRコードをアップロードしてください。")
    else:
        with st.spinner("シミュレーショングラフとPDFを生成中..."):
            pdf_data = create_flyer()
            st.success("✅ 全ての要素が反映されたチラシが完成しました！")
            st.download_button(label="📥 ダウンロード", data=pdf_data, file_name=f"FP_Full_{name}.pdf", mime="application/pdf")
