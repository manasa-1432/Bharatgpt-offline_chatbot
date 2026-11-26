import json
from langchain.schema.messages import HumanMessage, AIMessage
from datetime import datetime
from pathlib import Path

def message_to_dict(message):
    if hasattr(message, "model_dump"):
        return message.model_dump()
    return message.dict()

def save_chat_history_json(chat_history, file_path):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json_data = [message_to_dict(message) for message in chat_history]
        json.dump(json_data, f, ensure_ascii=False)

def load_chat_history_json(file_path):
    path = Path(file_path)
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)
        messages = [HumanMessage(**message) if message["type"] == "human" else AIMessage(**message) for message in json_data]
        return messages

def get_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

