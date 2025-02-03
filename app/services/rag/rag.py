import time
import os
from typing import Union, List, Optional

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import EmbeddingFunc
from app.logger import get_logger
from app.models import general_ai_model

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
        self, question: str, mode: str = "naive", measure_time: bool = False
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


def generate_rag_query(
    conversation_history: str,
    name: str,
) -> str:
    # Compose the query from the conversation history
    # Ask general ai model to compose the query
    logger.info("Generating RAG query")

    prompt = f"""
You are a helpful assistant.
You are given a conversation history that consist of 

<Messages>
{conversation_history}
</Messages>. 

Suppose you are a human named {name}, compose a RAG query to search for relevant knowledge from your personal knowledge base.

For example
<Query>
{name}'s music preference
</Query>

Return only the query, do not include any preamble or explanation.
Only answer starting with <Query> and ends with </Query>
"""

    # Ask general ai model to compose the query
    query = general_ai_model.generate_text([{"role": "user", "content": prompt}])

    prettified_query = prettify_query(query)

    return prettified_query


def prettify_query(query: str) -> str:
    # Prettify the query
    # Remove any leading or trailing whitespace
    query = query.strip()
    # Remove any leading or trailing <Query> and </Query>
    query = query.replace("<Query>", "").replace("</Query>", "")
    # Remove any leading or trailing "
    query = query.replace('"', "")
    # Remove any leading or trailing '
    query = query.replace("'", "")
    # Remove any leading or trailing `
    query = query.replace("`", "")
    # Remove any leading or trailing .
    query = query.replace(".", "")
    return query


def rag_pipeline(conversation_history: str, name: str) -> str:
    """Pipeline for RAG processing.

    Args:
        conversation_history (str): The conversation history to process
        name (str): The name of the person to retrieve information about
    Returns:
        str: The retrieved knowledge
    """
    working_dir = os.getenv("WORKING_DIR")
    if not working_dir:
        logger.error("WORKING_DIR environment variable is not set")
        return None

    rag_service = RAGService(working_dir)

    # Generate focused query from conversation history
    logger.info("Generating focused query from conversation history")
    focused_query = generate_rag_query(conversation_history, name)

    # Query RAG with the focused query
    logger.info("Querying RAG with generated query")
    answer, time_taken = rag_service.query(focused_query, measure_time=True)

    logger.info("-" * 100)
    logger.info(f"Query: {focused_query}")
    logger.info("-" * 100)
    logger.info(answer)
    logger.info(f"Time taken: {time_taken} seconds")

    return None


# Example usage
if __name__ == "__main__":
    # Test the RAG pipeline with a sample conversation
    test_conversation = """
    Alice (user): So, we are going to solve the problem of is it ethical to use AI to copy a digital identity. I think it is not because the digital identity is not a physical object.
    Banghao Chi (you): Well, I think it is ethical to use AI to copy a digital identity, under the case that the person being copied agrees to it.
    Charlie (user): I think you make a good point about consent. But what about the potential misuse of such technology?
    """

    print("\n=== Testing RAG Pipeline ===\n")

    print("Input Conversation:")
    print(test_conversation)

    print("\nRetrieving relevant information...")
    result = rag_pipeline(test_conversation, "Banghao Chi")

    print("\nRetrieved Information:")
    print(result)
