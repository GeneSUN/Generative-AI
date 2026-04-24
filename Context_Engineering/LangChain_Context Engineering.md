https://www.langchain.com/blog/context-engineering-for-agents

Context engineering is the art and science of filling the context window with just the right information at each step of an agent’s trajectory. In this post, we break down some common strategies — write, select, compress, and isolate — for context engineering by reviewing various popular agents and papers. 

![alt text](image-2.png)



Context Engineering


As Andrej Karpathy puts it, LLMs are like a new kind of operating system:

| Component | Analogy | Role |
|---|---|---|
| **LLM** | CPU | The reasoning core — processes instructions and computes outputs, but holds no state of its own |
| **Context window** | RAM | The working memory — fast and immediately accessible, but limited in capacity |
| **Context engineering** | OS | The memory manager — curates what fits into RAM, scheduling the right information at the right time |

