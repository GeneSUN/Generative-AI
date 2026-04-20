# Tool Use with Claude

## Overview

1. LLMs are powerful reasoning engines. They understand intent, plan steps, and synthesize information.
2. LLMs have inherent limitations: (1) Knowledge cutoff (outdated information); (2) No awareness of your codebase, files, or libraries; (3) Context window constraints (can't hold everything at once).
3. This is precisely why agents and RAG exist
    - The LLM doesn't merely use tools — it decides which tool to use and when. This autonomy is what distinguishes an agent from a simple API call.
    - to extend the LLM by supplying relevant tools and information on demand, rather than embedding everything upfront.
4. The loop is essential. Each tool result becomes new context that the LLM reasons over, potentially triggering further tool calls.


## What is a tool, and how to build one

<details>
<summary>Tool function — it can be a function, a class, or an API call</summary>

- **Use descriptive names**: Both your function name and parameter names should clearly indicate their purpose.
- **Validate inputs**: Check that required parameters are not empty or invalid, and raise errors when they are.
- **Provide meaningful error messages**: Claude can read error messages and may retry the function call with corrected parameters.

</details>

<details>
<summary>Tool schema</summary>

A complete tool specification has three main parts:

- **name** — A clear, descriptive name for your tool (e.g., `get_weather`)
- **description** — What the tool does, when to use it, and what it returns
    - Aim for 3–4 sentences explaining what the tool does
    - Describe when Claude should use it
    - Explain what kind of data it returns
    - Provide detailed descriptions for each argument
- **input_schema** — The JSON schema describing the function's arguments

#### The Easy Way to Generate Schemas
Instead of writing JSON schemas from scratch, you can use Claude itself to generate them. Here is the process:

**Prompt template** =
```python

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


## Tool loops — how the LLM decides which tools to use and how tools interact with it

Claude does not store conversation history — you must manage it manually. When working with tool responses, you must preserve the entire content structure, including all blocks (tools Managing Conversation History with Multi-Block Messages).

The tool usage process follows this pattern:

<details>
<summary>1. Send tool request to model, let it decide which tool to use</summary>

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
<summary>2. Receive the assistant message containing a text block and a tool use block</summary>

When Claude decides to use a tool, it returns an assistant message with multiple blocks in the content list. You should extract the block `id` and input from the tool use block:

**Message blocks**
```python
[ToolUseBlock(id='toolu_015vDN6vQyFSzWZj77TUujcz',
                caller=DirectCaller(type='direct'),
                input={'datetime_str': '2026-03-24', 'duration': 10, 'unit': 'days'}, name='add_duration_to_datetime',
                type='tool_use')]
```

</details>

<details>
<summary>3. Extract tool information and execute the actual function</summary>

```
# Loop through content blocks
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
<summary>4. Send tool result back to Claude along with complete conversation history</summary>

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
<summary>5. Receive final response from Claude, stop the tool-loop</summary>

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
