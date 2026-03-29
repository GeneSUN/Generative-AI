log customer question and response, more importantly, customer feedback.

x->y_predicted, y_actual label 1/0


1. use thumbs-up/down as an online product-health metric

2. mine thumbs-down cases to find failure patterns by query type, source, customer segment, or retriever/prompt/model version
Build slice-based monitoring
Do not only track overall thumbs-up rate. Break it down by:
- query type
- topic/domain
- customer segment
- retriever version
- prompt version
- model version
- source corpus
- top-K / reranker setting

3. Create **labeled datasets** for improvement
Thumb feedback is weak supervision, but still useful for constructing better datasets:
- downvoted + bad retrieval → query / positive chunk / negative chunk data for reranker tuning
- downvoted + good retrieval but bad answer → prompt or answer-rewrite training examples
- downvoted + insufficient evidence but model still answered → refusal / “I don’t know” training examples
- upvoted examples → preference/style examples, and maybe high-quality answer exemplars after filtering

Use it for active learning
A very practical loop is:
- collect downvoted cases
- cluster them by failure mode
- manually label a small subset
- use those labeled cases to improve chunking, reranking, prompting, or refusal behavior
- redeploy and compare the same slices again








