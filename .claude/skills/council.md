# LLM Council: Full Documentation

## Overview

The LLM Council is a decision-making framework that runs questions through five independent AI advisors with different thinking styles. They peer-review each other anonymously, and a chairman synthesizes their outputs into a final verdict.

## When to Use the Council

The council works best for high-stakes decisions with genuine uncertainty:

**Good council questions:** Strategic pivots, pricing decisions, positioning choices, hiring trade-offs, copy evaluation

**Bad council questions:** Factual lookups, simple creation tasks, yes/no questions without meaningful trade-offs

Triggers include: "council this," "run the council," "should I X or Y," "which option," "validate this"

## The Five Advisors

Each represents a distinct thinking lens:

1. **The Contrarian** — hunts for fatal flaws and what could fail
2. **The First Principles Thinker** — questions assumptions and reframes problems
3. **The Expansionist** — identifies upside and missed opportunities
4. **The Outsider** — brings fresh perspective without domain expertise
5. **The Executor** — focuses on practical implementation and first steps

These five create natural tensions: Contrarian vs Expansionist (downside vs upside), First Principles vs Executor (rethinking vs doing), with the Outsider maintaining objectivity.

## Session Structure

**Step 1:** Enrich the question with workspace context (CLAUDE.md, memory files, past decisions) and frame it neutrally

**Step 2:** Spawn all five advisors in parallel (150-300 words each, thinking independently)

**Step 3:** Conduct peer review—each advisor reviews all anonymized responses and identifies strongest arguments, biggest blind spots, and collective gaps

**Step 4:** Chairman synthesizes into final verdict covering agreement points, disagreements, blind spots, recommendation, and one concrete next step

**Step 5:** Present verdict in chat using markdown (no HTML files)

**Step 6:** Save transcript only if significant

## Key Principles

- Always run advisors in parallel, not sequentially
- Anonymize responses before peer review
- Chairman can disagree with majority if reasoning supports it
- Avoid counciling trivial questions with single right answers
- Keep output scannable with bullet points
