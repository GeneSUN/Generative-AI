# Context Engineering for Personalization: State Management with Long-Term Memory



- [Context Engineering for Personalization - State Management with Long-Term Memory Notes using OpenAI Agents SDK](https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization)


- [Context Engineering - Short-Term Memory Management with Sessions from OpenAI Agents SDK](https://developers.openai.com/cookbook/examples/agents_sdk/session_memory?utm_source=chatgpt.com)


<hr style="border: 2px solid #555;">




## Reverse Engineering ChatGPT Memory: Four-Layer Architecture

> https://llmrefs.com/blog/reverse-engineering-chatgpt-memory

ChatGPT's memory system is composed of four distinct layers, each with different persistence scope and purpose.

| Layer | Name | Persistence | Purpose |
|---|---|---|---|
| 1 | Session Metadata | Session-only | Environmental context |
| 2 | User Memory | Permanent | Persistent facts about the user |
| 3 | Recent Conversation Summaries | Semi-persistent | Lightweight history across ~15 sessions |
| 4 | Current Session Messages | In-context | Full active transcript |

---

<details>
<summary><strong>Layer 1: Session Metadata</strong></summary>

Temporary contextual information that exists only for the duration of the current session. Vanishes when the session ends.

| What it contains | Examples |
|---|---|
| Device & browser | Safari on macOS, Chrome on Windows |
| Location & timezone | UK, UTC+1, 2:30 PM |
| Subscription & usage | Pro plan, daily user |
| Display preferences | Dark mode, preferred model |

> Enables the system to tailor responses to current circumstances without storing anything permanently.

</details>

<details>
<summary><strong>Layer 2: User Memory</strong></summary>

Persistent facts that follow the user across all conversations. Does not reset between sessions.

**How facts get stored — two triggers:**

1. **Explicit request** — user says "Remember that I prefer Python"
2. **Auto-detection** — ChatGPT notices something important and receives user confirmation

**What gets stored (real example — 33 facts for one user):**

- Name, age, career background
- Current projects and study topics
- Fitness habits and personal preferences

**Key design decisions:**
- Users can delete any stored fact at any time
- Memory requires deliberate action — it does **not** silently learn from every interaction

> This is not secret profiling. Storage is transparent and user-controlled.

</details>

<details>
<summary><strong>Layer 3: Recent Conversation Summaries</strong></summary>

Lightweight summaries of approximately 15 recent conversations, rather than full transcripts.

**Summary format — captures only:**
- User contributions (not assistant responses)
- A brief note on the topic

**Example entry:**
> "Dec 8, 2025: Building a load balancer in Go — asked about connection pooling."

**Design tradeoff:**

| Approach | Latency | Depth |
|---|---|---|
| Full retrieval over all history | High | Deep |
| Lightweight summaries (~15 sessions) | Low | Shallow |

> Prioritizes speed over depth — avoids the latency of searching through thousands of archived messages.

</details>

<details>
<summary><strong>Layer 4: Current Session Messages</strong></summary>

The full, uncompressed transcript of the ongoing conversation, loaded directly into the context window.

**Trimming behavior when token limits are hit:**

| What gets trimmed first | What persists |
|---|---|
| Recent session messages | Permanent user facts (Layer 2) |
| | Conversation summaries (Layer 3) |

> Reveals OpenAI's prioritization: long-term personalization is preserved over immediate in-session context when space is scarce.

</details>
