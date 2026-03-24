## Claude Models

Anthropic offers three Claude model tiers, each balancing intelligence, cost, and speed differently.

| | **Claude Opus** | **Claude Sonnet** | **Claude Haiku** |
|:---|:---:|:---:|:---:|
| **Intelligence** | Highest | High | Moderate |
| **Speed** | Slower | Balanced | Fastest |
| **Cost** | Most expensive | Balanced | Most affordable |
| **Best for** | Complex, demanding tasks | General-purpose use | Fast, lightweight tasks |
| | ← More intelligent | | More efficient → |

![alt text](image-1.png)


## Create Messages

![alt text](image-2.png)

- model - The name of the Claude model you want to use
- max_tokens - A safety limit on response length (not a target)
- messages - The conversation history you're sending to Claude


## Multi-Turn Conversation

![alt text](image-3.png)
You can imagine the chat as a list passed back and forth between user and llm/assistant: each turn, one role add a dictionary to the list
- User messages - Content you want to send to Claude (written by humans)
- Assistant messages - Responses that Claude has generated


```python
messages = [
    {"role": "user",      "content": "Generate a JSON rule"},
    {"role": "assistant", "content": "```json\n{ ... }\n```"},
    {"role": "user",      "content": "Make it shorter"},
]
```

**Memory**


## System Prompts

![alt text](image-4.png)

## Structured Response

By default, when you ask Claude to generate JSON, you might get something like this:
```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"]
  }
}
```
The JSON is correct, but it's wrapped in markdown formatting and includes explanatory text. 

### The Solution: Assistant Message Prefilling + Stop Sequences

| Method | How | Reliability | Effort |
|:---|:---|:---:|:---:|
| Prompt only | Tell Claude "return raw JSON only, no backticks" | Medium — usually works, sometimes adds text | Lowest |
| Prefill + stop | Prefill ` ```json `, stop at ` ``` ` | High | Low |
| Extract after the fact | Let Claude respond freely, find `{...}` with regex | Medium — breaks on edge cases | Low |
| Tool schema | Define a tool whose input shape IS your JSON | Highest — Claude cannot produce invalid JSON | High |






