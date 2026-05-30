import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import requests

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi相当) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE = (255, 255, 255)
GOLD = (184, 134, 11) 
BLACK = (30, 30, 30)
RED = (220, 0, 0)
PINK = (255, 0, 127)

# --- フォントを確実に準備する関数 ---
@st.cache_resource
def load_japanese_font():
    font_filename = "NotoSansJP-Bold.ttf"
    # Google公式の信頼できるダウンロード先
    font_url = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
    
    if not os.path.exists(font_filename):
        try:
            with st.spinner("初回のみ日本語フォントを準備しています（30秒ほど）..."):
                response = requests.get(font_url)
                with open(font_filename, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            st.error(f"フォントのダウンロードに失敗しました: {e}")
            return None
    return font_filename

def get_font(size):
    path = load_japanese_font()
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception as e:
            st.error(f"フォントの読み込みエラー: {e}")
    # 失敗した時の最後の手段（非常に小さくなりますがエラーは防ぎます）
    return ImageFont.load_default()

# --- メイン画面 ---
st.title("🚀 本格FPチラシ自動生成システム")
st.success("【改良版】文字化け・サイズの問題を修正しました。")

# フォントが正しく読み込めているかチェック
if not os.path.exists("NotoSansJP-Bold.ttf"):
    st.warning("現在フォントを準備中です。一度『完成させる』ボタンを押すとダウンロードが始まります。")

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

    # 2. タイトル（圧倒的に大きく！）
    draw.text((WIDTH//2, 850), "お金の", font=get_font(420), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 1350), "超基本", font=get_font(750), fill=BLACK, anchor="mm")
    draw.rectangle([WIDTH//2 - 600, 1600, WIDTH//2 + 600, 1630], fill=GOLD)

    # 3. ピンク帯
    draw.rectangle([0, 1800, WIDTH, 2150], fill=PINK)
    catch_text = f"つみたてだけで老後 {final_amount_man}万円 を作ります！"
    draw.text((WIDTH//2, 1975), catch_text, font=get_font(140), fill=WHITE, anchor="mm")

    # 4. シミュレーション
    draw.text((WIDTH//2, 2300), "【シミュレーション結果】", font=get_font(110), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2480), f"毎月3.3万円を {rate}% で30年間運用", font=get_font(95), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 2800), f"資産額：約 {final_amount_man:,} 万円", font=get_font(320), fill=RED, anchor="mm")

    # 5. 写真とプロフィール
    if user_photo:
        photo = Image.open(user_photo).convert("RGBA").resize((750, 750))
        mask = Image.new("L", (750, 750), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 750, 750), fill=255)
        photo_round = ImageOps.fit(photo, (750, 750), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (250, 2650), photo_round)

    if qr_code:
        qr = Image.open(qr_code).resize((550, 550))
        canvas.paste(qr, (WIDTH - 800, 2750))
        draw.text((WIDTH - 525, 3350), "公式LINEはこちら", font=get_font(75), fill=BLACK, anchor="mm")

    # 名前と肩書き（中央右寄り）
    draw.text((WIDTH//2 + 150, 3050), title, font=get_font(85), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2 + 150, 3250), f"{name}", font=get_font(200), fill=BLACK, anchor="mm")

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
        with st.spinner("PDFを生成中..."):
            pdf_data = create_flyer()
            st.success("✅ チラシが完成しました！")
            st.download_button(
                label="📥 A4チラシPDFをダウンロード",
                data=pdf_data,
                file_name=f"FPチラシ_{name}.pdf",
                mime="application/pdf"
            )
