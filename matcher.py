#!/usr/bin/env python3
"""
Mini intro matcher — Key AI take-home (Part 1)
Usage:  python matcher.py "your query here"
Requires: ANTHROPIC_API_KEY environment variable  (pip install anthropic)
"""

import json
import sys
import anthropic

PROFILES = [
    {"id": 1, "name": "Priya",  "desc": "Staff Engineer, fintech | Python, payments, Kafka | Bangalore"},
    {"id": 2, "name": "Daniel", "desc": "Product Designer | Figma, design systems, mobile | San Francisco"},
    {"id": 3, "name": "Mei",    "desc": "Backend Engineer | Go, payments, Postgres | Singapore"},
    {"id": 4, "name": "Arjun",  "desc": "ML Engineer | PyTorch, ranking, recommendations | Palo Alto"},
    {"id": 5, "name": "Sofia",  "desc": "Founder, climate tech | fundraising, ops, hiring | London"},
    {"id": 6, "name": "Wei",    "desc": "Full-stack Engineer | TypeScript, React, Stripe | Singapore"},
]

PROFILE_LIST = "\n".join(f"{p['id']}. {p['name']}: {p['desc']}" for p in PROFILES)
MIN_SCORE = 20  # below this we consider it "no meaningful match"


def find_matches(query: str) -> list[dict]:
    if not query.strip():
        return []

    client = anthropic.Anthropic()
    prompt = (
        f'Networking request: "{query}"\n\n'
        f"Score each profile 0-100 for relevance. "
        f"Return JSON only — top 3 as:\n"
        f'[{{"id":<int>,"name":"<str>","score":<int>,"reason":"<one sentence why>"}}]\n\n'
        f"Profiles:\n{PROFILE_LIST}"
    )

    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        results = json.loads(msg.content[0].text)
        return sorted(
            [r for r in results if r.get("score", 0) >= MIN_SCORE],
            key=lambda x: x["score"],
            reverse=True,
        )[:3]
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "I need a backend engineer who has worked on payments"

    if not query.strip():
        print('Usage: python matcher.py "your query here"')
        return

    print(f"Query: {query}\n")
    results = find_matches(query)

    if not results:
        print("No matches found.")
        return

    for rank, m in enumerate(results, 1):
        print(f"#{rank}  {m['score']:>3}/100  {m['name']}")
        print(f"       {m['reason']}\n")


if __name__ == "__main__":
    main()
