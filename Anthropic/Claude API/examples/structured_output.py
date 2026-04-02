"""
================================================================================
  Structured Output — 4 Methods Compared
  ---------------------------------------------------------------------------
  All four ways to get clean, parseable JSON from Claude:

  Method 1: Prefill + stop sequence   (what the lecture taught)
  Method 2: Prompt instruction only   (simplest, least reliable)
  Method 3: Prompt + json.loads hack  (parse by finding the JSON yourself)
  Method 4: Tool use / forced schema  (most reliable, most setup)

  Run:  python structured_output_methods.py
================================================================================
"""

import os
import re
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL  = "claude-haiku-4-5-20251001"

QUESTION = "Generate a very short EventBridge rule as JSON."
DIVIDER  = "\n" + "─" * 70 + "\n"


# ── shared helpers ────────────────────────────────────────────────────────────

def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages, stop_sequences=None):
    kwargs = dict(model=MODEL, max_tokens=300, messages=messages)
    if stop_sequences:
        kwargs["stop_sequences"] = stop_sequences
    response = client.messages.create(**kwargs)
    return response.content[0].text

def try_parse(label, text):
    """Try json.loads and print result or error."""
    try:
        parsed = json.loads(text.strip())
        print(f"  json.loads() result: VALID JSON")
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as e:
        print(f"  json.loads() result: FAILED — {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 1 — Prefill + Stop Sequence
#  (the technique from the lecture)
# ══════════════════════════════════════════════════════════════════════════════

def method_1_prefill_stop():
    messages = []
    add_user_message(messages, QUESTION)
    add_assistant_message(messages, "```json")          # prefill

    raw = chat(messages, stop_sequences=["```"])         # stop sequence

    # raw is already clean JSON — prefill stripped opening, stop stripped closing
    return raw


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 2 — Prompt instruction only
#  Just tell Claude in the prompt to return only JSON.
#  Simple, but Claude sometimes still adds commentary despite instructions.
# ══════════════════════════════════════════════════════════════════════════════

def method_2_prompt_only():
    messages = []
    add_user_message(messages,
        f"{QUESTION}\n\n"
        "IMPORTANT: Reply with raw JSON only. "
        "No markdown. No backticks. No explanation. "
        "Start your response with {{ and end with }}."
    )

    return chat(messages)


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 3 — Extract JSON from whatever Claude returns
#  Let Claude respond naturally, then find and extract the JSON yourself.
#  Useful when you cannot control the prompt or prefill.
# ══════════════════════════════════════════════════════════════════════════════

def method_3_extract():
    messages = []
    add_user_message(messages, QUESTION)

    raw = chat(messages)                                 # default response

    # Strategy A: strip markdown fences manually
    # Remove ```json ... ``` wrapper if present
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip()

    # Strategy B: find the first { and last } — grab everything between
    start = cleaned.find("{")
    end   = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        json_only = cleaned[start:end]
    else:
        json_only = cleaned

    return raw, json_only                                # return both for display


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 4 — Force JSON via tool use schema
#  Define a "tool" whose input shape IS your desired JSON schema.
#  Claude must call the tool, which forces it to output valid JSON.
#  Most reliable method — zero chance of markdown or commentary.
# ══════════════════════════════════════════════════════════════════════════════

def method_4_tool_schema():
    # Define a fake tool whose parameters match the JSON shape you want
    tool_schema = {
        "name": "output_rule",
        "description": "Output an EventBridge rule in structured format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {
                    "type":        "array",
                    "items":       {"type": "string"},
                    "description": "AWS service source, e.g. aws.ec2"
                },
                "detail-type": {
                    "type":        "array",
                    "items":       {"type": "string"},
                    "description": "Event detail type"
                },
                "detail": {
                    "type":        "object",
                    "description": "Event detail filters"
                }
            },
            "required": ["source", "detail-type", "detail"]
        }
    }

    response = client.messages.create(
        model    = MODEL,
        max_tokens = 300,
        tools    = [tool_schema],
        tool_choice = {"type": "tool", "name": "output_rule"},
        messages = [{"role": "user", "content": QUESTION}]
    )

    # Claude returns a tool_use block — extract .input which is already a dict
    for block in response.content:
        if block.type == "tool_use":
            return block.input                           # already a Python dict!

    return None

# ══════════════════════════════════════════════════════════════════════════════
#  langchain version
# ══════════════════════════════════════════════════════════════════════════════


