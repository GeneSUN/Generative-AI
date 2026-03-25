[MultiChallenge: A Realistic Multi-Turn Conversation Evaluation Benchmark Challenging to Frontier LLMs](https://arxiv.org/pdf/2501.17399)

[LLMS GET LOST IN MULTI-TURN CONVERSATION](https://arxiv.org/pdf/2505.06120)


 this is widely discussed. Most prior evaluation studies have focused on classification or short-form tasks with more straightforward evaluation settings, because conversational trajectories in multi-turn settings diverge far more than in single-turn. arXiv A recent paper literally titled "LLMs Get Lost In Multi-Turn Conversation" (2025) quantified this: all top open- and closed-weight LLMs exhibit significantly lower performance in multi-turn conversations than single-turn, with an average drop of 39% across six generation tasks. OpenReview
Another benchmark paper, MultiChallenge (2025), found that despite achieving near-perfect scores on existing multi-turn evaluation benchmarks, all frontier models have less than 50% accuracy on MultiChallenge, with the top-performing Claude 3.5 Sonnet achieving just 41.4% average accuracy. arXiv This tells you that even the benchmarks themselves are still immature.

On your second question — common evaluation criteria:
The field has converged on a few major dimensions:
1. Context utilization & coherence
Conversations build meaning across turns, with references, pronouns, and implicit understanding that only emerge through sustained interaction. A model might perform well on isolated responses but struggle to maintain consistent personality, facts, or logical threads across multiple exchanges. Medium Coherence is typically scored as how well each response connects to and builds on the prior context.
2. The four MultiChallenge dimensions (probably the most concrete recent taxonomy):
Instruction retention (following constraints set in the first turn throughout the whole conversation), inference memory (recalling and connecting user information when responding to later turns), reliable versioned editing, and self-coherence (not contradicting what the model itself said in previous turns). ACL Anthology
3. Simulated user / LLM-as-judge
For the "can't replay history" problem you raised, the main practical workaround is: simulating a user with an LLM that has access to the entirety of a sharded instruction and is in charge of revealing information progressively during turns of the conversation. OpenReview This lets you construct reproducible conversation histories synthetically.
4. Practical criteria for your RAG chatbot specifically
Beyond the academic dimensions, for a RAG chatbot you'd typically evaluate:

Retrieval consistency across turns — does the system retrieve the right chunks when a question references a prior answer ("what did you just say about X")?
Coreference resolution — can it handle pronouns and ellipsis that depend on prior context?
Belief updating — if the user corrects the bot in turn 3, does it update cleanly or contradict itself later?
Context window degradation — as conversations extend, they may exceed model context windows, creating evaluation challenges that don't reflect real-world deployment constraints. Medium

