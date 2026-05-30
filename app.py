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
MARGIN = 200 # 左右の安全マージン
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

# --- グラフ作成関数 (金額ラベル付き) ---
def create_graph(rate, monthly):
    font_path = load_font_path()
    prop = fm.FontProperties(fname=font_path) if font_path else None
    
    plt.figure(figsize=(11, 7), dpi=150)
    months = np.arange(30 * 12 + 1)
    r = (rate / 100) / 12
    principal_val = monthly * (30 * 12)
    assets_series = monthly * ((1 + r)**months - 1) / r if r > 0 else monthly * months
    final_assets = assets_series[-1]
    
    plt.fill_between(months/12, assets_series, color="#FFD700", alpha=0.3, label="運用収益")
    plt.plot(months/12, assets_series, color="#FF4500", linewidth=7, label="資産合計")
    plt.plot(months/12, [monthly * m for m in months], color="#4169E1", linewidth=4, linestyle="--", label="投資元金")
    
    # グラフ上に最終金額を表示（吹き出し）
    plt.annotate(f'資産合計\n{int(final_assets//10000):,}万円', xy=(30, final_assets), xytext=(22, final_assets*0.8),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontproperties=prop, fontsize=14, weight='bold')
    plt.annotate(f'投資元金\n{int(principal_val//10000):,}万円', xy=(30, principal_val), xytext=(22, principal_val*0.4),
                 arrowprops=dict(facecolor='blue', shrink=0.05), fontproperties=prop, fontsize=14)

    plt.title(f"30年間の利回り {rate}% シミュレーション", fontsize=18, fontproperties=prop)
    plt.xlabel("経過年数 (年)", fontsize=14, fontproperties=prop)
    plt.ylabel("資産額 (円)", fontsize=14, fontproperties=prop)
    plt.grid(True, linestyle=":", alpha=0.6)
    if prop: plt.legend(prop=prop, loc="upper left", fontsize=12)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    return Image.open(buf)

# --- メイン画面 ---
st.title("📄 細川様モデル：FP A4両面チラシ生成システム")

with st.sidebar:
    st.header("👤 掲載情報")
    name = st.text_input("お名前", "細川 豪")
    title = st.text_input("肩書き", "ファイナンシャルプランナー")
    user_photo = st.file_uploader("顔写真", type=['jpg', 'png'])
    qr_code = st.file_uploader("LINE QRコード", type=['jpg', 'png'])

rate = st.select_slider("想定利回り (%)", options=[7.5, 8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0], value=7.5)
final_amount_man = int(33000 * (((rate/100/12) + 1)**360 - 1) / (rate/100/12)) // 10000

def create_pages():
    f = get_font
    
    # --- PAGE 1 (表面) ---
    p1 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d1 = ImageDraw.Draw(p1)
    
    d1.rectangle([0, 0, WIDTH, 450], fill=GOLD)
    d1.text((WIDTH//2, 180), "節約・貯蓄・NISA・投資・保険", font=f(100), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 330), "日本人の９割が知らない", font=f(150), fill=WHITE, anchor="mm")
    d1.text((WIDTH//2, 700), "お金の超基本", font=f(450), fill=BLACK, anchor="mm")
    
    # グラフ配置
    graph = create_graph(rate, 33000).resize((2200, 1350))
    p1.paste(graph, (WIDTH//2 - 1100, 950))
    
    # 細川様のエピソード (1P中央)
    hosokawa_txt = "私、細川の運用実績が7.5%であり、最終的に利回りは7.5%に収斂するという確信を得たことで、\nこのコンサルティングサービスをスタートさせました。"
    d1.multiline_text((WIDTH//2, 2450), hosokawa_txt, font=f(75), fill=BLACK, anchor="mm", align="center", spacing=20)

    d1.rectangle([0, 2650, WIDTH, 3050], fill=PINK)
    d1.text((WIDTH//2, 2850), f"つみたてだけで老後 {final_amount_man}万円 を作れます！", font=f(125), fill=WHITE, anchor="mm")
    
    txt_footer = "「iDeCoだけで老後2000万円作る」をコンセプトに、\n国の制度を最大限に活用した資産形成をお伝えしています。"
    d1.multiline_text((WIDTH//2, 3250), txt_footer, font=f(85), fill=BLACK, anchor="mm", align="center", spacing=30)

    # --- PAGE 2 (裏面) ---
    p2 = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    d2 = ImageDraw.Draw(p2)
    d2.text((WIDTH//2, 250), "なぜ今、資産形成が必要なのか？", font=f(120), fill=GOLD, anchor="mm")
    
    story = (
        "過去20年間を振り返れば、ITバブル崩壊、リーマンショック、東日本大震災、そしてコロナショックと、\n"
        "世界経済を揺るがす暴落が何度も繰り返されてきました。しかし、長期投資はそれらを乗り越える力があります。\n\n"
        "私（細川）は自らの運用実績を通じ、長期的な利回りが7.5%へと収斂していく事実を目の当たりにしました。\n"
        "この実体験に基づいた確信こそが、自信を持って皆様にこのサービスをお届けする原動力となっています。\n\n"
        "2019年の「老後2000万円問題」以降、年金プラスアルファの準備は必須となりました。\n"
        "これぞ複利の効果であり、「複利が起こす奇跡の価値」と呼ばれるものです。\n\n"
        "正しいつみたてを知り、新NISAやiDeCoといった国の制度を賢く活用することで、\n"
        "大切なお金を守り、育て、家族が安心して暮らせる未来を共に作っていきましょう。"
    )
    d2.multiline_text((MARGIN, 500), story, font=f(85), fill=BLACK, spacing=55)

    # プロフィールエリア
    d2.rectangle([0, 2450, WIDTH, HEIGHT], fill=(248, 248, 248))
    
    if user_photo:
        photo = ImageOps.fit(Image.open(user_photo).convert("RGBA"), (750, 750), centering=(0.5, 0.5))
        mask = Image.new("L", (750, 750), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 750, 750), fill=255)
        photo.putalpha(mask)
        p2.paste(photo, (MARGIN, 2550), photo)
    
    # プロフィールテキスト（写真の右に配置）
    d2.text((1050, 2750), title, font=f(85), fill=BLACK)
    d2.text((1050, 2950), f"{name}", font=f(180), fill=BLACK)
    
    if qr_code:
        qr = Image.open(qr_code).resize((550, 550))
        p2.paste(qr, (WIDTH - MARGIN - 550, 2600))
        d2.text((WIDTH - MARGIN - 275, 3250), "公式LINEはこちら", font=f(70), fill=BLACK, anchor="mm")

    pdf_buf = io.BytesIO()
    p1.save(pdf_buf, format="PDF", save_all=True, append_images=[p2], resolution=300.0)
    return pdf_buf.getvalue()

if st.button("🚀 細川様モデル：A4両面チラシを生成する"):
    if not user_photo or not qr_code:
        st.warning("写真とQRコードをアップロードしてください。")
    else:
        with st.spinner("高品質な両面PDFを生成中..."):
            pdf = create_pages()
            st.success("✅ 細川様オリジナルチラシが完成しました！")
            st.download_button("📥 両面PDFをダウンロード", pdf, f"FP_Hosokawa_Report.pdf", "application/pdf")
