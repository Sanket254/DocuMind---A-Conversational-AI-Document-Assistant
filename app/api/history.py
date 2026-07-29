from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db

from crud import (
    create_conversation,
    get_conversation,
    get_messages,
    list_conversations,
    delete_conversation,
)

from app.schemas.history import ConversationCreate

router = APIRouter(
    prefix="/history",
    tags=["Conversation History"],
)

@router.post("/conversations")
def new_conversation(conversation: ConversationCreate, db: Session = Depends(get_db),):
    conv = create_conversation(
        db,
        title=conversation.title,
    )
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
    }


@router.get("/conversations")
def get_all_conversations(db: Session = Depends(get_db),):
    conversations = list_conversations(db)
    return conversations



@router.get("/conversations/{conversation_id}")
def get_single_conversation(conversation_id: int, db: Session = Depends(get_db),):

    conversation = get_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = get_messages(
        db,
        conversation_id,
    )

    return {
        "conversation": conversation,
        "messages": messages,
    }



@router.delete("/conversations/{conversation_id}")
def remove_conversation(conversation_id: int, db: Session = Depends(get_db),):

    success = delete_conversation(
        db,
        conversation_id,
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "message": "Conversation deleted successfully"
    }





