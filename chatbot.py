import re
import os

print("="*60)
print("ENVIRONMENT CLASSIFICATION:")
print("- Partially Observable, Deterministic, Sequential, and Static")
print("="*60)

def load_knowledge_base():
    filepath = "extracted_knowledge_base.txt"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

kb_text = load_knowledge_base()

# Task 5.1, 5.3, & 5.4: Define rules and patterns
RULES = {
    "greetings": {
        "pattern": r'\b(hi|hello|hey|greetings)\b',
        "is_topic": False,
        "response": "Hello! I am your AI assistant. Ask me about AI Search, Machine Learning, or R Programming."
    },
    "r_programming": {
        "pattern": r'\b(r|r programming|vector|matrix|data\.frame|tibble|closure)\b',
        "is_topic": True
    },
    "ai_search": {
        "pattern": r'\b(ai|search|heuristic|hill climbing|minimax|alpha-beta)\b|a[/\s]*\*',
        "is_topic": True
    },
    "machine_learning": {
        "pattern": r'\b(ml|machine learning|regression|gradient descent|bias|variance|overfitting)\b',
        "is_topic": True
    }
}

# Task 5.7: Maintain conversation context and hidden "deep dive" data
context_state = {
    "last_topic": None,
    "last_keyword": None,
    "deep_dive_text": None
}

def search_text_file(keyword):
    if 'a' in keyword.lower() and '*' in keyword:
        keyword = "A*"
        
    paragraphs = kb_text.split('\n\n')
    results = []
    
    for para in paragraphs:
        if keyword.lower() in para.lower():
            if len(para.strip()) > 10 and "===" not in para: 
                results.append(para.strip())
                
    if results:
        # Combine the first two relevant paragraphs found
        return " ".join(results[:2])
    return None

# Task 5.2: Represent user input as states and matched responses as actions
def process_user_input(user_input):
    user_input_lower = user_input.lower()
    
    # Check for a deep dive request FIRST (e.g., "tell me more", "examples")
    if context_state["deep_dive_text"] and re.search(r'\b(more|explain|elaborate|detail|example|examples)\b', user_input_lower):
        matched_rule = f"deep_dive ({context_state['last_keyword']})"
        confidence = 0.85
        action_response = f"Here is the deeper dive into {context_state['last_keyword']}:\n\n{context_state['deep_dive_text']}"
        
        # Clear the deep dive text after showing it
        context_state["deep_dive_text"] = None 
        return matched_rule, confidence, action_response
    
    matched_rule = None
    confidence = 0.0
    action_response = ""
    
    for rule_name, rule_data in RULES.items():
        match = re.search(rule_data["pattern"], user_input_lower)
        if match:
            matched_rule = rule_name
            confidence = 0.95 
            
            if not rule_data["is_topic"]:
                action_response = rule_data["response"]
                context_state["deep_dive_text"] = None
            else:
                matched_keyword = match.group(0).strip()
                context_state["last_topic"] = rule_name
                context_state["last_keyword"] = matched_keyword
                
                kb_result = search_text_file(matched_keyword)
                
                if kb_result:
                    # Parse the paragraph into sentences using periods
                    sentences = [s.strip() + '.' for s in kb_result.split('.') if s.strip()]
                    
                    if len(sentences) > 1:
                        # Provide the first sentence as the summary
                        short_summary = sentences[0]
                        # Store the rest of the text in memory for follow-ups
                        context_state["deep_dive_text"] = " ".join(sentences[1:])
                        action_response = f"{short_summary}\n\n(Tip: Ask 'tell me more' or 'give me an example' to deep dive!)"
                    else:
                        action_response = sentences[0]
                        context_state["deep_dive_text"] = None
                else:
                    action_response = f"I know '{matched_keyword}' belongs to {rule_name}, but I couldn't find specific details in your knowledge base."
                    context_state["deep_dive_text"] = None
            break
            
    # Task 5.6: Implement a default/fallback response
    if not matched_rule:
        matched_rule = "fallback_unknown"
        confidence = 0.10
        action_response = "I do not recognize that query. Try asking about Machine Learning, R data structures, or AI search algorithms."
        
    return matched_rule, confidence, action_response

# Task 5.9: Python-based console interface
def start_chat():
    print("\nChatbot initialized. Type 'quit', 'exit', or 'bye' to stop.")
    while True:
        user_query = input("\nYou: ")
        
        if user_query.lower() in ['quit', 'exit', 'bye']:
            print("Chatbot: Goodbye!")
            break
            
        rule, conf, reply = process_user_input(user_query)
        
        # Task 5.8: Display matched rule, confidence, and response
        print(f"\n[System Log -> Rule Matched: '{rule}', Confidence: {conf*100}%]")
        print(f"Chatbot: {reply}")

if __name__ == "__main__":
    start_chat()