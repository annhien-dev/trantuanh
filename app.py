import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import tempfile

# Cấu hình giao diện
st.set_page_config(page_title="Học từ vựng", layout="centered")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

if "random_word" not in st.session_state:
    st.session_state.random_word = None

if "today_words" not in st.session_state:
    st.session_state.today_words = []

# Chọn ngôn ngữ học
lang = st.selectbox("🔤 Chọn ngôn ngữ học", ["Tiếng Anh", "Tiếng Nhật"])

# Load dữ liệu từ file Excel
def load_data(lang):
    filename = 'english_vocabulary.xlsx' if lang == "Tiếng Anh" else 'japanese_vocabulary.xlsx'
    # Đọc file Excel
    data = pd.read_excel(filename, sheet_name=None)  # sheet_name=None để đọc tất cả các sheet
    return data

data = load_data(lang)

# Lấy danh sách cấp độ (sheet names)
levels = list(data.keys())

# Chọn cấp độ học
level = st.selectbox("Chọn cấp độ học", levels)

# Lấy dữ liệu từ sheet của cấp độ
level_data = data[level]

# Chọn chế độ học
st.markdown("## ✨ Chọn chế độ học từ vựng")
mode = st.radio("Chế độ học", ["🔍 Chọn từ thủ công", "🔁 Học từ ngẫu nhiên", "📅 Học 5 từ hôm nay"])

# Xử lý lựa chọn
word_list = level_data['Word'].tolist()

if mode == "🔁 Học từ ngẫu nhiên":
    if st.button("🎲 Lấy từ ngẫu nhiên"):
        st.session_state.random_word = random.choice(word_list)
    selected_word = st.session_state.random_word or word_list[0]

elif mode == "📅 Học 5 từ hôm nay":
    if not st.session_state.today_words:
        st.session_state.today_words = random.sample(word_list, min(5, len(word_list)))
    selected_word = st.selectbox("📆 Hôm nay bạn học:", st.session_state.today_words)

else:
    st.markdown("### 📚 Tìm & chọn từ vựng")
    search_keyword = st.text_input("🔎 Nhập từ khóa để tìm từ vựng")
    filtered_words = [w for w in word_list if search_keyword.lower() in w.lower()] if search_keyword else word_list
    if not filtered_words:
        st.warning("😕 Không tìm thấy từ nào phù hợp.")
        st.stop()
    selected_word = st.selectbox("📘 Chọn từ:", filtered_words)

# Ghi lịch sử học
if selected_word and selected_word not in st.session_state.history:
    st.session_state.history.append(selected_word)

# Lấy dữ liệu từ đã chọn
word_row = level_data[level_data['Word'] == selected_word].iloc[0]

# Hiển thị thông tin từ vựng
st.title(f"📘 Học từ: {word_row['Word']}")
st.write(f"**Nghĩa:** {word_row['Meaning']}")
st.write(f"**Ví dụ:** {word_row['Example']}")
st.caption(f"{word_row['Example_Vn']}")

# Giải thích ngữ pháp
st.markdown("📚 **Giải thích ngữ pháp:**")
st.info(word_row.get("Grammar", "Chưa có thông tin ngữ pháp cho từ này."))

# Ngôn ngữ phát âm
tts_lang = 'ja' if lang == "Tiếng Nhật" else 'en'

# Phát âm từ
tts = gTTS(word_row["Word"], lang=tts_lang)
with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
    tts.save(fp.name)
    st.audio(fp.name, format='audio/mp3', start_time=0)

# Phát âm ví dụ
tts_sentence = gTTS(word_row["Example"], lang=tts_lang)
with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp2:
    tts_sentence.save(fp2.name)
    st.audio(fp2.name, format='audio/mp3', start_time=0)

# Trắc nghiệm - Ẩn mặc định câu hỏi
st.markdown("---")
st.subheader("📝 Trắc nghiệm_Nhím ơi cố gắng lên nhé !!!")

# Tạo một button để hiển thị câu hỏi trắc nghiệm
show_quiz = st.button("📚 Hiển thị câu hỏi trắc nghiệm")

# Lấy câu hỏi trắc nghiệm và phát âm câu hỏi
if isinstance(word_row['Quiz'], str):
    quiz_data = eval(word_row['Quiz'])  # Đảm bảo 'Quiz' là danh sách của câu hỏi
else:
    quiz_data = word_row['Quiz']

for idx, q in enumerate(quiz_data):
    # Phát âm câu hỏi trắc nghiệm
    tts_question = gTTS(q['question'], lang=tts_lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp3:
        tts_question.save(fp3.name)
        st.audio(fp3.name, format='audio/mp3', start_time=0)

    # Nếu nhấn nút "Hiển thị câu hỏi", hiển thị câu hỏi
    if show_quiz:
        st.write(f"**Câu {idx + 1}:** {q['question']}")
    
    # Hiển thị đáp án và cho phép người dùng chọn
    st.write(f"**Lựa chọn đáp án:**")
    ans = st.radio("Chọn đáp án", q['options'], key=f"q{idx}")

    # Kiểm tra khi người dùng chọn đáp án
    if st.button(f"Kiểm tra câu {idx + 1}", key=f"btn{idx}"):
        if ans == q["correct_answer"]:
            st.success("✅ Chính xác!")
        else:
            st.error(f"❌ Sai rồi. Đáp án đúng là: {q['correct_answer']}")

    st.markdown("---")

# Bài đọc hiểu - Ẩn mặc định
st.markdown("📖 **Bài đọc hiểu**")

# Tạo một button để hiển thị phần bài đọc hiểu
show_reading = st.button("📖 Hiển thị đoạn văn đọc hiểu")

# Hiển thị đoạn văn đọc hiểu khi người dùng nhấn nút
if show_reading:
    reading_text = word_row["Reading_Text"]
    reading_questions = eval(word_row["Reading_Questions"])

    st.write(f"Đoạn văn đọc hiểu_Nhím ơi cố gắng lên nhé !!!: {reading_text}")

    # Phát âm đoạn văn đọc hiểu
    tts_reading = gTTS(reading_text, lang=tts_lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp4:
        tts_reading.save(fp4.name)
        st.audio(fp4.name, format='audio/mp3', start_time=0)

    # Hiển thị câu hỏi bài đọc hiểu sau khi nhấn nút
    for idx, q in enumerate(reading_questions):
        # Phát âm câu hỏi đọc hiểu
        tts_reading_question = gTTS(q['question'], lang=tts_lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp5:
            tts_reading_question.save(fp5.name)
            st.audio(fp5.name, format='audio/mp3', start_time=0)

        # Hiển thị đáp án và cho phép người dùng chọn
        st.write(f"**Câu hỏi {idx + 1}:**")
        ans = st.radio("Chọn đáp án", q['options'], key=f"reading_q{idx}")

        # Kiểm tra khi người dùng chọn đáp án
        if st.button(f"Kiểm tra câu {idx + 1}", key=f"reading_btn{idx}"):
            if ans == q["correct_answer"]:
                st.success("✅ Chính xác!")
            else:
                st.error(f"❌ Sai rồi. Đáp án đúng là: {q['correct_answer']}")
        st.markdown("---")

# Lịch sử học
with st.expander("📜 Lịch sử từ đã học (trong phiên)"):

    for i, word_h in enumerate(st.session_state.history, 1):
        st.write(f"{i}. {word_h}")
