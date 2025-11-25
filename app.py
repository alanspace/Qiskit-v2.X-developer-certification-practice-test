import streamlit as st
import pandas as pd
import pickle
from pathlib import Path
import time

# Constants
BLANK_STUDENT_HISTORY_FILE = "necessary_files/student_history.pkl"
TASK_BY_SECTION_DICT_FILE = "necessary_files/task_by_section_dict.pkl"
PERCENT_BY_TASK_DICT_FILE = "necessary_files/percentage_by_task_dict.pkl"
QUESTION_BANK_DF_FILE = "necessary_files/question_df.pkl"

# Load data files
def load_data():
    with open(QUESTION_BANK_DF_FILE, "rb") as f:
        question_df = pickle.load(f)
    with open(TASK_BY_SECTION_DICT_FILE, "rb") as f:
        task_by_section_dict = pickle.load(f)
    with open(PERCENT_BY_TASK_DICT_FILE, "rb") as f:
        percentage_by_task_dict = pickle.load(f)
    return question_df, task_by_section_dict, percentage_by_task_dict

def main():
    st.title("Qiskit Certification Practice Test")
    
    # Initialize session state
    if 'student_history' not in st.session_state:
        st.session_state.student_history = None
        st.session_state.question_df = None
        st.session_state.current_question = 0
        st.session_state.correct_count = 0
        st.session_state.practice_test = None
        st.session_state.start_time = None
        
    # Load data on first run
    if st.session_state.question_df is None:
        question_df, task_dict, percent_dict = load_data()
        st.session_state.question_df = question_df
        st.session_state.task_dict = task_dict
        st.session_state.percent_dict = percent_dict
        
    # Main menu
    if st.session_state.practice_test is None:
        st.write("Welcome to the Qiskit Practice Test!")
        
        menu_choice = st.radio(
            "What would you like to do?",
            ["Take a practice test", "View stats", "Save progress", "Quit"]
        )
        
        if menu_choice == "Take a practice test":
            # Test setup options
            col1, col2 = st.columns(2)
            with col1:
                test_type = st.radio("Test Type", ["Full Test", "Topic Specific"])
                n_questions = st.number_input("Number of questions", 1, 100, 10)
            with col2:
                timed = st.checkbox("Timed test")
                adaptive = st.selectbox(
                    "Adaptive Mode",
                    ["Focus on unseen questions", "Focus on wrong answers", "Random"]
                )
            
            if st.button("Start Practice"):
                # Generate practice test here
                st.session_state.practice_test = question_df.sample(n=n_questions)
                st.session_state.start_time = time.time()
                st.experimental_rerun()
                
    # Practice test interface
    else:
        current_q = st.session_state.practice_test.iloc[st.session_state.current_question]
        
        # Display question
        st.write(f"### Question {st.session_state.current_question + 1}")
        st.write(current_q["Question"])
        
        # Display choices as buttons
        answer = st.radio(
            "Select your answer:",
            [
                f"A: {current_q.get('Choice_A', '')}",
                f"B: {current_q.get('Choice_B', '')}",
                f"C: {current_q.get('Choice_C', '')}",
                f"D: {current_q.get('Choice_D', '')}"
            ]
        )
        
        if st.button("Submit Answer"):
            # Check answer and show explanation
            selected = answer[0].upper()
            correct = current_q["Correct_Answer"]
            
            if selected == correct:
                st.success("Correct!")
                st.session_state.correct_count += 1
            else:
                st.error(f"Incorrect. The correct answer was {correct}")
            
            if "Explanation" in current_q:
                st.info(f"Explanation: {current_q['Explanation']}")
                
            # Move to next question
            st.session_state.current_question += 1
            
            # Check if test is complete
            if st.session_state.current_question >= len(st.session_state.practice_test):
                end_time = time.time()
                duration = end_time - st.session_state.start_time
                st.success(f"""
                Test complete!
                Score: {st.session_state.correct_count}/{len(st.session_state.practice_test)}
                Time taken: {duration:.1f} seconds
                """)
                if st.button("Take Another Test"):
                    st.session_state.practice_test = None
                    st.session_state.current_question = 0
                    st.session_state.correct_count = 0
                    st.experimental_rerun()
            else:
                st.experimental_rerun()
                
if __name__ == "__main__":
    main()