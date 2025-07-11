from agent import WellnessAgent
from context import UserSessionContext
from utils.streaming import ResponseStreamer
import os
import time
from dotenv import load_dotenv

def main():
    """Main CLI entry point"""
    load_dotenv()
    
    print("🌿 Health & Wellness Planner CLI")
    print("-------------------------------\n")
    
    # Get user info
    name = input("What's your name? ")
    print(f"\nWelcome, {name}! I'll be your wellness assistant today.\n")
    
    # Initialize context
    context = UserSessionContext(name=name, uid=1)
    
    # Main loop
    agent = WellnessAgent(context)
    print("How can I help you with your health and wellness goals today?")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye! Wishing you wellness and happiness.")
            break
        
        print("\nAssistant: ", end='', flush=True)
        
        # Stream the response
        for chunk in ResponseStreamer.stream_response(user_input, context):
            print(chunk, end='', flush=True)
            time.sleep(0.05)  # Simulate typing
        
        print("\n")

if __name__ == "__main__":
    main()
