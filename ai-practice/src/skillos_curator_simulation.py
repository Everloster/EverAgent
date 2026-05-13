#!/usr/bin/env python3
"""Small deterministic simulation inspired by SkillOS skill curation.

This is not a reproduction of the paper's LLM+GRPO training system. It is a
CPU-friendly teaching experiment that keeps the key interface:

1. grouped task streams expose reusable dependencies
2. an executor retrieves skills from SkillRepo before solving each task
3. a curator inserts, updates, or deletes Markdown-like skills after execution
4. downstream tasks reveal whether earlier curation was useful
"""

from __future__ import annotations

import argparse
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Task:
    id: str
    group: str
    tags: tuple[str, ...]
    pitfalls: tuple[str, ...]
    difficulty: int


@dataclass
class Skill:
    name: str
    tags: set[str]
    pitfalls: set[str]
    uses: int = 0
    successes: int = 0
    revisions: int = 0

    def matches(self, task: Task) -> int:
        return len(self.tags.intersection(task.tags)) + 2 * len(self.pitfalls.intersection(task.pitfalls))

    @property
    def utility(self) -> float:
        if self.uses == 0:
            return 0.0
        return self.successes / self.uses


@dataclass
class SkillRepo:
    skills: dict[str, Skill] = field(default_factory=dict)
    operations: Counter = field(default_factory=Counter)

    def retrieve(self, task: Task, top_k: int) -> list[Skill]:
        ranked = sorted(
            self.skills.values(),
            key=lambda skill: (skill.matches(task), skill.utility, skill.revisions),
            reverse=True,
        )
        return [skill for skill in ranked if skill.matches(task) > 0][:top_k]

    def insert(self, task: Task) -> None:
        name = f"{task.group}_skill"
        if name in self.skills:
            return
        self.skills[name] = Skill(name=name, tags=set(task.tags), pitfalls=set(task.pitfalls))
        self.operations["insert"] += 1

    def update(self, task: Task, related: Skill) -> None:
        before = (len(related.tags), len(related.pitfalls))
        related.tags.update(task.tags)
        related.pitfalls.update(task.pitfalls)
        related.revisions += 1
        after = (len(related.tags), len(related.pitfalls))
        if after != before:
            self.operations["update"] += 1

    def delete_low_utility(self, min_uses: int, min_utility: float) -> None:
        delete_names = [
            name
            for name, skill in self.skills.items()
            if skill.uses >= min_uses and skill.utility < min_utility
        ]
        for name in delete_names:
            del self.skills[name]
            self.operations["delete"] += 1

    def token_cost(self) -> int:
        return sum(18 + 6 * len(skill.tags) + 8 * len(skill.pitfalls) for skill in self.skills.values())


@dataclass
class RunResult:
    policy: str
    total: int
    solved: int
    steps: int
    skill_tokens: int
    repo_size: int
    operations: Counter
    group_success: dict[str, tuple[int, int]]

    @property
    def success_rate(self) -> float:
        return self.solved / self.total

    @property
    def avg_steps(self) -> float:
        return self.steps / self.total


def build_grouped_tasks(groups: int, tasks_per_group: int, seed: int) -> list[Task]:
    rng = random.Random(seed)
    task_groups = {
        "alfworld_heat": ("heat", "container", "state_change", "avoid_wrong_object"),
        "alfworld_clean": ("clean", "sink", "state_change", "verify_state"),
        "webshop_filter": ("filter", "price", "attribute_match", "avoid_decoy"),
        "reasoning_verify": ("decompose", "equation", "verify_answer", "edge_case"),
        "reasoning_count": ("counting", "case_split", "verify_answer", "off_by_one"),
    }
    names = list(task_groups)[:groups]
    tasks: list[Task] = []
    for group_name in names:
        signature = task_groups[group_name]
        for index in range(tasks_per_group):
            shared = signature[:2]
            late = signature[2 + (index % 2)]
            distractor = rng.choice(["format", "navigation", "constraint", "fallback"])
            tags = tuple(dict.fromkeys((*shared, late, distractor)))
            pitfalls = (late, signature[-1])
            difficulty = 4 + (index % 3)
            tasks.append(
                Task(
                    id=f"{group_name}_{index + 1:02d}",
                    group=group_name,
                    tags=tags,
                    pitfalls=pitfalls,
                    difficulty=difficulty,
                )
            )
    return tasks


def shuffled_tasks(tasks: list[Task], seed: int) -> list[Task]:
    rng = random.Random(seed)
    result = list(tasks)
    rng.shuffle(result)
    return result


