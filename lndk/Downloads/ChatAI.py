import random
#!/usr/bin/env python3

def main():
    print("Welcome to ChatAI - Your AI Assistant")
    print("I'm here to help answer your questions!")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye! Have a nice day.")
            break

        # Simple responses based on input
        if 'hello' in user_input.lower() or 'hi' in user_input.lower():
            print("\nChatAI: Hello! How can I help you today?")
        elif 'how are you' in user_input.lower():
            print("\nChatAI: I'm just a simple program, but I'm functioning well. Thanks for asking!")
        elif 'who are you' in user_input.lower() or 'what are you' in user_input.lower():
            print("\nChatAI: I'm ChatAI, a simple AI assistant in PyShellOS.")
        elif 'help' in user_input.lower():
            print("\nChatAI: I can answer simple questions. Try asking about PyShellOS or general knowledge.")
        elif 'pyshell' in user_input.lower() or 'shellOS' in user_input.lower():
            print("\nChatAI: PyShellOS is a simulated shell environment written in Python.")
            print("It demonstrates basic shell functionality like file management, user accounts, and more.")
        else:
            print("\nChatAI: I'm not sure how to respond to that. I'm a very simple AI with limited responses.")
            print("Try asking about PyShellOS or use simple greetings.")

if __name__ == "__main__":
    main()
class SimpleAI:
    def __init__(self):
        # Dictionary containing possible responses for different types of messages
        self.responses = {
            "hello": [
                "Hello! How are you?",
                "Hi there! Nice to meet you!",
                "Hey! How's your day going?"
            ],
            "how_are_you": [
                "I'm just a computer program, so I don't have feelings, but thanks for asking!",
                "As an AI, I don't experience emotions, but I'm functioning well!",
                "I appreciate you asking, but I'm just a program designed to chat!"
            ],
            "good": [
                "That's great to hear!",
                "Wonderful! I'm glad things are going well!",
                "Excellent! Keep that positive spirit!"
            ],
            "bad": [
                "I'm sorry to hear that. I hope things get better!",
                "That's unfortunate. Remember that tough times don't last forever.",
                "I wish I could help more, but I'm just a simple program."
            ],
            "default": [
                "Interesting! Tell me more.",
                "I see. Please continue.",
                "I'm not sure I understand, but I'm listening.",
                "Could you rephrase that?"
            ]
        }

    def respond(self, user_input):
        # Convert input to lowercase for easier matching
        user_input = user_input.lower()

        # Check for different types of input and return appropriate response
        if any(greeting in user_input for greeting in ["hello", "hi", "hey"]):
            return random.choice(self.responses["hello"])

        elif any(phrase in user_input for phrase in ["how are you", "how're you", "how you"]):
            return random.choice(self.responses["how_are_you"])

        elif any(good in user_input for good in ["good", "great", "awesome", "fine"]):
            return random.choice(self.responses["good"])

        elif any(bad in user_input for bad in ["bad", "terrible", "not good", "sad"]):
            return random.choice(self.responses["bad"])

        # If no specific matches, return a default response
        return random.choice(self.responses["default"])

def main():
    ai = SimpleAI()
    print("AI: Hello! Type 'quit' to end the conversation.")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            print("AI: Goodbye!")
            break
            
        response = ai.respond(user_input)
        print("AI:", response)

if __name__ == "__main__":
    main()