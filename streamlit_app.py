import streamlit as st
import pandas as pd
from openai import OpenAI

# ==================================================
# CẤU HÌNH TRANG
# ==================================================

st.set_page_config(
    page_title="Mermaid AI Concierge",
    page_icon="🧜",
    layout="centered"
)

# ==================================================
# ĐỌC DỮ LIỆU
# ==================================================

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

# ==================================================
# KẾT NỐI OPENAI
# ==================================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ==================================================
# GIAO DIỆN
# ==================================================

st.title("🧜 Mermaid AI Concierge")

st.markdown(
    """
    **Trợ lý AI dành cho khách lưu trú tại Mermaid Seaside Hotel Vũng Tàu.**

    Bạn có thể hỏi:

    - Gia đình tôi có 2 trẻ em, chiều nay nên đi đâu?
    - Tôi muốn ăn hải sản gần khách sạn.
    - Có quán café nào gần Mermaid không?
    - Tôi muốn đi biển và ngắm cảnh.
    - Lập lịch trình 4 giờ tại Vũng Tàu.
    """
)

st.info(
    "📍 Điểm xuất phát mặc định: Mermaid Seaside Hotel."
)

# ==================================================
# HÀM CHỌN ĐỊA ĐIỂM
# ==================================================

def lay_dia_diem_phu_hop(question, max_places=12):

    q = question.lower()
    data = df.copy()

    groups = []

    # Ăn uống
    if any(
        x in q
        for x in [
            "ăn",
            "nhà hàng",
            "hải sản",
            "quán ăn",
            "ẩm thực"
        ]
    ):
        groups += [
            "Nhà hàng",
            "Ăn nhanh"
        ]

    # Cafe
    if any(
        x in q
        for x in [
            "cafe",
            "cà phê",
            "coffee"
        ]
    ):
        groups.append("Café")

    # Biển
    if any(
        x in q
        for x in [
            "biển",
            "tắm biển"
        ]
    ):
        groups.append("Bãi biển")

    # Tham quan
    if any(
        x in q
        for x in [
            "tham quan",
            "du lịch",
            "đi chơi",
            "địa điểm"
        ]
    ):
        groups += [
            "Điểm tham quan",
            "Bảo tàng",
            "Công viên",
            "Check-in / Ngắm cảnh"
        ]

    # Check-in
    if any(
        x in q
        for x in [
            "check in",
            "check-in",
            "chụp hình",
            "ngắm cảnh"
        ]
    ):
        groups.append(
            "Check-in / Ngắm cảnh"
        )

    # Tâm linh
    if any(
        x in q
        for x in [
            "chùa",
            "tâm linh"
        ]
    ):
        groups.append("Tâm linh")

    # Nếu nhận diện được nhóm
    if groups:
        groups = list(set(groups))

        data = data[
            data["nhom"].isin(groups)
        ]

    # Nếu khách muốn gần
    if any(
        x in q
        for x in [
            "gần",
            "quanh khách sạn",
            "không xa",
            "gần đây"
        ]
    ):
        data = data[
            data["khoang_cach_km"] <= 5
        ]

    # Sắp gần trước
    data = data.sort_values(
        "khoang_cach_km"
    )

    return data.head(max_places)


# ==================================================
# TẠO CONTEXT CHO AI
# ==================================================

def tao_context(data):

    lines = []

    for _, row in data.iterrows():

        line = (
            f"- {row['ten']} | "
            f"Nhóm: {row['nhom']} | "
            f"Khoảng cách: {row['khoang_cach_km']} km"
        )

        if pd.notna(row.get("dia_chi")):
            dia_chi = str(row["dia_chi"]).strip()

            if dia_chi:
                line += f" | Địa chỉ: {dia_chi}"

        if pd.notna(row.get("opening_hours")):
            opening = str(row["opening_hours"]).strip()

            if opening:
                line += f" | Giờ mở cửa: {opening}"

        if pd.notna(row.get("ban_do")):
            map_url = str(row["ban_do"]).strip()

            if map_url:
                line += f" | Bản đồ: {map_url}"

        lines.append(line)

    return "\n".join(lines)


# ==================================================
# HÀM GỌI AI
# ==================================================

def hoi_ai(question):

    selected = lay_dia_diem_phu_hop(
        question
    )

    context = tao_context(
        selected
    )

    system_prompt = """
Bạn là Mermaid AI Concierge, trợ lý du lịch dành riêng
cho khách lưu trú tại Mermaid Seaside Hotel Vũng Tàu.

Nhiệm vụ:
- tư vấn điểm tham quan;
- ăn uống;
- café;
- biển;
- vui chơi;
- lịch trình trải nghiệm tại Vũng Tàu.

Quy định:
1. Ưu tiên các địa điểm trong dữ liệu được cung cấp.
2. Không tự bịa địa điểm.
3. Ưu tiên địa điểm gần Mermaid Seaside Hotel.
4. Nếu khách cho biết số người, trẻ em, thời gian hoặc nhu cầu,
   hãy cá nhân hóa tư vấn.
5. Có thể lập lịch trình theo thứ tự hợp lý.
6. Khoảng cách là khoảng cách ước tính theo tọa độ.
7. Không tự đoán giờ mở cửa nếu dữ liệu không có.
8. Trả lời thân thiện, rõ ràng và ngắn gọn.
9. Khi có link bản đồ thì nên cung cấp.
"""

    user_prompt = f"""
CÂU HỎI CỦA KHÁCH:

{question}

CÁC ĐỊA ĐIỂM PHÙ HỢP TỪ CƠ SỞ DỮ LIỆU:

{context}

Hãy tư vấn dựa trên dữ liệu trên.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=system_prompt,
        input=user_prompt
    )

    return response.output_text


# ==================================================
# LƯU HỘI THOẠI
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )


# ==================================================
# Ô CHAT
# ==================================================

question = st.chat_input(
    "Hãy hỏi Mermaid AI..."
)


if question:

    # Hiển thị câu hỏi
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Trả lời
    with st.chat_message("assistant"):

        with st.spinner(
            "Mermaid AI đang tư vấn..."
        ):

            try:

                answer = hoi_ai(
                    question
                )

                st.markdown(answer)

            except Exception as e:

                answer = (
                    "Xin lỗi, hiện Mermaid AI chưa thể trả lời. "
                    "Vui lòng thử lại sau."
                )

                st.error(answer)

                st.caption(
                    f"Lỗi kỹ thuật: {e}"
                )

    # Lưu câu trả lời
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# ==================================================
# CHÂN TRANG
# ==================================================

st.markdown("---")

st.caption(
    "Dữ liệu địa điểm: © OpenStreetMap contributors."
)

st.caption(
    "Thông tin có thể thay đổi. "
    "Vui lòng kiểm tra lại trước khi sử dụng dịch vụ."
)
