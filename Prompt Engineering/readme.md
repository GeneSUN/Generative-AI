When it comes to prompt engineering, i divided into three categories:

- Controlled Behavior Prompting
- Superviced Learning
- f


## Instruction Prompting, 

- **What you want**: Explicitly tell the model how to behave.

- **what you do not want**: Explicit rules and restrictions.
```
    - Do not speculate
    - Cite sources
    - If uncertain, say "I don't know"
```

- **Role Prompting**
  ```python
      # old chatgpt 3.5
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

- https://colab.research.google.com/drive/1DwfVi6N9wDOLUNC0uVTI18BCHy-w0k51#scrollTo=b_Cq1tfrEAWS

### chain of thought


## *Optional

### Self-consistency sampling



