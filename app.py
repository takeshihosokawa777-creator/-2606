import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# --- ページ設定 ---
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

# --- 設定：A4サイズ (300dpi) ---
WIDTH, HEIGHT = 2480, 3508 
WHITE = (255, 255, 255)
GOLD = (184, 134, 11) # 高級感のある色
BLACK = (0, 0, 0)
RED = (200, 0, 0)

# --- フォント読み込みの関数 ---
def get_font(size):
    try:
        # GitHubにアップロードしたフォントファイル名を指定
        return ImageFont.truetype("NotoSansJP-Bold.ttf", size)
    except:
        # フォントがない場合の予備（Streamlit Cloud環境のデフォルト）
        return ImageFont.load_default()

# --- メイン画面 ---
st.title("📄 本格FPチラシPDF作成")
st.write("情報を入力して、高品質なA4チラシを生成します。")

with st.sidebar:
    st.header("👤 プロフィール設定")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真（正方形に近いと綺麗です）", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

st.header("📈 シミュレーション設定")
rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)

# 計算
monthly = 33000
years = 30
r = (rate / 100) / 12
n = years * 12
final_amount = int(monthly * ((1 + r)**n - 1) / r)
final_amount_man = final_amount // 10000

# --- チラシ生成ロジック ---
def create_flyer():
    # 1. ベース作成（白紙）
    canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(canvas)

    # 2. デザイン装飾（ヘッダー部分）
    draw.rectangle([0, 0, WIDTH, 400], fill=GOLD)
    draw.text((100, 100), "日本人の9割が知らない", font=get_font(80), fill=WHITE)
    draw.text((100, 200), "お金の超基本シミュレーション", font=get_font(140), fill=WHITE)

    # 3. メインコンテンツ：金額
    draw.text((WIDTH//2 - 400, 800), "30年後の想定資産額", font=get_font(100), fill=BLACK)
    amount_text = f"約 {final_amount_man:,} 万円"
    draw.text((WIDTH//2 - 500, 1000), amount_text, font=get_font(300), fill=RED)

    # 4. サブ情報
    info_text = f"毎月3.3万円を{rate}%で運用し続けた結果です。"
    draw.text((WIDTH//2 - 450, 1350), info_text, font=get_font(80), fill=BLACK)

    # 5. 写真の加工（丸く切り抜く）
    if user_photo:
        photo_img = Image.open(user_photo).convert("RGBA").resize((600, 600))
        mask = Image.new("L", (600, 600), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 600, 600), fill=255)
        
        photo_round = ImageOps.fit(photo_img, (600, 600), centering=(0.5, 0.5))
        photo_round.putalpha(mask)
        canvas.paste(photo_round, (200, 2500), photo_round)

    # 6. QRコードの配置
    if qr_code:
        qr_img = Image.open(qr_code).resize((400, 400))
        canvas.paste(qr_img, (WIDTH - 600, 2500))
        draw.text((WIDTH - 600, 2920), "公式LINEはこちら", font=get_font(50), fill=BLACK)

    # 7. プロフィールテキスト
    draw.text((850, 2650), f"{title}", font=get_font(60), fill=BLACK)
    draw.text((850, 2750), f"{name}", font=get_font(120), fill=BLACK)

    # 8. フッター
    draw.rectangle([0, HEIGHT-150, WIDTH, HEIGHT], fill=GOLD)

    # PDFとして保存
    pdf_buffer = io.BytesIO()
    canvas.save(pdf_buffer, format="PDF", resolution=300.0)
    return pdf_buffer.getvalue()

# --- 出力セクション ---
st.divider()
if st.button("🚀 この内容でチラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("⚠️ 写真とQRコードをアップロードしてください。")
    else:
        with st.spinner("高品質PDFを生成中..."):
            pdf_data = create_flyer()
            st.success("✅ チラシが完成しました！下のボタンからダウンロードしてください。")
            st.download_button(
                label="📥 A4チラシPDFをダウンロード",
                data=pdf_data,
                file_name=f"FPチラシ_{name}.pdf",
                mime="application/pdf"
            )
