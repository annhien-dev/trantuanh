import os
import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO

# Đọc dữ liệu từ tất cả các sheet trong file Excel
@st.cache_data
def load_vocabulary_data():
    df = pd.read_excel('english_vocabulary.xlsx', sheet_name=None)
    return df

# Tạo file âm thanh từ văn bản
def generate_audio(text):
    try:
        if not text or not isinstance(text, str) or text.strip() == "":
            return None

        # Loại bỏ ký tự lạ có thể gây lỗi
        clean_text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").strip()

        tts = gTTS(text=clean_text, lang='en')
        audio_file = BytesIO()
        tts.save(audio_file)
        audio_file.seek(0)
        return audio_file
    except Exception as e:
        st.warning(f"⚠️ Could not generate audio: {e}")
        return None

# Hiển thị bài đọc và từ vựng
def display_unit(unit_name, unit_data):
    if unit_name not in unit_data:
        st.error(f"Unit '{unit_name}' not found.")
        return

    unit_df = unit_data[unit_name]
    if not unit_df.empty:
        st.title(f"📚 Unit: {unit_name}")

        # Hiển thị bài đọc
        reading_text = unit_df['Reading Text'].iloc[0]
        if pd.notna(reading_text):
            st.subheader("📖 Reading Text:")
            st.write(reading_text)

            # Phát âm bài đọc từ TTS
            st.subheader("🔊 Listen to the reading:")
            audio_file = generate_audio(reading_text)
            if audio_file:
                st.audio(audio_file, format='audio/mp3')

            st.write("---")

        # Hiển thị từ vựng
        st.subheader("📘 Vocabulary:")
        for _, row in unit_df.iterrows():
            if pd.isna(row['Question']):  # Chỉ hiển thị từ vựng (câu hỏi là NaN)
                st.markdown(f"**{row['Vocabulary']}** ({row['IPA']})")
                st.write(f"**Example**: {row['Example']}")
                st.write(f"**Explanation**: {row['Explanation']}")
                st.write(f"**Note**: {row['Note']}")

                # Phát âm từ vựng qua TTS
                st.markdown("🔊 **Pronunciation:**")
                audio_file = generate_audio(row['Vocabulary'])
                if audio_file:
                    st.audio(audio_file, format='audio/mp3')

                # Phát âm câu ví dụ
                st.markdown("🔊 **Example Audio:**")
                audio_file = generate_audio(row['Example'])
                if audio_file:
                    st.audio(audio_file, format='audio/mp3')

                st.write("---")
    else:
        st.error(f"Unit {unit_name} is empty!")

# Hiển thị câu hỏi trắc nghiệm
def display_quiz(unit_name, unit_df):
    st.subheader("🧠 Quiz Time!")

    quiz_data = unit_df[unit_df['Question'].notna()]
    if quiz_data.empty:
        st.info("No quiz questions found in this unit.")
        return

    # Tạo key duy nhất cho từng lần hiển thị câu hỏi
    quiz_key = f"{unit_name}_quiz_counter"
    if quiz_key not in st.session_state:
        st.session_state[quiz_key] = 0

    # Lấy 1 câu hỏi ngẫu nhiên mỗi lần
    question_row = quiz_data.sample(n=1).iloc[0]

    question = question_row['Question']
    options = [question_row['Option 1'], question_row['Option 2'], question_row['Option 3']]
    correct_answer = question_row['Correct Answer']
    explanation = question_row['Explanation']

    st.markdown(f"**❓ Question:** {question}")
    
    # Phát âm câu hỏi
    audio_file = generate_audio(question)
    if audio_file:
        st.audio(audio_file, format='audio/mp3')

    selected = st.radio("Choose the correct answer:", options, key=f"{unit_name}_radio_{st.session_state[quiz_key]}")

    if st.button("✅ Submit", key=f"{unit_name}_submit_{st.session_state[quiz_key]}"):
        if selected == correct_answer:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! The correct answer is: {correct_answer}")

        if pd.notna(explanation):
            st.markdown(f"**Explanation:** {explanation}")
            explanation_audio = generate_audio(explanation)
            if explanation_audio:
                st.audio(explanation_audio, format='audio/mp3')

    if st.button("🔁 Next Question", key=f"{unit_name}_next_{st.session_state[quiz_key]}"):
        st.session_state[quiz_key] += 1
        st.experimental_rerun()

# App chính
def main():
    st.title("🧒 English Learning App for Nhím - Angel")

    unit_data = load_vocabulary_data()
    units = list(unit_data.keys())
    selected_unit = st.sidebar.selectbox("📚 Choose a Unit", units)

    if selected_unit:
        display_unit(selected_unit, unit_data)
        display_quiz(selected_unit, unit_data[selected_unit])

    st.markdown("---")
    text_to_speak = st.text_input("🔊 Enter any text to hear it spoken aloud:")
    if text_to_speak:
        audio_file = generate_audio(text_to_speak)
        if audio_file:
            st.audio(audio_file, format="audio/mp3")

if __name__ == "__main__":
    main()
