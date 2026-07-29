from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import cast

from app.schemas.rag_schema import QueryRequest

from app.dependencies import (
    rag,
    get_db,
)

from crud import (
    create_conversation,
    create_message,
    get_messages,
)

router = APIRouter(tags=["Chat"])

@router.post("/query")
def query(request: QueryRequest, db: Session = Depends(get_db),):

    if not request.conversation_id:
        conversation = create_conversation(
            db,
            title=request.question[:50],
        )
        conversation_id = cast(int, conversation.id)
    else:
        conversation_id = request.conversation_id

    create_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=request.question,
    )

    messages = get_messages(
        db=db,
        conversation_id=conversation_id,
        limit=10,
    )

    history = []

    for msg in messages:
        history.append(
            {
                "role": msg.role,
                "content": msg.content,
            }
        )

    result = rag.ask(
        question=request.question,
        history=history,
        top_k=request.top_k,
        stream=request.stream,
        summarize=request.summarize,
        return_context=False,
    )

    create_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=result["answer"],
    )

    result["conversation_id"] = conversation_id
    return result