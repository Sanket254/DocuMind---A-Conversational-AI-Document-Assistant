from sqlalchemy.orm import Session
from models import Conversation, Message

def create_conversation(db: Session, title: str | None = None):
    """
    Create a new conversation.
    """
    conversation = Conversation(title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def create_message(db: Session, conversation_id: int, role: str, content: str,):
    """
    Save one message.
    """

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message



def get_conversation(db: Session, conversation_id: int,):
    """
    Get a conversation by ID.
    """

    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )


def get_messages(db: Session, conversation_id: int, limit: int = 10,):
    """
    Return latest N messages in order.
    """

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.timestamp.desc()
        )
        .limit(limit)
        .all()
    )

    # Reverse because we fetched newest first
    return messages[::-1]


def list_conversations(db: Session):
    """
    Return all conversations.
    """

    return (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def delete_conversation(db: Session, conversation_id: int,):
    """
    Delete a conversation.
    """

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if conversation is None:
        return False

    db.delete(conversation)
    db.commit()
    return True


