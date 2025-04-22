import os
import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO

# Đọc dữ liệu từ tất cả các sheet trong file Excel
@st.cache_data
def load_vocabulary_data():
    # Đọc tất cả các sheet từ file Excel
    df = pd.read_excel('english_vocabulary.xlsx', sheet_name=None)  # sheet_name=None để đọc tất cả các sheet
    return df

# Hàm tạo câu hỏi trắc nghiệm
def display_quiz(unit_name, unit_data):
    # Kiểm tra các cột có trong unit_data để đảm bảo cột 'Unit' có tồn tại
    st.write("Columns in unit_data:", unit_data.columns)

    # Kiểm tra xem cột 'Unit' có tồn tại không
    if 'Unit' not in unit_data.columns:
        st.error("The column 'Unit' does not exist in the data. Please check your data structure.")
        return

    quiz_data = unit_data[unit_data['Unit'] == unit_name]  # Lọc câu hỏi theo unit

    if not quiz_data.empty:
        # Chọn câu hỏi ngẫu nhiên để hỏi
        question_row = quiz_data.sample(n=1).iloc[0]

        question = question_row['Question']
        options = [question_row['Option 1'], question_row['Option 2'], question_row['Option 3']]
        correct_answer = question_row['Correct Answer']
        explanation = question_row['Explanation']

        # Hiển thị câu hỏi
        st.subheader(f"Question: {question}")
        st.write(f"Options:")
        for idx, option in enumerate(options, 1):
            st.write(f"{idx}. {option}")
        
        # Phát âm câu hỏi
        st.subheader("Listen to the question:")
        audio_file = generate_audio(question)
        st.audio(audio_file, format='audio/mp3')

        # Chọn đáp án
        selected_option = st.radio("Choose your answer:", options)

        # Nếu đã chọn, kiểm tra câu trả lời
        if selected_option:
            if selected_option == correct_answer:
                st.success("Correct!")
            else:
                st.error("Incorrect!")
            
            st.write(f"Explanation: {explanation}")
            
            # Phát âm giải thích
            st.subheader("Listen to the explanation:")
            audio_file = generate_audio(explanation)
            st.audio(audio_file, format='audio/mp3')

            # Đưa ra một câu hỏi mới nếu muốn
            if st.button("Next Question"):
                display_quiz(unit_name, unit_data)
    else:
        st.error(f"No quiz data found for unit {unit_name}.")

# Hiển thị bài đọc và từ vựng liên quan
def display_unit(unit_name, unit_data):
    # Kiểm tra các sheet có trong unit_data (tên sheet sẽ là các unit)
    st.write("Available Units:", unit_data.keys())  # In ra các tên sheet (units)
    
    # Kiểm tra xem unit_name có tồn tại trong unit_data không
    if unit_name not in unit_data:
        st.error(f"Unit '{unit_name}' not found. Available units are: {list(unit_data.keys())}")
        return

    # Kiểm tra dữ liệu của unit hiện tại
    unit_data_filtered = unit_data[unit_name]

    # Kiểm tra các cột của unit_data_filtered
    st.write(f"Columns of {unit_name}: {unit_data_filtered.columns}")

    if not unit_data_filtered.empty:
        # Hiển thị bài đọc dài
        st.title(f"Unit: {unit_name}")
        reading_text = unit_data_filtered['Reading Text'].iloc[0]  # Lấy đoạn văn dài của unit
        if pd.notna(reading_text):
            st.subheader("Reading Text:")
            st.write(reading_text)  # Hiển thị đoạn văn bản

            # Phát âm bài đọc
            st.subheader("Listen to the reading:")
            audio_file = generate_audio(reading_text)  # Phát âm bài đọc qua gTTS
            st.audio(audio_file, format='audio/mp3')

            st.write("---")
        
        # Hiển thị danh sách từ vựng và phát âm qua TTS
        st.subheader("Vocabulary:")
        for index, row in unit_data_filtered.iterrows():
            if pd.isna(row['Question']):  # Chỉ hiển thị từ vựng, không hiển thị câu hỏi
                st.write(f"**{row['Vocabulary']}** ({row['IPA']})")
                st.write(f"**Example**: {row['Example']}")
                st.write(f"**Explanation**: {row['Explanation']}")
                st.write(f"**Note**: {row['Note']}")  # Hiển thị phần ghi chú

                # Phát âm từ vựng qua gTTS
                st.subheader(f"Listen to the pronunciation of '{row['Vocabulary']}':")
                audio_file = generate_audio(row['Vocabulary'])  # Phát âm từ vựng
                st.audio(audio_file, format='audio/mp3')
                
                st.subheader(f"Listen to the example sentence:")
                audio_file = generate_audio(row['Example'])  # Phát âm câu ví dụ
                st.audio(audio_file, format='audio/mp3')
                
                st.write("---")
    else:
        st.error(f"Unit {unit_name} not found!")

# Tạo file âm thanh từ văn bản và phát âm
def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.save(audio_file)
    audio_file.seek(0)
    return audio_file

# Chạy ứng dụng Streamlit
def main():
    st.title("English Learning App for Kids")
    
    # Đọc dữ liệu từ tất cả các sheet trong file Excel
    unit_data = load_vocabulary_data()

    # Hiển thị danh sách các unit (tên sheet)
    units = unit_data.keys()  # Lấy danh sách các sheet (unit)
    selected_unit = st.sidebar.selectbox("Choose a Unit", units)
    
    # Hiển thị bài đọc và các từ vựng của unit được chọn
    display_unit(selected_unit, unit_data)

    # Hiển thị câu hỏi trắc nghiệm của unit được chọn
    display_quiz(selected_unit, unit_data[selected_unit])
    
    # Tạo và phát âm từ vựng hoặc câu ví dụ khi người dùng yêu cầu
    text_to_speak = st.text_input("Enter text to hear pronunciation")
    if text_to_speak:
        audio_file = generate_audio(text_to_speak)
        st.audio(audio_file, format="audio/mp3")

if __name__ == "__main__":
    main()
