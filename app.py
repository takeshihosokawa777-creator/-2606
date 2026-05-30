import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE = (255, 255, 255)
GOLD = (184, 134, 11) 
DARK_GOLD = (140, 100, 0)
BLACK = (30, 30, 30)
RED = (220, 0, 0)

# --- フォント読み込みの関数 ---
def get_font(size):
    try:
        # GitHubにアップロードしたNotoSansJP-Bold.ttfを読み込む
        return ImageFont.truetype("NotoSansJP-Bold.ttf", size)
    except:
        # フォントがない場合は標準フォントを大きくして返す
        return ImageFont.load_default()

# --- メイン画面 ---
st.title("🚀 本格FPチラシ自動生成（改良版）")

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

    # 1. ヘッダー（金色の帯）
    draw.rectangle([0, 0, WIDTH, 500], fill=GOLD)
    # anchor="mm" は中央揃えを意味します
    draw.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=get_font(100), fill=WHITE, anchor="mm")
    draw.text((WIDTH//2, 350), "日本人の９割が知らない", font=get_font(160), fill=WHITE, anchor="mm")

    # 2. メインタイトル
    draw.text((WIDTH//2, 750), "お金の", font=get_font(350), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 1150), "超基本", font=get_font(600), fill=BLACK, anchor="mm")
    
    # 金色の下線
    draw.rectangle([WIDTH//2 - 500, 1400, WIDTH//2 + 500, 1420], fill=GOLD)

    # 3. インパクトセクション（赤い帯）
    draw.rectangle([0, 1600, WIDTH, 1950], fill=(255, 0, 127)) # 鮮やかなピンクレッド
    catch_text = f"つみたてだけで老後 {final_amount_man}万円 を作ります！"
    draw.text((WIDTH//2, 1775), catch_text, font=get_font(120), fill=WHITE, anchor="mm")

    # 4. シミュレーション詳細
    draw.text((WIDTH//2, 2150), f"【シミュレーション結果】", font=get_font(100), fill=BLACK, anchor="mm")
    res_text = f"毎月3.3万円を {rate}% で30年間運用"
    draw.text((WIDTH//2, 2300), res_text, font=get_font(80), fill=BLACK, anchor="mm")
    
    amount_text = f"資産額：約 {final_amount_man:,} 万円"
    draw.text((WIDTH//2, 2550), amount_text, font=get_font(250), fill=RED, anchor="mm")

    # 5. プロフィールエリア
    # 写真（丸く切り抜いて左下に配置）
    if user_photo:
        photo_img = Image.open(user_photo).convert("RGBA").resize((600, 600))
        mask = Image.new("L", (600, 600), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 600, 600), fill=255)
        photo_round = ImageOps.fit(photo_img, (600, 600), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (250, 2750), photo_round)

    # QRコード（右下に配置）
    if qr_code:
        qr_img = Image.open(qr_code).resize((450, 450))
        canvas.paste(qr_img, (WIDTH - 700, 2800))
        draw.text((WIDTH - 475, 3300), "公式LINEはこちら", font=get_font(60), fill=BLACK, anchor="mm")

    # 名前と肩書き（中央下部）
    draw.text((WIDTH//2, 2900), title, font=get_font(70), fill=BLACK, anchor="mm")
    draw.text((WIDTH//2, 3100), f"{name}", font=get_font(150), fill=BLACK, anchor="mm")

    # 6. フッター
    draw.rectangle([0, HEIGHT-100, WIDTH, HEIGHT], fill=GOLD)

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
            st.download_button(
                label="📥 A4チラシPDFをダウンロード",
                data=pdf_data,
                file_name=f"FPチラシ_{name}.pdf",
                mime="application/pdf"
            )
