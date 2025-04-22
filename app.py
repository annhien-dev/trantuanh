import os
import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO

# 📦 Đọc tất cả các sheet từ file Excel
@st.cache_data
def load_vocabulary_data():
    df = pd.read_excel('english_vocabulary.xlsx', sheet_name=None)
    return df

# 🔊 Tạo file audio từ văn bản
def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.save(audio_file)
    audio_file.seek(0)
    return audio_file

# 📘 Hiển thị bài đọc và từ vựng
def display_unit(unit_name, unit_data):
    if unit_name not in unit_data:
        st.error(f"Unit '{unit_name}' not found.")
        return

    unit_df = unit_data[unit_name]
    if not unit_df.empty:
        st.title(f"📚 Unit: {unit_name}")

        # 📖 Hiển thị bài đọc
        reading_text = unit_df['Reading Text'].iloc[0]
        if pd.notna(reading_text):
            st.subheader("📖 Reading Text:")
            st.write(reading_text)

            # 🎧 Phát audio từ file nếu có
            st.subheader("🔊 Listen to the reading:")
            audio_path = f"audio/{unit_name}.mp3"
            if os.path.exists(audio_path):
                st.audio(audio_path, format='audio/mp3')
            else:
                st.warning("⚠️ Audio file not found. Using TTS instead.")
                st.audio(generate_audio(reading_text), format='audio/mp3')

            st.write("---")

        # 📘 Hiển thị từ vựng
        st.subheader("📘 Vocabulary:")
        for _, row in unit_df.iterrows():
            if pd.isna(row['Question']):
                st.markdown(f"**{row['Vocabulary']}** ({row['IPA']})")
                st.write(f"**Example**: {row['Example']}")
                st.write(f"**Explanation**: {row['Explanation']}")
                st.write(f"**Note**: {row['Note']}")

                # 🔊 Phát âm từ và ví dụ
                st.markdown("🔊 **Pronunciation:**")
                st.audio(generate_audio(row['Vocabulary']), format='audio/mp3')

                st.markdown("🔊 **Example Audio:**")
                st.audio(generate_audio(row['Example']), format='audio/mp3')

                st.write("---")
    else:
        st.error(f"Unit {unit_name} is empty!")

# 🧠 Hiển thị câu hỏi trắc nghiệm
def display_quiz(unit_name, unit_df):
    st.subheader("🧠 Quiz Time!")

    quiz_data = unit_df[unit_df['Question'].notna()]
    if quiz_data.empty:
        st.info("No quiz questions found in this unit.")
        return

    question_row = quiz_data.sample(n=1).iloc[0]
    question = question_row['Question']
    options = [question_row['Option 1'], question_row['Option 2'], question_row['Option 3']]
    correct_answer = question_row['Correct Answer']
    explanation = question_row.iloc[-1]  # Giải thích quiz ở cột cuối cùng

    st.markdown(f"**❓ Question:** {question}")
    st.audio(generate_audio(question), format='audio/mp3')

    selected = st.radio("Choose the correct answer:", options)

    if selected:
        if selected == correct_answer:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! The correct answer is: {correct_answer}")

        if pd.notna(explanation):
            st.markdown(f"**Explanation:** {explanation}")
            st.audio(generate_audio(explanation), format='audio/mp3')

        if st.button("🔁 Next Question"):
            display_quiz(unit_name, unit_df)

# 🚀 App chính
def main():
    st.title("🧒 English Learning App for Kids")

    unit_data = load_vocabulary_data()
    units = list(unit_data.keys())
    selected_unit = st.sidebar.selectbox("📚 Choose a Unit", units)

    if selected_unit:
        display_unit(selected_unit, unit_data)
        display_quiz(selected_unit, unit_data[selected_unit])

    st.markdown("---")
    text_to_speak = st.text_input("🔊 Enter any text to hear it spoken aloud:")
    if text_to_speak:
        st.audio(generate_audio(text_to_speak), format="audio/mp3")

if __name__ == "__main__":
    main()
