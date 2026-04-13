from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie

# Import our custom AI service
# We instantiate it once per worker, but for Django it's better to instantiate per request or use a singleton
# For simplicity, we create a new instance per request to avoid state bleeding between users
from .services import AIManagerService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    """
    Endpoint for the AI Manager chat widget.
    Receives a message from the user, processes it with Gemini, and returns the response.
    """
    message = request.data.get('message', '') # Can be empty if only sending a file
    file_data = request.data.get('file')
    
    if not message and not file_data:
        return Response({"error": "Message or file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        # Initialize the AI service
        ai_service = AIManagerService()
        
        # Process the message
        result = ai_service.process_message(message, file_data)
        
        if result.get("success"):
            return Response({
                "message": result.get("text"),
                "action": result.get("action")
            })
        else:
            return Response({"error": result.get("error")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
