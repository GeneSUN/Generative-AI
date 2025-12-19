When it comes to prompt engineering, i divided into three categories:

- Controlled Behavior Prompting
- Superviced Learning
- f


## Controlled Behavior Prompting, 

- Instruction Prompting

  Explicitly tell the model how to behave.

- Constraint-Based Prompting

  Explicit rules and restrictions.
```
    - Do not speculate
    - Cite sources
    - If uncertain, say "I don't know"
```

- Role Prompting
  ```python
      resp = client.chat.completions.create(
          model=model,
          messages=[
              {"role": "system", "content": system_msg},
              {"role": "user", "content": user_msg},
          ],
          temperature=temperature,
          max_tokens=max_tokens,
          logit_bias=logit_bias,
      )
  ```

## Template Learning

### zero-shot

### few-shot

### chain of thought

### Self-consistency sampling



