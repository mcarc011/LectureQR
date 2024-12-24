import streamlit as st

# Function to display a question and options
def display_question(question, options, correct_answer, question_id):
    st.write(question)
    user_choice = st.radio("Select an answer:", options, key=f"radio_{question_id}")
    
    if st.button("Submit Answer", key=f"submit_{question_id}"):
        if user_choice == correct_answer:
            st.success("Correct! 🎉")
        else:
            st.error(f"Incorrect. The correct answer is: {correct_answer}")

# App title
st.title("Multiple Choice Quiz")

# Questions and Answers
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris",
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Mars",
    },
    {
        "question": "Who wrote 'To Kill a Mockingbird'?",
        "options": ["Harper Lee", "J.K. Rowling", "Ernest Hemingway", "Mark Twain"],
        "answer": "Harper Lee",
    },
]

# Display the quiz
for i, q in enumerate(questions):
    st.subheader(f"Question {i + 1}")
    display_question(q["question"], q["options"], q["answer"], question_id=i)
