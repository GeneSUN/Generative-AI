# Tool Use with Claude

Tools are what separate an agent from a static workflow.
- A **static workflow** follows a predetermined path — if-else branches, case-when routing, fixed sequences.
- An **agent** (1). reasons about which action to take at each step and (2). updates that reasoning based on what it observes; tools are the actions it can take.

---

## Part 1 — What Is a Tool and How an Agent Uses It



<details>
<summary><b>What is a tool</b></summary>

```
┌─────────────────────────────────────────────────────────┐
│                        TOOL SCHEMA                      │
│                                                         │
│  name           ◄────────────────┐                      │
│  description    ◄────────────────┼──┐                   │
│  input_schema   ◄────────────────┼──┼──┐                │
│  input_examples                  │  │  │                │
│                                  │  │  │                │
│  ┌────────────────────────────── │──│──│──────────────┐ │
│  │         TOOL FUNCTION         │  │  │              │ │
│  │                               │  │  │              │ │
│  │  def function_name(...):  ────┘  │  │              │ │
│  │      """docstring"""  ───────────┘  │              │ │
│  │      (param: type, ...)  ───────────┘              │ │
│  │                                                    │ │
│  │      # function body                               │ │
│  │      ...                                           │ │
│  │      return result                                 │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

</details>


<details>
<summary><b>How the agent uses tools: The five-step sequence</b></summary>

Once the schema is defined, the agent reads it, reasons about which tool fits the current step, invokes it, and feeds the result back into the next reasoning step. Claude does not store conversation history, so every tool result must be passed back alongside the full message history.

<details>
<summary>1. Send the request — let the model decide which tool to use</summary>

```python
message = client.messages.create(
    model=model,
    max_tokens=1000,
    tools=[add_duration_to_datetime_schema],
    messages=[{"role": "user", "content": "What is 10 days from March 24, 2026?"}],
)
```

</details>

<details>
<summary>2. Receive the assistant message — text block + tool use block</summary>

When Claude decides to use a tool, it returns an assistant message with multiple content blocks. Extract the `id` and `input` from the tool use block:

```python
[ToolUseBlock(id='toolu_015vDN6vQyFSzWZj77TUujcz',
                input={'datetime_str': '2026-03-24', 'duration': 10, 'unit': 'days'},
                name='add_duration_to_datetime',
                type='tool_use')]
```

</details>

<details>
<summary>3. Extract tool information and execute the function</summary>

```python
for block in message.content:
    if block.type == "text":
        print(block.text)          # e.g. "I'll calculate that for you."

    elif block.type == "tool_use":
        print(block.name)          # "add_duration_to_datetime"
        print(block.id)            # "toolu_01..." ← needed to send result back
        print(block.input)         # {"datetime_str": "2026-03-24", "duration": 10, "unit": "days"}
```

</details>

<details>
<summary>4. Send the tool result back with the full conversation history</summary>

```python
final = client.messages.create(
    model=model,
    max_tokens=1000,
    tools=[add_duration_to_datetime_schema],
    messages=[
        {"role": "user", "content": "What is 10 days from March 24, 2026?"},
        {"role": "assistant", "content": message.content},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_block.id, "content": tool_result}]},
    ],
)
```

</details>

<details>
<summary>5. Loop until the model stops calling tools</summary>

```python
def run_conversation(messages):
    while True:
        response = chat(
            messages,
            tools=[
                get_current_datetime_schema,
                add_duration_to_datetime_schema,
                set_reminder_schema,
            ],
        )

        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages
```

</details>

</details>

---

## Part 2 — Designing Tools for Agents


<details>
<summary><b>1. Name and description are the most important fields</b></summary>

The name is what the agent sees first when scanning a list of tools. Before reading any description, the name alone should communicate:
- What service this belongs to
- What resource it operates on
- What action it performs

The description fills in *when* to use the tool and what to expect from it. A vague description forces the agent to guess — and it will guess wrong.

<details>
<summary><b>Prompt template — generate a tool schema from function code</b></summary>

```
I have defined a Python tool function below. Please write a valid JSON schema specification for the purposes of tool calling with Claude.

Ensure the schema includes:

- A clear name for the tool.
- A descriptive description (3-4 sentences) explaining what the tool does and when to use it.
- An input_schema that defines all function arguments, their types, and descriptions.
- A list of required parameters.

Here is the function code:

<tool_function_code>
[PASTE YOUR FUNCTION CODE HERE]
</tool_function_code>

Please format the output so I can directly use it in my tools list for the Claude API.
```

</details>

</details>

<details>
<summary><b>2. Control what your tool returns</b></summary>

When a tool returns data, the agent reads everything. Noisy, technical, or irrelevant fields waste context and increase the chance of confusion or hallucination.

**The UUID problem** — UUIDs like `a3f9b2c1-4d5e-6789` are meaningless to an LLM. They look like noise, and the agent is more likely to misremember or hallucinate them. Replacing UUIDs with readable identifiers directly reduces errors.

Return only what the agent needs to reason about the next step.

</details>

<details>
<summary><b>3. Prototype fast, then refine from real use</b></summary>

Build a minimal version and observe how the agent actually uses it before investing in a polished implementation.

- **List contacts** — you may discover the agent never needs a full list; `search_contacts` or `message_contact` covers the real workflows
- **Read file** — a quick version that reads any path quickly reveals that the agent hits token limits on large files; add a line-count limit parameter

Real usage reveals what the agent actually needs, which is often different from what seemed necessary upfront.

</details>

<details>
<summary><b>4. Evaluate tool use, not just task output</b></summary>

- Collect metrics beyond accuracy: total tool calls, runtime per call, token consumption, tool errors
- Track which tools the agent calls together — common co-occurrence patterns are candidates for consolidation into a single tool
- In evaluation prompts, instruct the agent to output reasoning before tool calls; this triggers chain-of-thought and makes tool selection legible and debuggable

</details>

→ [Tool evaluation cookbook](https://platform.claude.com/cookbook/tool-evaluation-tool-evaluation) · [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
