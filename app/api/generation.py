from fastapi import APIRouter, HTTPException
from app.types import Message, GenerationResponse
from app.services.reply.generation import (
    get_conversation_history,
    get_profile,
    generate_response,
)
from app.logger import get_logger

logger = get_logger("generation_api")

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_message(message: Message, name: str):
    """
    Generate a response for a given message and assistant name

    Args:
        message: The incoming message with sender's information
        assistant_name: Name of the AI assistant who should respond
    """
    try:
        logger.info(f"Received generation request for name: {name}")

        # Validate that the message is not from the assistant
        if message.role == "assistant":
            raise HTTPException(
                status_code=400,
                detail="Cannot generate response for a message from an assistant",
            )

        # Get conversation history
        conversation_history = get_conversation_history(message)

        # Get assistant profile
        profile = get_profile(message)

        # Generate response
        response = generate_response(
            message=message,
            conversation_history=conversation_history,
            profile=profile,
            name=name,
        )

        logger.info("Generation completed successfully")
        return response

    except Exception as e:
        logger.error(f"Error in generation endpoint: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}"
        )
