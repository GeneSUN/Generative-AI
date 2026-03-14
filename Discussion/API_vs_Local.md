## 1️⃣ What most companies actually do

###  Most companies start with APIs.
- Example APIs: OpenAI/Anthropic (Claude)/Google Gemini/AWS Bedrock;
- Comes with huge models/scaling/reliability/no infrastructure

APIs are considered the easiest path because they provide state-of-the-art models with minimal engineering effort

### What large companies often do later

1. Cost: API pricing is token-based.
2. Privacy
3. Customization

```
HYBRID Solution:
Local LLM → internal tasks
API LLM → difficult queries
```

### What researchers usually do
1. reproducibility
2. access to logits / probabilities
- token logits
- attention weights
- hidden states
3. ability to modify models <p>

Open Source vs Industry giants
- The trend in 2024-2025 is that open source models (LLaMA 3, Mistral, Qwen) have closed the quality gap significantly against GPT-4 for specific tasks. 
- This is pushing more companies toward self-hosting than two years ago — but API access still dominates simply because it is so much easier to operate.



















