import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import urllib.request

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ ---
WIDTH, HEIGHT = 2480, 3508 
WHITE, GOLD, BLACK, RED, PINK = (255, 255, 255), (184, 134, 11), (30, 30, 30), (220, 0, 0), (255, 0, 127)

# --- フォントを自動で準備する関数 ---
@st.cache_resource
def get_font_path():
    # Streamlit Cloud上で確実に動く日本語フォントのパス
    font_filename = "NotoSansJP-Bold.ttf"
    # もしファイルがない、または壊れている場合に備えて自動ダウンロード
    if not os.path.exists(font_filename) or os.path.getsize(font_filename) < 1000:
        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/OTC/NotoSansCJKjp-Bold.otf"
        try:
            with st.spinner("初回起動のためフォントを準備しています（数十秒かかります）..."):
                urllib.request.urlretrieve(url, font_filename)
        except:
            return None # 失敗した場合はNoneを返す
    return font_filename

def get_font(size):
    path = get_font_path()
    try:
        if path:
            return ImageFont.truetype(path, size)
    except:
        pass
    return ImageFont.load_default()

# --- メイン画面 ---
st.title("🚀 本格FPチラシ自動生成システム")

with st.sidebar:
    st.header("👤 プロフィール設定")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

st.header("📈 シミュレーション設定")
rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)

# 資産計算
monthly, years = 33000, 30
r = (rate / 100) / 12
n = years * 12
final_amount_man = int(monthly * ((1 + r)**n - 1) / r) // 10000

def create_flyer():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(canvas)
    f = get_font

    # 1. ヘッダー
    draw.rectangle([0, 0, WIDTH, 500], fill=GOLD)
    draw.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    draw.text((WIDTH//2, 350), "日本人の９割が知らない", font=f(160), fill=WHITE, anchor="mm")

    # 2. タイトル
    draw.text((WIDTH//2, 800), "お金の", font=f(380), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 1250), "超基本", font=f(650), fill=BLACK, anchor="mm")
    draw.rectangle([WIDTH//2 - 600, 1500, WIDTH//2 + 600, 1530], fill=GOLD)

    # 3. ピンク帯
    draw.rectangle([0, 1700, WIDTH, 2050], fill=PINK)
    draw.text((WIDTH//2, 1875), f"つみたてだけで老後 {final_amount_man}万円 を作ります！", font=f(130), fill=WHITE, anchor="mm")

    # 4. シミュレーション
    draw.text((WIDTH//2, 2200), "【シミュレーション結果】", font=f(110), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2380), f"毎月3.3万円を {rate}% で30年間運用", font=f(90), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2650), f"資産額：約 {final_amount_man:,} 万円", font=f(280), fill=RED, anchor="mm")

    # 5. プロフィール
    if user_photo:
        photo = Image.open(user_photo).convert("RGBA").resize((700, 700))
        mask = Image.new("L", (700, 700), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 700, 700), fill=255)
        photo_round = ImageOps.fit(photo, (700, 700), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (250, 2650), photo_round)

    if qr_code:
        qr = Image.open(qr_code).resize((500, 500))
        canvas.paste(qr, (WIDTH - 750, 2700))
        draw.text((WIDTH - 500, 3250), "公式LINEはこちら", font=f(70), fill=BLACK, anchor="mm")

    draw.text((WIDTH//2 + 100, 2950), title, font=f(80), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2 + 100, 3150), f"{name}", font=f(160), fill=BLACK, anchor="mm")

    draw.rectangle([0, HEIGHT-120, WIDTH, HEIGHT], fill=GOLD)

    pdf_buffer = io.BytesIO()
    canvas.save(pdf_buffer, format="PDF", resolution=300.0)
    return pdf_buffer.getvalue()

if st.button("🚀 この内容でチラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("⚠️ 写真とQRコードをアップロードしてください。")
    else:
        with st.spinner("プロ級PDFを生成中..."):
            pdf_data = create_flyer()
            st.success("✅ 完成しました！")
            st.download_button(label="📥 ダウンロード", data=pdf_data, file_name=f"FP_{name}.pdf", mime="application/pdf")
