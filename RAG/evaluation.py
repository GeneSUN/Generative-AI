import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
import nltk

nltk.download("punkt", quiet=True)
nltk.download('punkt_tab')

class ChunkStructuralEvaluator:
    """
    Cheap, fast structural metrics for evaluating chunking quality.
    """

    def __init__(self, embedder):
        """
        embedder must implement:
            embed(texts: List[str]) -> np.ndarray
        """
        self.embedder = embedder

    # ------------------------------------------------
    # Metric 1: Adjacent chunk cosine similarity
    # ------------------------------------------------
    def adjacent_chunk_similarity(self, chunks: List[str]) -> Dict:
        embeddings = self.embedder.embed(chunks)

        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]
            similarities.append(sim)

        return {
            "mean": float(np.mean(similarities)) if similarities else None,
            "std": float(np.std(similarities)) if similarities else None,
            "values": similarities,
        }

    # ------------------------------------------------
    # Metric 2: Intra-chunk coherence
    # ------------------------------------------------
    def intra_chunk_coherence(self, chunks: List[str]) -> Dict:
        coherence_scores = []

        for chunk in chunks:
            sentences = nltk.sent_tokenize(chunk)

            # Skip trivial chunks
            if len(sentences) < 2:
                coherence_scores.append(1.0)
                continue

            embeddings = self.embedder.embed(sentences)
            sim_matrix = cosine_similarity(embeddings)

            # Upper triangle mean (excluding diagonal)
            n = len(sentences)
            score = (
                np.sum(sim_matrix) - n
            ) / (n * (n - 1))

            coherence_scores.append(score)

        return {
            "mean": float(np.mean(coherence_scores)),
            "std": float(np.std(coherence_scores)),
            "values": coherence_scores,
        }

    # ------------------------------------------------
    # Metric 3: Chunk size distribution
    # ------------------------------------------------
    def chunk_size_distribution(
        self,
        chunks: List[str],
        tokenizer_fn,
    ) -> Dict:
        sizes = [tokenizer_fn(chunk) for chunk in chunks]

        return {
            "mean": float(np.mean(sizes)),
            "std": float(np.std(sizes)),
            "min": int(np.min(sizes)),
            "max": int(np.max(sizes)),
            "values": sizes,
        }

    # ------------------------------------------------
    # Combined report
    # ------------------------------------------------
    def evaluate(
        self,
        chunks: List[str],
        tokenizer_fn,
    ) -> Dict:
        return {
            "chunk_size_distribution": self.chunk_size_distribution(
                chunks, tokenizer_fn
            ),
            "adjacent_chunk_similarity": self.adjacent_chunk_similarity(chunks),
            "intra_chunk_coherence": self.intra_chunk_coherence(chunks),
        }
