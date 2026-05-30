import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import requests

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi相当) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE, GOLD, BLACK, RED, PINK = (255, 255, 255), (184, 134, 11), (30, 30, 30), (220, 0, 0), (255, 0, 127)

# --- フォントを確実に準備する関数（軽量版に変更） ---
@st.cache_resource
def load_font():
    font_filename = "font_bold.ttf"
    # 日本語フォント（より確実に落とせるURLに変更）
    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/OTC/NotoSansCJKjp-Bold.otf"
    
    if not os.path.exists(font_filename):
        try:
            response = requests.get(font_url, timeout=30)
            with open(font_filename, "wb") as f:
                f.write(response.content)
        except:
            return None
    return font_filename

def get_font(size):
    path = load_font()
    try:
        if path: return ImageFont.truetype(path, size)
    except: pass
    return ImageFont.load_default()

# --- メイン画面 ---
st.title("🚀 FPチラシ自動生成システム【レイアウト修正版】")

with st.sidebar:
    st.header("👤 プロフィール設定")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

st.header("📈 シミュレーション設定")
rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)

# 計算（毎月3.3万円、30年）
monthly, years = 33000, 30
r = (rate / 100) / 12
n = years * 12
final_amount_man = int(monthly * ((1 + r)**n - 1) / r) // 10000

def create_flyer():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(canvas)
    f = get_font

    # 1. ヘッダー（上部500px）
    draw.rectangle([0, 0, WIDTH, 500], fill=GOLD)
    draw.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    draw.text((WIDTH//2, 350), "日本人の９割が知らない", font=f(160), fill=WHITE, anchor="mm")

    # 2. タイトル（位置を少し上げました）
    draw.text((WIDTH//2, 750), "お金の", font=f(350), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 1150), "超基本", font=f(600), fill=BLACK, anchor="mm")
    draw.rectangle([WIDTH//2 - 550, 1400, WIDTH//2 + 550, 1425], fill=GOLD)

    # 3. ピンク帯（「つ」が切れないよう位置調整）
    draw.rectangle([0, 1600, WIDTH, 1950], fill=PINK)
    catch_text = f"つみたてだけで老後 {final_amount_man}万円 を作ります！"
    draw.text((WIDTH//2, 1775), catch_text, font=f(130), fill=WHITE, anchor="mm")

    # 4. シミュレーション結果（重ならないよう上に配置）
    draw.text((WIDTH//2, 2100), "【シミュレーション結果】", font=f(100), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2250), f"毎月3.3万円を {rate}% で30年間運用", font=f(90), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2500), f"資産額：約 {final_amount_man:,} 万円", font=f(280), fill=RED, anchor="mm")

    # 5. プロフィールエリア（下部に集約）
    # 写真（左下）
    if user_photo:
        photo = Image.open(user_photo).convert("RGBA").resize((650, 650))
        mask = Image.new("L", (650, 650), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 650, 650), fill=255)
        photo_round = ImageOps.fit(photo, (650, 650), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (200, 2750), photo_round)

    # QRコード（右下）
    if qr_code:
        qr = Image.open(qr_code).resize((500, 500))
        canvas.paste(qr, (WIDTH - 700, 2800))
        draw.text((WIDTH - 450, 3350), "公式LINEはこちら", font=f(70), fill=BLACK, anchor="mm")

    # 名前・肩書き（中央下）
    draw.text((WIDTH//2 + 100, 3050), title, font=f(75), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2 + 100, 3250), f"{name}", font=f(180), fill=BLACK, anchor="mm")

    # 6. フッター
    draw.rectangle([0, HEIGHT-100, WIDTH, HEIGHT], fill=GOLD)

    pdf_buffer = io.BytesIO()
    canvas.save(pdf_buffer, format="PDF", resolution=300.0)
    return pdf_buffer.getvalue()

# --- 実行 ---
if st.button("🚀 この内容でチラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("⚠️ 写真とQRコードをアップロードしてください。")
    else:
        with st.spinner("高品質PDFを生成中..."):
            pdf_data = create_flyer()
            st.success("✅ 完成！ダウンロードしてください。")
            st.download_button(label="📥 ダウンロード", data=pdf_data, file_name=f"FP_{name}.pdf", mime="application/pdf")
