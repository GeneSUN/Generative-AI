**Workflow — the structure of how the agent thinks and acts**

Workflow is the skeleton: it defines how information flows, when decisions are made, and what runs in sequence versus in parallel. Without a workflow, you have a prompt. With a workflow, you have a system.

Common patterns:

- **Prompt chaining** — break a complex task into sequential steps, each feeding the next
- **Routing** — classify the input and direct it to the right specialist
- **Parallelization** — run independent subtasks concurrently, then merge
- **Orchestrator-worker** — a coordinating agent delegates to specialized sub-agents
- **Evaluator-optimizer** — one agent critiques and refines another's output

The workflow doesn't care what tools exist. It defines *when* and *how* the agent decides to act.
