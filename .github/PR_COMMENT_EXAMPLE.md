# Devscope PR Comment Example

This is what the automated Devscope comment will look like on your pull requests.

---

## 🔍 Devscope Health Check

```
Devscope: B · Low risk · Easy onboarding · 0.78 tests · 0.82s ⚡
```

---
*Updated: Thu, 13 Feb 2026 14:52:33 GMT*

---

## How it works

1. Every time you open or update a PR, the workflow runs
2. Devscope analyzes your codebase
3. The bot posts (or updates) this comment with the latest health metrics
4. No spam — the same comment is updated each time

## Visual Example

```
┌─────────────────────────────────────────────────┐
│ 🔍 Devscope Health Check                        │
├─────────────────────────────────────────────────┤
│                                                 │
│ Devscope: B · Low risk · Easy onboarding ·      │
│           0.78 tests · 0.82s ⚡                  │
│                                                 │
│ ─────────────────────────────────────────────   │
│ Updated: Thu, 13 Feb 2026 14:52:33 GMT          │
└─────────────────────────────────────────────────┘
```

## Error Handling

If analysis fails, the comment will show:

```
## 🔍 Devscope Health Check

⚠️ **Analysis failed**

<details>
<summary>Error output</summary>

Error: Could not analyze repository
...
</details>

---
*Updated: Thu, 13 Feb 2026 14:52:33 GMT*
```

## Benefits

- ✅ **Automatic updates** — No comment spam
- ✅ **Instant visibility** — See health at a glance
- ✅ **Zero config** — Just add the workflow file
- ✅ **No secrets needed** — Works on public repos
- ✅ **Graceful degradation** — Errors don't block PRs
