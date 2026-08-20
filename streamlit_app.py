import streamlit as st
import pandas as pd

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Mermaid Vũng Tàu Guide",
    page_icon="🧜",
    layout="centered"
)

# =========================
# ĐỌC DỮ LIỆU
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("mermaid_vungtau.xlsx")

    df["ten"] = df["ten"].fillna("").astype(str)
    df["nhom"] = df["nhom"].fillna("Khác").astype(str)

    df["khoang_cach_km"] = pd.to_numeric(
        df["khoang_cach_km"],
        errors="coerce"
    )

    return df

df = load_data()

# =========================
# TIÊU ĐỀ
# =========================
st.title("🧜 Mermaid Vũng Tàu Guide")

st.markdown(
    """
    **Trợ lý khám phá Vũng Tàu dành cho khách lưu trú
    tại Mermaid Seaside Hotel.**

    Hãy chọn loại trải nghiệm và khoảng cách mong muốn.
    """
)

st.info(
    "📍 Điểm xuất phát: Mermaid Seaside Hotel, Vũng Tàu"
)

st.caption(
    "Khoảng cách được tính theo tọa độ và mang tính ước tính."
)

# =========================
# CHỌN NHÓM
# =========================
st.subheader("🔎 Bạn muốn trải nghiệm gì?")

groups = sorted(
    [
        x for x in df["nhom"].dropna().unique()
        if str(x).strip() != ""
    ]
)

category = st.selectbox(
    "Chọn loại địa điểm",
    groups
)

# =========================
# CHỌN KHOẢNG CÁCH
# =========================
distance = st.slider(
    "Khoảng cách tối đa từ khách sạn",
    min_value=1,
    max_value=15,
    value=5,
    step=1,
    format="%d km"
)

# =========================
# TÌM THEO TÊN
# =========================
keyword = st.text_input(
    "Tìm theo tên địa điểm (không bắt buộc)",
    placeholder="Nhập tên địa điểm..."
)

# =========================
# LỌC DỮ LIỆU
# =========================
result = df[
    (df["nhom"] == category)
    &
    (df["khoang_cach_km"] <= distance)
].copy()

if keyword.strip():
    result = result[
        result["ten"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

result = result.sort_values(
    "khoang_cach_km"
)

# =========================
# HIỂN THỊ KẾT QUẢ
# =========================
st.markdown("---")

st.subheader(
    f"📌 Tìm thấy {len(result)} địa điểm"
)

if len(result) == 0:

    st.warning(
        "Chưa tìm thấy địa điểm phù hợp. "
        "Hãy tăng khoảng cách hoặc chọn loại địa điểm khác."
    )

else:

    for _, row in result.head(50).iterrows():

        st.markdown(
            f"### {row['ten']}"
        )

        st.write(
            f"📍 Cách Mermaid khoảng "
            f"**{row['khoang_cach_km']} km**"
        )

        # Địa chỉ
        dia_chi = row.get("dia_chi")

        if pd.notna(dia_chi):
            dia_chi = str(dia_chi).strip()

            if dia_chi:
                st.write(
                    f"🏠 {dia_chi}"
                )

        # Giờ mở cửa
        opening = row.get("opening_hours")

        if pd.notna(opening):
            opening = str(opening).strip()

            if opening:
                st.write(
                    f"🕒 {opening}"
                )

        # Điện thoại
        phone = row.get("dien_thoai")

        if pd.notna(phone):
            phone = str(phone).strip()

            if phone:
                st.write(
                    f"☎️ {phone}"
                )

        # Website
        website = row.get("website")

        if pd.notna(website):
            website = str(website).strip()

            if website.startswith("http"):
                st.link_button(
                    "🌐 Website",
                    website
                )

        # Bản đồ
        map_url = row.get("ban_do")

        if pd.notna(map_url):
            map_url = str(map_url).strip()

            if map_url.startswith("http"):
                st.link_button(
                    "🗺️ Xem bản đồ",
                    map_url
                )

        st.markdown("---")

# =========================
# CHÂN TRANG
# =========================
st.caption(
    "Dữ liệu địa điểm: © OpenStreetMap contributors."
)

st.caption(
    "Mermaid Vũng Tàu Guide - Phiên bản thử nghiệm."
)
