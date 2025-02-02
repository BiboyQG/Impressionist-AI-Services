import time
import os
from typing import Union, List, Optional

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import EmbeddingFunc
from app.logger import get_logger

logger = get_logger("rag_service")


class RAGService:
    _instance: Optional["RAGService"] = None
    _initialized: bool = False

    def __new__(cls, working_dir: str):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
        return cls._instance

    def __init__(self, working_dir: str):
        """Initialize the RAG service with the working directory.

        Args:
            working_dir (str): The working directory for storing RAG data
        """
        # Only initialize once
        if not self._initialized:
            self.working_dir = working_dir
            logger.info(
                f"Initializing RAG service with working directory: {working_dir}"
            )

            if not os.path.exists(working_dir):
                logger.info(f"Creating working directory: {working_dir}")
                os.makedirs(working_dir)

            self.rag = LightRAG(
                working_dir=working_dir,
                llm_model_func=gpt_4o_mini_complete,
                embedding_func=EmbeddingFunc(
                    embedding_dim=1536,
                    max_token_size=8192,
                    func=lambda texts: openai_embed(
                        texts, model="text-embedding-3-small"
                    ),
                ),
            )
            logger.info("RAG service initialized successfully")
            self._initialized = True

    def insert_text(self, text: str) -> None:
        """Insert a text string into the RAG system.

        Args:
            text (str): The text content to insert
        """
        logger.debug(f"Inserting text: {text[:100]}...")
        self.rag.insert(text)
        logger.info("Text inserted successfully")

    def insert_file(self, file_path: str) -> None:
        """Insert content from a file into the RAG system.

        Args:
            file_path (str): Path to the file to insert
        """
        logger.info(f"Inserting file: {file_path}")
        try:
            with open(file_path, "r") as f:
                self.insert_text(f.read())
            logger.info(f"File {file_path} inserted successfully")
        except Exception as e:
            logger.error(f"Error inserting file {file_path}: {str(e)}")
            raise

    def insert_files(self, file_paths: List[str]) -> None:
        """Insert content from multiple files into the RAG system.

        Args:
            file_paths (List[str]): List of file paths to insert
        """
        logger.info(f"Inserting {len(file_paths)} files")
        for file_path in file_paths:
            self.insert_file(file_path)

    def query(
        self, question: str, mode: str = "hybrid", measure_time: bool = False
    ) -> Union[str, tuple[str, float]]:
        """Query the RAG system with a question.

        Args:
            question (str): The question to ask
            mode (str, optional): Search mode ("hybrid", "semantic", or "keyword"). Defaults to "hybrid".
            measure_time (bool, optional): Whether to measure and return query time. Defaults to False.

        Returns:
            Union[str, tuple[str, float]]: If measure_time is False, returns just the answer.
                                         If measure_time is True, returns tuple of (answer, time_taken)
        """
        start_time = time.time() if measure_time else None

        answer = self.rag.query(question, param=QueryParam(mode=mode))

        if measure_time:
            time_taken = time.time() - start_time
            return answer, time_taken

        return answer


def rag_pipeline(conversation_history: str) -> str:
    """Pipeline for RAG processing.

    Args:
        conversation_history (str): The conversation history to process

    Returns:
        str: The retrieved knowledge
    """
    working_dir = os.getenv("WORKING_DIR")
    if not working_dir:
        logger.error("WORKING_DIR environment variable is not set")
        return None

    # This will reuse the existing instance if it exists
    rag_service = RAGService(working_dir)

    # Example: Query with time measurement
    answer, time_taken = rag_service.query(conversation_history, measure_time=True)

    logger.info("-" * 100)
    logger.info("Hybrid search")
    logger.info("-" * 100)
    logger.info(answer)
    logger.info(f"Time taken: {time_taken} seconds")

    return answer


# Example usage
if __name__ == "__main__":
    working_dir = os.getenv("WORKING_DIR")
    if not working_dir:
        raise ValueError("WORKING_DIR environment variable is not set")

    rag_service = RAGService(working_dir)

    # Example: Insert a file
    # info_path = f"{working_dir}/data/info.txt"
    # rag_service.insert_file(info_path)

    # Example: Query with time measurement
    question = "What is the GPA of Banghao Chi in UIUC?"
    answer, time_taken = rag_service.query(question, measure_time=True)

    logger.info("-" * 100)
    logger.info("Hybrid search")
    logger.info("-" * 100)
    logger.info(answer)
    logger.info(f"Time taken: {time_taken} seconds")
