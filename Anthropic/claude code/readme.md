

Agent = LLM + Tools + Loop
- LLM — the "brain" that reasons, plans, and decides what to do next
- Tools — capabilities the LLM can invoke (read file, write file, run terminal command, search codebase, etc.)
- Loop — the agent keeps running (observe → think → act) until the task is done

1. LLM is a powerful reasoning engine. It understands intent, plans steps, and synthesizes information.
2. LLM has limitations: (1) Knowledge cutoff (outdated info); (2) Can't know your codebase, your files, your libraries; (3) Context window limits (can't hold everything at once)
3. This is exactly why agents and RAG exist — to extend the LLM by feeding it relevant tools/information on demand, rather than baking everything in upfront.
4. The LLM doesn't just use tools — it decides which tool to use and when. This autonomy is what separates an agent from a simple API call.
5. The loop is essential. Each tool result becomes new context that the LLM reasons over, potentially triggering more tool calls.
