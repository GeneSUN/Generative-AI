<img width="915" height="316" alt="image" src="https://github.com/user-attachments/assets/ec27c366-00b5-4871-b371-23d246f22e30" />

## ACE approach (3 roles)

### 1. Generator = “Do the task”

This is just the LLM answering: 

```
Generator output:

"Speed drop likely due to high airtime utilization (>80%) 
and weak RSSI (-75 dBm)"
```

### 2. Reflector = “What did we learn?”

Now another LLM (or same model, different role) looks at:
- question
- answer
- result (correct? wrong?)

This is NOT answering the question, It extracts generalizable knowledge

```
Insight:

"When airtime utilization > 75% AND RSSI < -70,
speed degradation is highly likely"

Failure:

"Forgot to check device reboot logs"
```

### 3. Curator = “Update the playbook”
Now we store knowledge into structured context

before: 
Playbook:
- Check RSSI
- Check throughput

After update:

Playbook (updated):

Rule 1:
If airtime_util > 75% AND RSSI < -70 → likely congestion issue

Rule 2:
Always check device reboot logs before concluding



### 🔁 Next question improves automatically
