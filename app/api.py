from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from app.types import Message, GenerationResponse
from app.services.reply.generation import (
    get_conversation_history,
    get_profile,
    generate_response,
)

api_router = APIRouter()


@api_router.post("/reply", response_model=GenerationResponse)
async def generate_message(
    name: str = Body(..., embed=True),
    # message: Message
):
    """
    Generate a response for a given message and assistant name

    Args:
        message: The incoming message with sender's information
        assistant_name: Name of the AI assistant who should respond
    """
    try:
        # Validate that the message is not from the assistant
        # if message.role == "you":
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Cannot generate response for a message from impressionist itself",
        #     )

        # TODO: delete this example message
        message = Message(
            content="I think you make a good point about consent. But what about the potential misuse of such technology?",
            role="user",
            sender_name="Charlie",
            timestamp="2024-02-02T10:00:10Z",
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

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}"
        )


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}
