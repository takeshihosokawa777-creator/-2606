import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import urllib.request

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi相当) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE = (255, 255, 255)
GOLD = (184, 134, 11) 
BLACK = (30, 30, 30)
RED = (220, 0, 0)
PINK = (255, 0, 127)

# --- フォントを強制的に準備する関数 ---
def get_font(size):
    font_filename = "font.ttf"
    # 日本語フォント（IPAexゴシック）のダウンロードURL（軽量で確実なもの）
    url = "https://github.com/googlefonts/ipafont/raw/main/fonts/ipaexg.ttf"
    
    if not os.path.exists(font_filename):
        try:
            with st.spinner("初回のみ日本語フォントをダウンロード中..."):
                urllib.request.urlretrieve(url, font_filename)
        except Exception as e:
            st.error(f"フォントのダウンロードに失敗しました: {e}")
            return ImageFont.load_default()
    
    try:
        return ImageFont.truetype(font_filename, size)
    except Exception as e:
        st.error(f"フォントの読み込みに失敗しました: {e}")
        return ImageFont.load_default()

# --- メイン画面 ---
st.title("🚀 本格FPチラシ自動生成システム")
st.info("文字が点になる問題を解決した最新版です。")

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

    # 1. ヘッダー
    draw.rectangle([0, 0, WIDTH, 500], fill=GOLD)
    draw.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=get_font(100), fill=WHITE, anchor="mm")
    draw.text((WIDTH//2, 350), "日本人の９割が知らない", font=get_font(160), fill=WHITE, anchor="mm")

    # 2. タイトル
    draw.text((WIDTH//2, 850), "お金の", font=get_font(400), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 1300), "超基本", font=get_font(700), fill=BLACK, anchor="mm")
    draw.rectangle([WIDTH//2 - 600, 1550, WIDTH//2 + 600, 1580], fill=GOLD)

    # 3. ピンク帯
    draw.rectangle([0, 1750, WIDTH, 2100], fill=PINK)
    catch_text = f"つみたてだけで老後 {final_amount_man}万円 を作ります！"
    draw.text((WIDTH//2, 1925), catch_text, font=get_font(135), fill=WHITE, anchor="mm")

    # 4. シミュレーション
    draw.text((WIDTH//2, 2250), "【シミュレーション結果】", font=get_font(110), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2430), f"毎月3.3万円を {rate}% で30年間運用", font=get_font(95), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2750), f"資産額：約 {final_amount_man:,} 万円", font=get_font(300), fill=RED, anchor="mm")

    # 5. プロフィール（写真を少し大きく）
    if user_photo:
        photo = Image.open(user_photo).convert("RGBA").resize((750, 750))
        mask = Image.new("L", (750, 750), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 750, 750), fill=255)
        photo_round = ImageOps.fit(photo, (750, 750), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (200, 2600), photo_round)

    # QRコード
    if qr_code:
        qr = Image.open(qr_code).resize((550, 550))
        canvas.paste(qr, (WIDTH - 800, 2700))
        draw.text((WIDTH - 525, 3300), "公式LINEはこちら", font=get_font(75), fill=BLACK, anchor="mm")

    # 名前と肩書き（位置調整）
    draw.text((WIDTH//2 + 150, 2980), title, font=get_font(85), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2 + 150, 3180), f"{name}", font=get_font(180), fill=BLACK, anchor="mm")

    # 6. フッター
    draw.rectangle([0, HEIGHT-120, WIDTH, HEIGHT], fill=GOLD)

    pdf_buffer = io.BytesIO()
    canvas.save(pdf_buffer, format="PDF", resolution=300.0)
    return pdf_buffer.getvalue()

# --- ボタン ---
if st.button("🚀 この内容でチラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("⚠️ 写真とQRコードをアップロードしてください。")
    else:
        with st.spinner("高品質PDFを生成中...（初回はフォント取得のため時間がかかります）"):
            pdf_data = create_flyer()
            st.success("✅ チラシが完成しました！ダウンロードしてください。")
            st.download_button(
                label="📥 A4チラシPDFをダウンロード",
                data=pdf_data,
                file_name=f"FPチラシ_{name}.pdf",
                mime="application/pdf"
            )
