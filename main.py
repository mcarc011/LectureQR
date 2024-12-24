import streamlit as st

# Initialize session state for user answers and results
if "results" not in st.session_state:
    st.session_state["results"] = []  # List to store answers from multiple users
if "current_answers" not in st.session_state:
    st.session_state["current_answers"] = {}  # Store answers for the current user

# Function to display a question and options
def display_question(question, options, correct_answer, question_id):
    st.write(question)
    user_choice = st.radio("Select an answer:", options, key=f"radio_{question_id}")
    st.session_state["current_answers"][question_id] = user_choice

# App title
st.title("Multiple Choice Quiz")

# Define questions and answers
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

# Navigation: Quiz Page or Results Page
page = st.sidebar.selectbox("Navigation", ["Take Quiz", "View Results"])

if page == "Take Quiz":
    st.header("Take Quiz")
    for i, q in enumerate(questions):
        st.subheader(f"Question {i + 1}")
        display_question(q["question"], q["options"], q["answer"], question_id=i)
    
    if st.button("Submit Quiz"):
        correct_count = sum(
            st.session_state["current_answers"][i] == q["answer"] for i, q in enumerate(questions)
        )
        total_questions = len(questions)
        
        # Store results for the current user
        st.session_state["results"].append({
            "user": f"User {len(st.session_state['results']) + 1}",
            "correct": correct_count,
            "total": total_questions,
        })
        
        # Reset current answers for a new user
        st.session_state["current_answers"] = {}
        st.success(f"Your score: {correct_count}/{total_questions}")
        st.info("Your results have been saved. Go to 'View Results' to see everyone's scores.")

elif page == "View Results":
    st.header("Quiz Results")
    if not st.session_state["results"]:
        st.info("No results yet. Ask users to take the quiz.")
    else:
        # Display results as a table
        st.table(st.session_state["results"])
