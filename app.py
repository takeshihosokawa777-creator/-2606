import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE = (255, 255, 255)
GOLD = (184, 134, 11) 
BLACK = (30, 30, 30)
RED = (220, 0, 0)
PINK = (255, 0, 127)

# --- フォント読み込み（ここを強化しました） ---
def get_font(size):
    # GitHub上のファイル名を指定（大文字小文字に注意！）
    font_path = "NotoSansJP-Bold.ttf" 
    
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    else:
        # ファイルが見つからない場合、画面に警告を出して標準フォントを巨大化して返す
        st.error(f"フォントファイル '{font_path}' が見つかりません。GitHubにアップロードされているか確認してください。")
        return ImageFont.load_default()

# --- メイン画面 ---
st.title("🚀 本格FPチラシ自動生成（最終調整版）")

with st.sidebar:
    st.header("👤 プロフィール設定")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

st.header("📈 シミュレーション設定")
rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)

# 計算ロジック
monthly = 33000
years = 30
r = (rate / 100) / 12
n = years * 12
final_amount = int(monthly * ((1 + r)**n - 1) / r)
final_amount_man = final_amount // 10000

def create_flyer():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(canvas)

    # 1. ヘッダー
    draw.rectangle([0, 0, WIDTH, 500], fill=GOLD)
    draw.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=get_font(100), fill=WHITE, anchor="mm")
    draw.text((WIDTH//2, 350), "日本人の９割が知らない", font=get_font(160), fill=WHITE, anchor="mm")

    # 2. メインタイトル（サイズを調整）
    draw.text((WIDTH//2, 800), "お金の", font=get_font(380), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 1250), "超基本", font=get_font(650), fill=BLACK, anchor="mm")
    draw.rectangle([WIDTH//2 - 600, 1500, WIDTH//2 + 600, 1530], fill=GOLD)

    # 3. インパクトセクション（ピンク帯）
    draw.rectangle([0, 1700, WIDTH, 2050], fill=PINK)
    catch_text = f"つみたてだけで老後 {final_amount_man}万円 を作ります！"
    draw.text((WIDTH//2, 1875), catch_text, font=get_font(130), fill=WHITE, anchor="mm")

    # 4. シミュレーション詳細（さらに大きく）
    draw.text((WIDTH//2, 2200), f"【シミュレーション結果】", font=get_font(110), fill=BLACK, anchor="mm")
    res_text = f"毎月3.3万円を {rate}% で30年間運用"
    draw.text((WIDTH//2, 2380), res_text, font=get_font(90), fill=BLACK, anchor="mm")
    
    amount_text = f"資産額：約 {final_amount_man:,} 万円"
    draw.text((WIDTH//2, 2650), amount_text, font=get_font(280), fill=RED, anchor="mm")

    # 5. 写真とプロフィール（位置を微調整）
    if user_photo:
        photo_img = Image.open(user_photo).convert("RGBA").resize((700, 700))
        mask = Image.new("L", (700, 700), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 700, 700), fill=255)
        photo_round = ImageOps.fit(photo_img, (700, 700), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (250, 2650), photo_round)

    # QRコード
    if qr_code:
        qr_img = Image.open(qr_code).resize((500, 500))
        canvas.paste(qr_img, (WIDTH - 750, 2700))
        draw.text((WIDTH - 500, 3250), "公式LINEはこちら", font=get_font(70), fill=BLACK, anchor="mm")

    # 名前
    draw.text((WIDTH//2 + 100, 2950), title, font=get_font(80), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2 + 100, 3150), f"{name}", font=get_font(160), fill=BLACK, anchor="mm")

    # 6. フッター
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
            st.success("✅ チラシが完成しました！")
            st.download_button(
                label="📥 A4チラシPDFをダウンロード",
                data=pdf_data,
                file_name=f"FPチラシ_{name}.pdf",
                mime="application/pdf"
            )
