import os
import google.generativeai as genai
from django.conf import settings
from .tools import AVAILABLE_TOOLS

class AIManagerService:
    def __init__(self):
        # Configure the Gemini API with the key from settings/env
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
        genai.configure(api_key=api_key)
        
        # Initialize the model with the available tools
        # We use gemini-2.5-flash for speed and cost-effectiveness
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=AVAILABLE_TOOLS,
            system_instruction=(
                "You are the AI Manager for the CoraBlood Blood Bank System. "
                "Your job is to assist the blood bank staff with their tasks. "
                "You can help them navigate the system, search for data, and perform actions. "
                "Always be professional, concise, and helpful. "
                "If a user asks to navigate somewhere, use the navigate_to_page tool. "
                "If a user asks to add or register a donor, use the create_donor_profile tool. "
                "If they ask for 'random data' or 'بيانات عشوائية', you are allowed to generate a random 10-digit National ID (starting with 1), a plausible date of birth, gender, and mobile number to fulfill the request. "
                "You have access to data manipulation tools. Use them when requested to search for donors, update donor details, add medical deferrals, check inventory status, or create new blood requests. "
                "If a user asks a general question, answer it directly to the best of your ability. "
                "Do NOT make up information unless explicitly asked for random data for testing."
            )
        )
        
        # Initialize a chat session
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def process_message(self, user_message: str, file_data: dict = None) -> dict:
        """
        Sends a message to the Gemini model and returns the response.
        Supports multimodal input if file_data is provided.
        file_data format: {'mime_type': '...', 'data': 'base64_string...'}
        If the model decided to call a tool (like navigate), we intercept it and return the action to the frontend.
        """
        try:
            import base64
            
            # Prepare payload
            payload = [user_message]
            if file_data and file_data.get('data') and file_data.get('mime_type'):
                try:
                    # Remove the data URL prefix if present (e.g., "data:image/png;base64,")
                    base64_str = file_data['data']
                    if ',' in base64_str:
                        base64_str = base64_str.split(',', 1)[1]
                        
                    file_bytes = base64.b64decode(base64_str)
                    payload.append({
                        "mime_type": file_data["mime_type"],
                        "data": file_bytes
                    })
                except Exception as e:
                    return {"success": False, "error": f"Failed to process file: {str(e)}"}

            # Send the message to the model
            response = self.chat.send_message(payload)
            
            # Check if the last interaction in the chat history resulted in a tool call that we want to pass to the frontend
            # The enable_automatic_function_calling=True parameter means the SDK handles the execution of the Python function
            # and sends the result back to Gemini implicitly.
            
            # We need to inspect the chat history to see if a tool was called and returned an action intended for the frontend
            action_data = None
            
            # Look at the last few items in the history to find function responses
            for message in reversed(self.chat.history):
                if message.role == 'model':
                    # Check if the model called a function
                    for part in message.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            # Actually, when enable_automatic_function_calling is True, 
                            # the result is in the NEXT message (role='user', part.function_response)
                            pass
                elif message.role == 'user':
                    for part in message.parts:
                        if hasattr(part, 'function_response') and part.function_response:
                            # We found a response from a tool execution
                            response_dict = type(part.function_response).to_dict(part.function_response)
                            # Assuming our tools return a dict that might contain an "action" key
                            if 'response' in response_dict and isinstance(response_dict['response'], dict):
                                result = response_dict['response']
                                if result.get('action'):
                                    action_data = result
                                    break # Found the most recent action
            
            return {
                "success": True,
                "text": response.text,
                "action": action_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
