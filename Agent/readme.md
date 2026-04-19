

## Skill Metadata Fields

The agent skills open standard supports several fields in the SKILL.md frontmatter. Two are required, and the rest are optional:

- `name` (required) — Identifies your skill. Use lowercase letters, numbers, and hyphens only. Maximum 64 characters. Should match your directory name.
- `description` (required) 
    - What does the skill do?
    - When should Claude use it?
- `allowed-tools` (optional) — Restricts which tools Claude can use when the skill is active.
- `model` (optional) — Specifies which Claude model to use for the skill.

## Progressive Disclosure

The pattern is identical at every layer: a lightweight index that points to heavy details, loaded only when relevant.

The naive approach — dump everything into one file:
```
database/
  SKILL.md   ← 1,800 lines containing EVERYTHING
```

The Progressive Disclosure approach
```
database/
  SKILL.md                          ← ~200 lines, essential only
  references/
    schema-reference.md             ← all table definitions, 600 lines
    query-optimization-guide.md     ← indexing rules, explain plans, 400 lines
    migration-procedures.md         ← how to write safe migrations, 300 lines
  scripts/
    validate_query.py               ← script to dry-run a query
    generate_migration.py           ← scaffolds migration files
```



## Quick Troubleshooting Checklist

- Not triggering? Improve your description and add trigger phrases.
- Not loading? Check your path, file name, and YAML syntax.
- Wrong skill used? Make descriptions more distinct from each other.
- Being shadowed? Check the priority hierarchy and rename if needed.
- Plugin skills missing? Clear cache and reinstall.
- Runtime failure? Check dependencies, permissions, and paths.



## Reference

- https://www.anthropic.com/engineering/building-effective-agents
- https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf?utm_source=enterpriseaiexecutive.ai&utm_medium=referral&utm_campaign=deloitte-s-ai-playbook-for-cxos
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills



