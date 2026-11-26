from prompt_templates import memory_prompt_template
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.embeddings import Embeddings
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain_chroma import Chroma
from transformers import AutoModel, AutoTokenizer
import chromadb
from chromadb.config import Settings
import torch
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

CHROMA_PATH = PROJECT_ROOT / "chroma_db"

class LocalBgeEmbeddings(Embeddings):
    """Create normalized CLS embeddings from a local BGE model directory."""

    def __init__(self, model_path: Path):
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(model_path),
            local_files_only=True,
        )
        self.model = AutoModel.from_pretrained(
            str(model_path),
            local_files_only=True,
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def _embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for start in range(0, len(texts), 16):
            batch = texts[start:start + 16]
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            inputs = {name: tensor.to(self.device) for name, tensor in inputs.items()}
            with torch.inference_mode():
                pooled = self.model(**inputs).last_hidden_state[:, 0]
                normalized = torch.nn.functional.normalize(pooled, p=2, dim=1)
            vectors.extend(normalized.cpu().tolist())
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text])[0]


def load_normal_chain(chat_history):
    """Loads the normal chat chain."""
    return chatChain(chat_history)

def load_pdf_chat_chain(chat_history):
    """Loads the PDF-based chat chain."""
    return pdfChatChain(chat_history)


def create_llm(model_path=config["model_path"]["large"], model_type=config["model_type"], model_config=config["model_config"]):
    model_file = Path(model_path)
    if not model_file.is_absolute():
        model_file = PROJECT_ROOT / model_file
    model_config = dict(model_config)
    if not torch.cuda.is_available():
        model_config["gpu_layers"] = 0
    if not model_file.is_file():
        raise FileNotFoundError(
            f"LLM model not found: {model_file}. Download the configured GGUF model "
            "and place it at the path specified in config.yaml."
        )

    print("Loading LLM model...")
    llm = CTransformers(model=str(model_file), model_type=model_type, config=model_config)
    print("LLM loaded successfully.")
    return llm



def create_embeddings(embeddings_path=config["embeddings_path"]):
    """Load embeddings model."""
    model_path = Path(embeddings_path)
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    if not model_path.is_dir():
        raise FileNotFoundError(
            f"Embedding model not found: {model_path}. Download the configured model "
            "before using PDF chat."
        )
    return LocalBgeEmbeddings(model_path)

def create_prompt_from_template(template):
    """Generate a prompt from a template."""
    return PromptTemplate.from_template(template)

def load_vectordb(embeddings):
    """Load ChromaDB for document storage & metadata tracking."""
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    persistent_client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False),
    )

    # Main vector database for documents
    vector_db = Chroma(
        client=persistent_client,
        collection_name="pdfs",
        embedding_function=embeddings
    )

    # Metadata store for tracking processed PDFs
    hash_store = Chroma(
        client=persistent_client,
        collection_name="pdf_hashes",
        embedding_function=embeddings
    )

    return vector_db, hash_store


def load_retrieval_chain(llm, vector_db):
    retriever = vector_db.as_retriever(search_kwargs={"k": 1})  # ✅ Reduce retrieval complexity
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)


class pdfChatChain:
    """Handles PDF-based AI chat."""

    def __init__(self, chat_history):
        self.chat_history = chat_history
        self.vector_db, self.hash_store = load_vectordb(create_embeddings())
        llm = create_llm()
        self.llm_chain = load_retrieval_chain(llm, self.vector_db)

    def run(self, user_input):
        """Process user queries using vector retrieval."""
        print("PDF chat chain is running...")

        print("Sending query to LLM...")
        response = self.llm_chain.invoke({"query": user_input})["result"]
        self.chat_history.add_user_message(user_input)
        self.chat_history.add_ai_message(response)
        print("Response received from LLM.")

        if not response or response.strip() == "":
            response = "No relevant information found. Try asking differently."
            print("No response from AI; using fallback message.")

        print("AI Response:", response)
        return response




def debug_retrieve(query):
    """Manually test ChromaDB retrieval."""
    vector_db, _ = load_vectordb(create_embeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke(query)
    print("Retrieved documents:", results)
    return results

class chatChain:
    """Handles normal chat (non-PDF)."""

    def __init__(self, chat_history):
        self.chat_history = chat_history
        self.llm = create_llm()
        self.prompt = create_prompt_from_template(memory_prompt_template)

    def run(self, user_input):
        previous_messages = self.chat_history.messages[-6:]
        history = "\n".join(
            f"{'USER' if message.type == 'human' else 'ASSISTANT'}: {message.content}"
            for message in previous_messages
        )
        prompt = self.prompt.format(history=history, human_input=user_input)
        response = self.llm.invoke(prompt, stop=["USER:"])
        self.chat_history.add_user_message(user_input)
        self.chat_history.add_ai_message(response)
        return response