from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# ── 1. Define the output shape as a Pydantic model ──────────────────────────
class EventBridgeRule(BaseModel):
    source: list[str]       = Field(description="AWS service source, e.g. aws.ec2")
    detail_type: list[str]  = Field(description="Event detail type", alias="detail-type")
    detail: dict            = Field(description="Event detail filters")

# ── 2. Create the model and bind the schema as a tool ───────────────────────
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

structured_llm = llm.with_structured_output(EventBridgeRule)

# ── 3. Invoke ────────────────────────────────────────────────────────────────
result = structured_llm.invoke(QUESTION)

# result is already an EventBridgeRule object — access fields directly
print(result.source)
print(result.detail)



# ══════════════════════════════════════════════════════════════════════════════
#  Run all four and compare
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("\n" + "═" * 70)
    print("  STRUCTURED OUTPUT — 4 METHODS COMPARED")
    print(f"  Question: {repr(QUESTION)}")
    print("═" * 70)

    # ── Method 1 ──────────────────────────────────────────────────────────────
    print(DIVIDER)
    print("METHOD 1 — Prefill + Stop Sequence")
    print("How it works:")
    print('  add_assistant_message(messages, "```json")   # pretend we started')
    print('  chat(messages, stop_sequences=["```"])        # halt at closing ```')
    print()
    r1 = method_1_prefill_stop()
    print("Raw response from Claude:")
    print(r1)
    try_parse("method 1", r1)
    print()
    print("Reliability:  High — backticks are structural, not stylistic")
    print("Setup effort: Low")

    # ── Method 2 ──────────────────────────────────────────────────────────────
    print(DIVIDER)
    print("METHOD 2 — Prompt instruction only")
    print("How it works:")
    print('  add_user_message(messages, QUESTION + "\\nReply with raw JSON only...")')
    print()
    r2 = method_2_prompt_only()
    print("Raw response from Claude:")
    print(r2)
    try_parse("method 2", r2)
    print()
    print("Reliability:  Medium — Claude usually obeys but sometimes adds text")
    print("Setup effort: Lowest (just words in your prompt)")

    # ── Method 3 ──────────────────────────────────────────────────────────────
    print(DIVIDER)
    print("METHOD 3 — Extract JSON from Claude's natural response")
    print("How it works:")
    print("  Let Claude respond normally, then find { ... } yourself with regex")
    print()
    raw3, extracted3 = method_3_extract()
    print("Raw response from Claude (unmodified):")
    print(raw3)
    print()
    print("After extraction (everything between first { and last }):")
    print(extracted3)
    try_parse("method 3", extracted3)
    print()
    print("Reliability:  Medium — breaks if JSON contains nested } at end")
    print("Setup effort: Low (a few lines of regex/string slicing)")

    # ── Method 4 ──────────────────────────────────────────────────────────────
    print(DIVIDER)
    print("METHOD 4 — Tool use with forced schema")
    print("How it works:")
    print("  Define a tool whose input_schema = the JSON shape you want.")
    print("  Set tool_choice to force Claude to always call it.")
    print("  Claude's tool arguments ARE the structured data — already a dict.")
    print()
    r4 = method_4_tool_schema()
    print("Response from Claude (block.input — already a Python dict):")
    print(json.dumps(r4, indent=2))
    print()
    print("Note: no json.loads() needed — it is already parsed!")
    print()
    print("Reliability:  Highest — Claude cannot produce invalid JSON here")
    print("Setup effort: High (must define tool schema upfront)")

    # ── Decision guide ────────────────────────────────────────────────────────
    print(DIVIDER)
    print("WHICH METHOD SHOULD YOU USE?")
    print()
    print("  Prompt only (Method 2)")
    print("  → Quick prototype, structure is simple, occasional failures ok")
    print()
    print("  Prefill + Stop (Method 1)  ← what the lecture taught")
    print("  → Good balance of reliability and simplicity")
    print("  → Best when you know the output starts with { or a code block")
    print()
    print("  Extract (Method 3)")
    print("  → You cannot change the prompt or add prefill")
    print("  → Parsing someone else's Claude output after the fact")
    print()
    print("  Tool schema (Method 4)")
    print("  → Production system, reliability is critical")
    print("  → Output shape is complex and must match a known schema exactly")
    print("  → You want a Python dict directly, skip json.loads() entirely")
    print("═" * 70 + "\n")
