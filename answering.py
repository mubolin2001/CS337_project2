import re

conversation_history = []

def is_what_is_question(user_input):
    return user_input.lower().startswith("what is")

def extract_subject(input):
    match = re.search(r"what is (a|an|the)?\s*(.*)\??", input.lower())
    if match:
        return match.group(2).strip()
    return None

def handle_what_is_question(user_input, save_conversation=True):
    if is_what_is_question(user_input):
        if save_conversation:
            conversation_history.append(user_input)
        subject = extract_subject(user_input)
        if subject:
            search_query = subject.replace(" ", "+")
            url = f"https://www.google.com/search?q=what+is+{search_query}"
            return f"I found this for you: {url}"
    return "I'm not sure what you're asking. Could you rephrase?"

def is_how_to_question(user_input):
    return user_input.lower().startswith("how to")

def extract_action(input):
    match = re.search(r"how to (.*?)(?: (?:a|an|the) (.*))?\??", input.lower())
    if match:
        return match.group(1).strip()
    return None

def handle_how_to_question(user_input, save_conversation=True):
    if is_how_to_question(user_input):
        if save_conversation:
            conversation_history.append(user_input)
        action = extract_action(user_input)
        if action:
            search_query = action.replace(" ", "+")
            url = f"https://www.google.com/search?q=how+to+{search_query}"
            return f"I found this for you: {url}"
    return "I'm not sure what you're asking. Could you rephrase?"

def is_vague_how_to_question(user_input):
    return user_input.lower() in ["how do i do that?", "how do i do this?", "how do i do it?"]

def handle_vague_how_to_question(user_input):
    if is_vague_how_to_question(user_input):
        if conversation_history:
            last_question = conversation_history[-1]
            if is_what_is_question(last_question):
                return handle_what_is_question(last_question, False)
            elif is_how_to_question(last_question):
                return handle_how_to_question(last_question, False)
            else:
                return "I'm not sure what you're asking. Could you provide more context?"
    return "I'm not sure what you're asking. Could you rephrase?"
    
    


