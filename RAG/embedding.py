#@title OpenAI embedding wrapper
from openai import OpenAI
import numpy as np
from typing import List

class OpenAIEmbedder:
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key_env: str = "OPENAI_API_KEY",
    ):
        self.client = OpenAI()
        self.model = model

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of texts into embeddings.
        Returns: np.ndarray (n_texts, embedding_dim)
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)

embedder = OpenAIEmbedder(
    model="text-embedding-3-small"
)
