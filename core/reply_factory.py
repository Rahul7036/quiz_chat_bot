
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    Returns a tuple of (success, error_message).
    '''
    # Skip recording if this is the first message (no current question)
    if not current_question_id:
        return True, ""
    
    # Validate that the current_question_id is valid
    if current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID"
    
    # Initialize answers dict in session if it doesn't exist
    if "answers" not in session:
        session["answers"] = {}
    
    # Store the answer
    session["answers"][str(current_question_id)] = answer.strip()
    
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    Returns a tuple of (question_text, question_id).
    If there are no more questions, returns (None, None).
    '''
    # If no current question (first question)
    if current_question_id is None:
        if PYTHON_QUESTION_LIST:
            return PYTHON_QUESTION_LIST[0], 0
        return None, None
    
    # Calculate next question id
    next_question_id = current_question_id + 1
    
    # Check if we've reached the end of questions
    if next_question_id >= len(PYTHON_QUESTION_LIST):
        return None, None
    
    # Return next question and its ID
    return PYTHON_QUESTION_LIST[next_question_id], next_question_id


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    if "answers" not in session:
        return "No answers found. Please start the quiz again."
    
    answers = session["answers"]
    total_questions = len(PYTHON_QUESTION_LIST)
    answered_questions = len(answers)
    
    # Calculate completion percentage
    completion_rate = (answered_questions / total_questions) * 100
    
    # Build the response message
    response_parts = [
        "🎉 Quiz Complete! 🎉\n",
        f"You answered {answered_questions} out of {total_questions} questions.",
        f"Completion rate: {completion_rate:.1f}%\n",
        "Here's a summary of your answers:\n"
    ]
    
    # Add each question and answer to the summary
    for q_id in range(total_questions):
        question = PYTHON_QUESTION_LIST[q_id]
        answer = answers.get(str(q_id), "Not answered")
        response_parts.append(f"\nQ{q_id + 1}: {question}")
        response_parts.append(f"Your answer: {answer}")
    
    # Add a closing message based on completion rate
    if completion_rate == 100:
        response_parts.append("\n🌟 Excellent! You completed the entire quiz!")
    elif completion_rate >= 75:
        response_parts.append("\n👏 Great effort! You answered most of the questions!")
    elif completion_rate >= 50:
        response_parts.append("\n👍 Good start! Try to answer more questions next time!")
    else:
        response_parts.append("\n💪 Keep practicing! Try the quiz again to improve your score!")
    
    # Clear the session data for a fresh start
    session["answers"] = {}
    session["current_question_id"] = None
    
    return "\n".join(response_parts)
