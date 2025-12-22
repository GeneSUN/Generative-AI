import re
import nltk
import spacy
import tiktoken as tk
from typing import List, Literal, Callable

nltk.download("punkt", quiet=True)


class TextChunker:
    """
    Sentence-aware, token-bounded chunker with pluggable
    sentence splitters and token counters.
    """

    def __init__(
        self,
        max_tokens: int,
        overlap: int = 0,
        sentence_splitter: Literal["regex", "nltk", "spacy"] = "spacy",
        token_encoding: str = "cl100k_base",
        spacy_model: str = "en_core_web_sm",
    ):
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.sentence_splitter = sentence_splitter

        # Tokenizer
        self.encoding = tk.get_encoding(token_encoding)

        # NLP engines (lazy init where possible)
        self._nlp = None
        self.spacy_model = spacy_model

    # ---------------------------
    # Sentence splitting methods
    # ---------------------------
    def _split_by_regex(self, text: str) -> List[str]:
        sentences = re.split(r"[.!?]", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_by_nltk(self, text: str) -> List[str]:
        return nltk.sent_tokenize(text)

    def _split_by_spacy(self, text: str) -> List[str]:
        if self._nlp is None:
            self._nlp = spacy.load(self.spacy_model)
        doc = self._nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    def split_sentences(self, text: str) -> List[str]:
        """
        Dispatch sentence splitting based on configuration.
        """
        if self.sentence_splitter == "regex":
            return self._split_by_regex(text)
        elif self.sentence_splitter == "nltk":
            return self._split_by_nltk(text)
        elif self.sentence_splitter == "spacy":
            return self._split_by_spacy(text)
        else:
            raise ValueError(f"Unsupported sentence splitter: {self.sentence_splitter}")

    # ---------------------------
    # Token counting
    # ---------------------------
    def count_tokens(self, text: str) -> int:
        """
        Counts tokens using tiktoken (LLM-compatible).
        """
        return len(self.encoding.encode(text))

    # ---------------------------
    # Chunking logic
    # ---------------------------
    def chunk(self, text: str) -> List[str]:
        """
        Create sentence-aware, token-bounded chunks
        with optional sliding window overlap.
        """
        sentences = self.split_sentences(text)
        token_lengths = [self.count_tokens(s) for s in sentences]

        chunks = []
        start_idx = 0

        while start_idx < len(sentences):
            current_chunk = []
            current_token_count = 0

            for idx in range(start_idx, len(sentences)):
                if current_token_count + token_lengths[idx] > self.max_tokens:
                    break
                current_chunk.append(sentences[idx])
                current_token_count += token_lengths[idx]

            if not current_chunk:
                # Safety: single sentence exceeds max_tokens
                # Force include it to avoid infinite loop
                current_chunk.append(sentences[start_idx])
                start_idx += 1
            else:
                chunks.append(" ".join(current_chunk))
                start_idx += max(len(current_chunk) - self.overlap, 1)

        return chunks




import re
import nltk
import spacy
import numpy as np
import tiktoken as tk
from typing import List, Literal
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt", quiet=True)


class SemanticChunker:
    """
    Embedding-driven semantic / topic-based chunker using OpenAI embeddings.
    """

    def __init__(
        self,
        embedder,
        similarity_threshold: float = 0.75,
        max_tokens: int | None = None,
        sentence_splitter: Literal["regex", "nltk", "spacy"] = "spacy",
        token_encoding: str = "cl100k_base",
        spacy_model: str = "en_core_web_sm",
    ):
        self.embedder = embedder
        self.similarity_threshold = similarity_threshold
        self.max_tokens = max_tokens
        self.sentence_splitter = sentence_splitter

        self.encoding = tk.get_encoding(token_encoding)
        self._nlp = None
        self.spacy_model = spacy_model

    # ---------------------------
    # Sentence splitting
    # ---------------------------
    def _split_by_regex(self, text: str) -> List[str]:
        sentences = re.split(r"[.!?]", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_by_nltk(self, text: str) -> List[str]:
        return nltk.sent_tokenize(text)

    def _split_by_spacy(self, text: str) -> List[str]:
        if self._nlp is None:
            self._nlp = spacy.load(self.spacy_model)
        doc = self._nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    def split_sentences(self, text: str) -> List[str]:
        if self.sentence_splitter == "regex":
            return self._split_by_regex(text)
        elif self.sentence_splitter == "nltk":
            return self._split_by_nltk(text)
        elif self.sentence_splitter == "spacy":
            return self._split_by_spacy(text)
        else:
            raise ValueError("Unsupported sentence splitter")

    # ---------------------------
    # Token counting
    # ---------------------------
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    # ---------------------------
    # Semantic chunking
    # ---------------------------
    def chunk(self, text: str) -> List[str]:
        sentences = self.split_sentences(text)
        if not sentences:
            return []

        embeddings = self.embedder.embed(sentences)

        chunks = []
        current_chunk = [sentences[0]]
        current_tokens = self.count_tokens(sentences[0])

        for i in range(1, len(sentences)):
            sim = cosine_similarity(
                embeddings[i - 1].reshape(1, -1),
                embeddings[i].reshape(1, -1)
            )[0][0]

            next_tokens = self.count_tokens(sentences[i])

            # Topic boundary OR token limit
            if (
                sim < self.similarity_threshold
                or (self.max_tokens and current_tokens + next_tokens > self.max_tokens)
            ):
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
                current_tokens = next_tokens
            else:
                current_chunk.append(sentences[i])
                current_tokens += next_tokens

        chunks.append(" ".join(current_chunk))
        return chunks


