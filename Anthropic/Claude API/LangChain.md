# Raw API vs LangChain

Two approaches to managing multi-turn conversation history with Claude — one manual, one abstracted.

---

## Approach 1 — Raw Anthropic API

The raw API requires you to maintain the message history yourself. Each call receives the full conversation so far, and you manually append both user and assistant turns after each exchange.

```python
from anthropic import Anthropic

client = Anthropic()
model  = "claude-sonnet-4-6"

# ── helper functions ──────────────────────────────────────────────────────────

def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages):
    response = client.messages.create(
        model      = model,
        max_tokens = 1000,
        messages   = messages,      # full history sent every time
    )
    return response.content[0].text

# ── usage ─────────────────────────────────────────────────────────────────────

messages = []

add_user_message(messages, "Define quantum computing in one sentence")
answer = chat(messages)
add_assistant_message(messages, answer)

add_user_message(messages, "Write another sentence")
final_answer = chat(messages)
add_assistant_message(messages, final_answer)

print(final_answer)
```

---

## Approach 2 — LangChain with ConversationBufferMemory

LangChain wraps the model and memory into a `ConversationChain`, handling history automatically. You just call `chain.predict()` — no manual message tracking needed.

```python
# pip install langchain langchain-anthropic

from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# ── set up model + memory ─────────────────────────────────────────────────────

llm = ChatAnthropic(
    model      = "claude-sonnet-4-6",
    max_tokens = 1000,
    api_key    = "your-api-key",
)

memory = ConversationBufferMemory(
    return_messages = True,     # store as message objects, not plain text
)

chain = ConversationChain(
    llm    = llm,
    memory = memory,
    verbose = True,             # prints the full prompt each time, good for learning
)

# ── usage — same conversation, much less manual work ─────────────────────────

answer       = chain.predict(input="Define quantum computing in one sentence")
final_answer = chain.predict(input="Write another sentence")

print(final_answer)

# inspect what memory holds
print(memory.chat_memory.messages)
```

### Other Memory Types

LangChain offers several memory strategies depending on how much history you want to retain:

```python
from langchain.memory import (
    ConversationBufferMemory,        # keeps ALL messages — same as raw API
    ConversationBufferWindowMemory,  # keeps only last K turns
    ConversationSummaryMemory,       # summarises old turns to save tokens
    ConversationSummaryBufferMemory, # summarises once history exceeds token limit
)

# Example: only keep last 3 turns
memory = ConversationBufferWindowMemory(k=3, return_messages=True)

# Example: auto-summarise when history gets long
memory = ConversationSummaryBufferMemory(
    llm          = llm,
    max_token_limit = 500,      # summarise once history exceeds 500 tokens
    return_messages = True,
)
```

---

## LangChain vs Raw API

| | Raw API | LangChain |
|:---|:---:|:---:|
| **Ease of use** | Verbose | Simple |
| **Debuggability** | Easy | Difficult |
| **Production-ready** | Manual setup | Built-in abstractions |

## Recommendation

1. **Start with the Raw API** to understand the underlying message flow and debug with full visibility.
2. **Migrate to LangChain for production** to leverage its built-in abstractions for cleaner, more maintainable code.
   - If compatibility issues arise, rolling back to the raw API is straightforward.
