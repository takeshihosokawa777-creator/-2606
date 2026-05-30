import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# ページの設定
st.set_page_config(page_title="FPチラシ作成システム", layout="centered")

st.title("📄 FP相談用 チラシ自動生成ツール")
st.write("情報を入力するだけで、あなた専用のA4チラシPDFが完成します。")

# 入力セクション
st.sidebar.header("👤 あなたの情報")
name = st.sidebar.text_input("お名前", "山田 太郎")
company = st.sidebar.text_input("会社名・肩書き", "ファイナンシャルプランナー")
user_photo = st.sidebar.file_uploader("あなたの写真をアップ", type=['jpg', 'png'])
qr_code = st.sidebar.file_uploader("LINEのQRをアップ", type=['jpg', 'png'])

st.header("📈 運用プラン設定")
rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)

# 計算ロジック（毎月3.3万円、30年）
monthly = 33000
years = 30
r = (rate / 100) / 12
n = years * 12
final_amount = int(monthly * ((1 + r)**n - 1) / r)

# プレビュー表示
st.divider()
st.subheader("💡 チラシに掲載される内容")
col1, col2 = st.columns(2)
with col1:
    st.metric("30年後の想定資産額", f"約 {final_amount // 10000:,} 万円")
    st.write(f"（元金合計: 1,188万円 / 運用益: {(final_amount - 11880000)//10000:,}万円）")
with col2:
    st.write(f"**担当:** {name}")
    st.write(f"**メッセージ:** 利回り{rate}%で運用した場合の奇跡を伝えましょう。")

# PDF生成（簡易シミュレーション画像）
def generate_pdf():
    # 本来はここで綺麗なデザイン画像と合成します
    # ここでは「作成完了」の合図としてプレースホルダーを表示
    st.balloons()
    st.success("✅ A4チラシPDFの生成準備が整いました！")
    st.info("※実際の運用では、ここにプロのデザイン背景を合成したPDFが表示されます。")
    
    # ダミーのダウンロードボタン
    st.download_button("📥 チラシPDFをダウンロード", "dummy content", file_name="flyer.pdf")

if st.button("🚀 この内容でチラシを完成させる"):
    if not user_photo or not qr_code:
        st.warning("⚠️ 写真とQRコードをアップロードしてください。")
    else:
        generate_pdf()