def execute(task: Task, skills: list[Skill], rng: random.Random) -> tuple[bool, int]:
    coverage = sum(skill.matches(task) for skill in skills)
    max_coverage = max(1, len(task.tags) + 2 * len(task.pitfalls))
    skill_bonus = min(0.42, 0.08 * coverage)
    overload_penalty = max(0, len(skills) - 2) * 0.05
    base_success = 0.42 + 0.02 * (6 - task.difficulty)
    probability = max(0.05, min(0.95, base_success + skill_bonus - overload_penalty))
    solved = rng.random() < probability
    steps = max(2, task.difficulty + 4 - min(4, coverage) + len(skills))
    return solved, steps


def run_policy(tasks: list[Task], policy: str, seed: int, top_k: int) -> RunResult:
    rng = random.Random(seed)
    repo = SkillRepo()
    solved = 0
    steps = 0
    group_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for task in tasks:
        retrieved = [] if policy == "no_memory" else repo.retrieve(task, top_k=top_k)
        ok, task_steps = execute(task, retrieved, rng)
        solved += int(ok)
        steps += task_steps
        group_counts[task.group][0] += int(ok)
        group_counts[task.group][1] += 1

        for skill in retrieved:
            skill.uses += 1
            skill.successes += int(ok)

        if policy == "no_memory":
            continue
        if policy == "raw_memory":
            repo.skills[f"{task.id}_trace"] = Skill(
                name=f"{task.id}_trace",
                tags=set(task.tags),
                pitfalls=set(task.pitfalls),
            )
            repo.operations["insert"] += 1
            continue

        related = repo.retrieve(task, top_k=1)
        if not related:
            repo.insert(task)
        elif ok:
            repo.update(task, related[0])
        else:
            repo.insert(task)
            repo.update(task, related[0])
        repo.delete_low_utility(min_uses=3, min_utility=0.34)

    return RunResult(
        policy=policy,
        total=len(tasks),
        solved=solved,
        steps=steps,
        skill_tokens=repo.token_cost(),
        repo_size=len(repo.skills),
        operations=repo.operations,
        group_success={group: (values[0], values[1]) for group, values in sorted(group_counts.items())},
    )


def print_table(title: str, rows: list[dict[str, str]]) -> None:
    headers = list(rows[0])
    widths = {header: max(len(header), *(len(row[header]) for row in rows)) for header in headers}
    print(f"\n== {title} ==")
    print(" | ".join(header.ljust(widths[header]) for header in headers))
    print("-+-".join("-" * widths[header] for header in headers))
    for row in rows:
        print(" | ".join(row[header].ljust(widths[header]) for header in headers))


def summarize(results: list[RunResult]) -> None:
    rows = []
    for result in results:
        rows.append(
            {
                "policy": result.policy,
                "success_rate": f"{result.success_rate:.3f}",
                "avg_steps": f"{result.avg_steps:.2f}",
                "repo_size": str(result.repo_size),
                "skill_tokens": str(result.skill_tokens),
                "insert": str(result.operations["insert"]),
                "update": str(result.operations["update"]),
                "delete": str(result.operations["delete"]),
            }
        )
    print_table("policy comparison", rows)

    grouped_rows = []
    skillos = next(result for result in results if result.policy == "skillos_heuristic")
    for group, (ok, total) in skillos.group_success.items():
        grouped_rows.append({"group": group, "success": f"{ok}/{total}", "rate": f"{ok / total:.3f}"})
    print_table("SkillOS-style grouped stream details", grouped_rows)


def run(args: argparse.Namespace) -> None:
    grouped = build_grouped_tasks(args.groups, args.tasks_per_group, args.seed)
    stream = grouped if args.order == "grouped" else shuffled_tasks(grouped, args.seed + 99)
    results = [
        run_policy(stream, "no_memory", args.seed + 1, args.top_k),
        run_policy(stream, "raw_memory", args.seed + 1, args.top_k),
        run_policy(stream, "skillos_heuristic", args.seed + 1, args.top_k),
    ]
    summarize(results)
    print(
        "\nObservation: grouped streams make later related tasks expose whether earlier "
        "insert/update/delete decisions created useful reusable skills."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SkillOS-style skill curation simulation")
    parser.add_argument("--groups", type=int, default=5)
    parser.add_argument("--tasks-per-group", type=int, default=8)
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--order", choices=["grouped", "shuffled"], default="grouped")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
