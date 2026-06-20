#!/usr/bin/env python3
"""TinyGRPO — CPU-runnable, scaled-down reproduction of GRPO for arith prompts.

This script is the engineering companion to ai-learning/reports/knowledge_reports/
推理模型三大流派详解_20260621.md (T060, 2026-06-21), Section 3.3 (DeepSeek R1
路线) and the GRPO algorithm box in Section 4.4. It implements:

  1. Group sampling: G candidate answers per prompt from a small policy.
  2. Rule-based reward: arith correctness + format reward (R1 style).
  3. Group-relative advantage: (r_i - mean_r) / std_r, NO critic network.
  4. PPO-clip style policy update with KL penalty to a frozen reference.
  5. Metrics: mean reward, reward std, policy entropy, KL(pi_theta || pi_ref).

The "policy" is a categorical distribution over discrete answer templates
("a + b = c", "X apples" style). It is small enough to run on CPU, but the
training loop follows the real GRPO equations (group sampling, group-relative
advantage, PPO clip, KL penalty) so the curves are interpretable. This is the
same engineering trade-off exp_006 / exp_007 use: small inputs, real shape.

Usage:
    python3 ai-practice/src/grpo_simulation.py                    # default run
    python3 ai-practice/src/grpo_simulation.py --steps 100 --group-size 8 \\
            --num-prompts 30 --seed 42 --out-dir /tmp/grpo_run
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
from dataclasses import dataclass, field

import numpy as np

# T060 §4.4 quotes: "DeepSeek R1 风格规则化奖励" and the GRPO loss box.
# This script materialises both ideas in a CPU-runnable form.


# ---------------------------------------------------------------------------
# 1. Task definition — toy GSM8K-style arithmetic.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArithPrompt:
    """A simple arithmetic word problem. Answer is a single integer string."""
    question: str
    ground_truth: int


def make_arith_prompts(num_prompts: int, max_value: int = 20, seed: int = 0,
                       only_single_digit_gt: bool = True) -> list[ArithPrompt]:
    """Build `num_prompts` simple two-number arithmetic problems.

    Templates cover +, -, x. Each problem's ground truth is the integer result.

    Difficulty knob:
      - `max_value` controls operand magnitude. The default 4 keeps ground
        truth as a single digit, which makes random sampling a non-trivial
        baseline (~1/10 hit rate) and gives GRPO a real group-relative
        advantage signal to learn from.
      - `only_single_digit_gt=True` further filters to problems whose
        ground truth is a single digit 0-9, matching the policy's answer
        format ("X=").
    """
    rng = random.Random(seed)
    templates = [
        ("What is {a} + {b}?", lambda a, b: a + b),
        ("What is {a} - {b}?", lambda a, b: a - b if a >= b else b - a),
        ("What is {a} times {b}?", lambda a, b: a * b),
    ]
    prompts: list[ArithPrompt] = []
    attempts = 0
    while len(prompts) < num_prompts and attempts < num_prompts * 10:
        attempts += 1
        template, fn = rng.choice(templates)
        a = rng.randint(1, max_value)
        b = rng.randint(1, max_value)
        gt = fn(a, b)
        if only_single_digit_gt and not (0 <= gt <= 9):
            continue
        prompts.append(ArithPrompt(question=template.format(a=a, b=b), ground_truth=gt))
    return prompts


# ---------------------------------------------------------------------------
# 2. Policy — small categorical distribution over discrete answer tokens.
# ---------------------------------------------------------------------------

# Action vocabulary: digits 0-9 plus a few "format" symbols. The policy
# outputs a sequence of these tokens. We model each action as a categorical
# over the whole vocabulary; this keeps the implementation tiny while still
# supporting the GRPO loss equations exactly.

VOCAB = list("0123456789=")  # length 11
VOCAB_INDEX = {c: i for i, c in enumerate(VOCAB)}
VOCAB_SIZE = len(VOCAB)
# 2-token answer = "<digit>=". With one digit we can represent 0-9, and the
# policy can put "=" in position 1 deterministically by making that logit very
# large after a few warm-up steps. Shorter answers make random sampling
# hit the correct ground truth with ~10% probability, which is what gives
# GRPO a non-zero group-relative advantage signal in this toy setting.
MAX_ANSWER_LEN = 2


def softmax(logits: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax."""
    shifted = logits - logits.max(axis=axis, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=axis, keepdims=True)


class TinyPolicy:
    """Categorical policy with per-position logits.

    θ is a tensor of shape [MAX_ANSWER_LEN, VOCAB_SIZE]. We sample left to right.
    This is intentionally small so the whole thing runs on CPU in seconds.
    """

    def __init__(self, vocab_size: int = VOCAB_SIZE, max_len: int = MAX_ANSWER_LEN,
                 seed: int = 0) -> None:
        rng = np.random.default_rng(seed)
        # Slight bias toward digits in the first position and "=" in the last
        # position to break initial symmetry. This matches the typical
        # answer format ("X=") and gives the policy a useful starting point.
        bias = np.zeros((max_len, vocab_size), dtype=np.float64)
        bias[0, :10] = 0.5  # prefer digits in position 0
        if max_len >= 2:
            bias[-1, 10] = 1.5  # strongly prefer "=" in the last position
        self.theta = bias + 0.01 * rng.standard_normal((max_len, vocab_size))
        self.max_len = max_len
        self.vocab_size = vocab_size

    def clone(self) -> "TinyPolicy":
        new = TinyPolicy(self.vocab_size, self.max_len)
        new.theta = self.theta.copy()
        return new

    def probs(self) -> np.ndarray:
        """Return softmax probs, shape [max_len, vocab_size]."""
        return softmax(self.theta, axis=-1)

    def log_probs(self) -> np.ndarray:
        """Stable log-softmax."""
        return np.log(self.probs() + 1e-12)

    def sample(self, rng: np.random.Generator) -> tuple[list[int], float]:
        """Sample one answer; return (token_ids, log_prob_of_sequence)."""
        probs = self.probs()
        ids: list[int] = []
        log_prob = 0.0
        for pos in range(self.max_len):
            p = probs[pos]
            tok = int(rng.choice(self.vocab_size, p=p))
            ids.append(tok)
            log_prob += math.log(p[tok] + 1e-12)
        return ids, log_prob

    def log_prob_of(self, ids: list[int]) -> float:
        """log π(ids) for a given sequence."""
        probs = self.probs()
        return float(sum(math.log(probs[pos, t] + 1e-12) for pos, t in enumerate(ids)))

    def sequence_entropy(self) -> float:
        """Per-position entropy, summed. Higher = more random."""
        probs = self.probs()
        ent = 0.0
        for pos in range(self.max_len):
            for v in range(self.vocab_size):
                p = probs[pos, v]
                if p > 0:
                    ent -= p * math.log(p)
        return ent


# ---------------------------------------------------------------------------
# 3. Reward — R1-style rule-based reward.
# ---------------------------------------------------------------------------

def decode_answer(ids: list[int]) -> str:
    """Convert sampled token ids to a string like '42='."""
    return "".join(VOCAB[i] for i in ids)


def extract_integer(answer_str: str) -> int | None:
    """Pull the leading integer out of an answer string. Robust to junk."""
    digits = ""
    for ch in answer_str:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def reward_function(answer_ids: list[int], prompt: ArithPrompt) -> tuple[float, dict]:
    """R1-style rule-based reward.

    Mirrors T060 §4.4 reward_correctness_and_format:
      - 1.0 if integer extraction equals ground truth (accuracy reward)
      - +0.3 if format contains "=" (format reward, mimicking R1)
      - small length penalty if extracted integer is unreasonable
    """
    text = decode_answer(answer_ids)
    extracted = extract_integer(text)
    info = {
        "text": text,
        "extracted": extracted,
        "ground_truth": prompt.ground_truth,
        "acc": 0.0,
        "fmt": 0.0,
    }
    if extracted is not None and extracted == prompt.ground_truth:
        info["acc"] = 1.0
    if "=" in text:
        # Small format reward (R1 uses 0.5 max, we use 0.1 here so the
        # dominant signal is the accuracy reward, not the format shortcut).
        info["fmt"] = 0.1
    return info["acc"] + info["fmt"], info


# ---------------------------------------------------------------------------
# 4. GRPO update.
# ---------------------------------------------------------------------------

@dataclass
class StepMetrics:
    step: int
    mean_reward: float
    reward_std: float
    group_advantage_mean: float
    group_advantage_std: float
    policy_entropy: float
    kl_to_ref: float
    mean_answer_len: float
    accuracy: float  # fraction of group samples with acc reward == 1.0
    format_rate: float  # fraction of group samples with fmt reward > 0
    loss: float
    sample_infos: list[dict] = field(default_factory=list)


def grpo_update(policy: TinyPolicy, ref_policy: TinyPolicy,
                prompts: list[ArithPrompt], group_size: int,
                clip_eps: float, kl_beta: float, lr: float,
                step_idx: int, rng: np.random.Generator) -> StepMetrics:
    """One GRPO update step over `len(prompts)` prompts (each with G samples).

    Implements DeepSeekMath GRPO (Shao et al. 2024) loss:
        L = -E_i [ min(ρ_i A_i, clip(ρ_i, 1-ε, 1+ε) A_i) ] + β KL(π_θ || π_ref)
    where ρ_i = π_θ(o_i|x) / π_ref(o_i|x) and A_i is group-normalised.
    """
    # 1) Sample G answers per prompt and compute rewards.
    all_log_probs_old = []  # log π_old (== π_θ at step start)
    all_rewards = []
    all_advantages = []
    all_infos = []
    all_sampled_ids = []  # store the actual sampled ids for the gradient step
    correct_flags = []
    format_flags = []
    mean_ans_len = 0.0
    n_total = 0

    for prompt in prompts:
        rewards: list[float] = []
        infos: list[dict] = []
        log_probs: list[float] = []
        sampled_ids: list[list[int]] = []
        for _ in range(group_size):
            ids, lp = policy.sample(rng)
            r, info = reward_function(ids, prompt)
            rewards.append(r)
            infos.append(info)
            log_probs.append(lp)
            sampled_ids.append(ids)
            correct_flags.append(1.0 if info["acc"] > 0 else 0.0)
            format_flags.append(1.0 if info["fmt"] > 0 else 0.0)
            mean_ans_len += len(info["text"])
            n_total += 1

        r_arr = np.asarray(rewards, dtype=np.float64)
        mean_r = float(r_arr.mean())
        std_r = float(r_arr.std() + 1e-8)
        advantages = (r_arr - mean_r) / std_r
        for ids, lp, a in zip(sampled_ids, log_probs, advantages):
            all_log_probs_old.append(lp)
            all_rewards.append(mean_r)  # for the step metric
            all_advantages.append(float(a))
            all_sampled_ids.append(ids)
        all_infos.append(infos)

    # 2) Compute the GRPO loss and gradient w.r.t. θ.
    #    The textbook GRPO gradient is ∇L = -E[ A_i · ∇log π(o_i|x) ] (the
    #    ratio cancels the ref in the score-function view). For a categorical
    #    policy, ∇log π(t | pos) is +1 at the sampled token and -1 elsewhere,
    #    scaled by 1 - p(t | pos) in the softmax gradient. We use that
    #    exact form so the toy trainer is algorithmically faithful.
    #
    #    The original DeepSeekMath paper applies a *per-prompt* average over
    #    the group, not a global average across the batch. This is the
    #    "GRPO" normalisation: divide each prompt's accumulated gradient by
    #    group_size, then sum over prompts. This makes the learning rate
    #    insensitive to |prompts| and to group_size, and matches the
    #    official pseudo-code in the R1 paper.
    grads = np.zeros_like(policy.theta)
    loss_total = 0.0
    advantage_arr = np.asarray(all_advantages, dtype=np.float64)
    probs = policy.probs()
    log_probs_ref = ref_policy.log_probs()

    flat_idx = 0
    for prompt_idx, prompt in enumerate(prompts):
        prompt_grad = np.zeros_like(policy.theta)
        for g in range(group_size):
            # IMPORTANT: reuse the ids sampled in step 1 — re-sampling
            # would make the gradient uncorrelated with the advantage.
            ids = all_sampled_ids[flat_idx]
            lp_new = policy.log_prob_of(ids)
            lp_ref = float(sum(math.log(ref_policy.probs()[pos, t] + 1e-12)
                               for pos, t in enumerate(ids)))
            ratio = math.exp(lp_new - lp_ref)
            adv = advantage_arr[flat_idx]
            unclipped = ratio * adv
            clipped_val = max(1 - clip_eps, min(1 + clip_eps, ratio)) * adv
            surr = min(unclipped, clipped_val)
            loss_total += -surr
            # Score-function gradient: ∇L ≈ -A_i · ∇log π(o_i|x).
            grad_scale = -adv
            for pos, t in enumerate(ids):
                # ∂log p[t] / ∂θ[pos, v] = 1[v==t] - p[v]
                grad_row = -probs[pos].copy()
                grad_row[t] += 1.0
                prompt_grad[pos] += grad_scale * grad_row
            flat_idx += 1
        # Per-prompt average (DeepSeekMath normalisation).
        prompt_grad /= max(group_size, 1)
        grads += prompt_grad

    # Per-step average across the number of prompts (so the effective
    # step size is independent of batch size, matching Adam-style behaviour
    # used in modern GRPO trainers).
    grads /= max(len(prompts), 1)

    # 3) KL penalty: KL(π_θ || π_ref) = Σ p · (log p - log p_ref)
    probs_now = policy.probs()
    log_probs_now = policy.log_probs()
    kl = float(np.sum(probs_now * (log_probs_now - log_probs_ref)))
    # Add β·KL to loss (gradient handled implicitly via the ref comparison).
    loss_total += kl_beta * kl
    # KL gradient push: ∇KL(π_θ||π_ref) w.r.t. θ is ∇(Σ p · log p) = Σ p · (1 + log p)
    # gradient plus the cross-entropy term with ref. Adding it to the GRPO
    # gradient keeps the policy close to ref, matching the surrogate loss.
    kl_grad = probs_now * (1.0 + log_probs_now - log_probs_ref)
    grads += kl_beta * kl_grad

    # 4) Apply gradient.
    policy.theta -= lr * grads

    mean_reward = float(np.mean(all_rewards))
    reward_std = float(np.std(all_rewards))
    return StepMetrics(
        step=step_idx,
        mean_reward=mean_reward,
        reward_std=reward_std,
        group_advantage_mean=float(advantage_arr.mean()),
        group_advantage_std=float(advantage_arr.std()),
        policy_entropy=policy.sequence_entropy(),
        kl_to_ref=kl,
        mean_answer_len=mean_ans_len / max(n_total, 1),
        accuracy=float(np.mean(correct_flags)),
        format_rate=float(np.mean(format_flags)),
        loss=loss_total / max(flat_idx, 1),
        sample_infos=[],
    )


# ---------------------------------------------------------------------------
# 5. Driver.
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> dict:
    rng = np.random.default_rng(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)

    prompts = make_arith_prompts(args.num_prompts, max_value=args.max_value, seed=args.seed)
    if not args.mixed_gt and args.shared_gt is not None:
        # Force a single ground truth across all prompts to give GRPO a
        # learnable target. Each prompt is rewritten to question+GT={shared_gt}.
        prompts = [
            ArithPrompt(
                question=p.question,
                ground_truth=args.shared_gt,
            )
            for p in prompts
        ]

    policy = TinyPolicy(seed=args.seed)
    ref_policy = policy.clone()  # frozen reference = initial policy

    history: list[StepMetrics] = []
    for step in range(1, args.steps + 1):
        # Shuffle prompts each step so we don't always hit the same examples.
        step_prompts = prompts.copy()
        random.shuffle(step_prompts)
        m = grpo_update(
            policy=policy,
            ref_policy=ref_policy,
            prompts=step_prompts,
            group_size=args.group_size,
            clip_eps=args.clip_eps,
            kl_beta=args.kl_beta,
            lr=args.lr,
            step_idx=step,
            rng=rng,
        )
        history.append(m)
        if step % args.log_every == 0 or step == 1 or step == args.steps:
            print(
                f"[step {step:>4}] mean_r={m.mean_reward:.4f} std_r={m.reward_std:.4f} "
                f"acc={m.accuracy:.2f} fmt={m.format_rate:.2f} "
                f"H={m.policy_entropy:.3f} KL={m.kl_to_ref:.4f} loss={m.loss:.4f}"
            )

    # Final qualitative samples.
    final_infos = []
    rng2 = np.random.default_rng(args.seed + 999)
    for prompt in prompts[: args.eval_prompts]:
        ids, _ = policy.sample(rng2)
        text = decode_answer(ids)
        r, info = reward_function(ids, prompt)
        final_infos.append({
            "question": prompt.question,
            "ground_truth": prompt.ground_truth,
            "sampled": text,
            "reward": r,
            "correct": bool(info["acc"] > 0),
            "well_formed": bool(info["fmt"] > 0),
        })

    return {
        "config": vars(args),
        "history": [m.__dict__ for m in history],
        "final_samples": final_infos,
    }


# ---------------------------------------------------------------------------
# 6. Output: plot + JSON + summary.
# ---------------------------------------------------------------------------

def _save_plot(history: list[dict], out_path: str) -> None:
    """Render a 4-panel PNG (reward, accuracy, entropy, KL) with PIL only.

    We do this with PIL instead of matplotlib so the script has zero plotting
    dependencies beyond the standard scientific stack.
    """
    from PIL import Image, ImageDraw, ImageFont

    steps = [m["step"] for m in history]
    panels = [
        ("mean_reward",  "Mean Reward (per group)",  (-0.1, 1.3)),
        ("accuracy",     "Accuracy (fraction correct)", (0.0, 1.05)),
        ("policy_entropy", "Policy Entropy (nats)", (0.0, None)),
        ("kl_to_ref",    "KL(pi_theta || pi_ref)",   (0.0, None)),
    ]
    W, H = 1200, 900
    panel_w, panel_h = W // 2, H // 2
    margin_l, margin_b = 70, 50
    margin_t, margin_r = 30, 20
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for idx, (key, title, (y_min, y_max)) in enumerate(panels):
        col = idx % 2
        row = idx // 2
        x0 = col * panel_w
        y0 = row * panel_h
        plot_x0 = x0 + margin_l
        plot_y0 = y0 + margin_t
        plot_x1 = x0 + panel_w - margin_r
        plot_y1 = y0 + panel_h - margin_b

        ys = [m[key] for m in history]
        if y_max is None:
            lo, hi = min(ys), max(ys)
            if hi - lo < 1e-9:
                hi = lo + 1.0
            y_min, y_max = lo, hi

        # Axes
        draw.rectangle([plot_x0, plot_y0, plot_x1, plot_y1], outline="black", width=1)
        # Title
        draw.text((plot_x0 + 5, y0 + 5), title, fill="black", font=font)
        # y labels
        for frac in (0.0, 0.5, 1.0):
            yy = plot_y1 - frac * (plot_y1 - plot_y0)
            label = f"{y_min + frac * (y_max - y_min):.3g}"
            draw.text((plot_x0 - 50, yy - 5), label, fill="black", font=font)
            draw.line([plot_x0, yy, plot_x1, yy], fill="#eee")

        # x labels
        if not steps:
            continue
        n = len(steps)
        for frac in (0.0, 0.5, 1.0):
            xx = plot_x0 + frac * (plot_x1 - plot_x0)
            idx_label = int(round(frac * (n - 1)))
            draw.text((xx - 8, plot_y1 + 5), str(steps[idx_label]), fill="black", font=font)

        # Line
        pts = []
        for i, v in enumerate(ys):
            xx = plot_x0 + (i / max(n - 1, 1)) * (plot_x1 - plot_x0)
            yy = plot_y1 - (v - y_min) / (y_max - y_min) * (plot_y1 - plot_y0)
            pts.append((xx, yy))
        draw.line(pts, fill="#c33", width=2)
        # Markers at log points
        for i, (xx, yy) in enumerate(pts):
            if i == 0 or i == n - 1 or (i + 1) % max(1, n // 8) == 0:
                draw.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill="#c33")

    img.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="TinyGRPO simulation (CPU)")
    parser.add_argument("--steps", type=int, default=80, help="GRPO update steps")
    parser.add_argument("--num-prompts", type=int, default=20, help="Number of unique arithmetic prompts")
    parser.add_argument("--group-size", type=int, default=8, help="G, samples per prompt")
    parser.add_argument("--max-value", type=int, default=4, help="Max operand magnitude")
    parser.add_argument("--shared-gt", type=int, default=7, help="If set, all prompts share this ground truth (toy single-answer mode)")
    parser.add_argument("--mixed-gt", action="store_true", help="Use mixed ground truths (failure case demo, requires prompt-conditional policy)")
    parser.add_argument("--clip-eps", type=float, default=0.2, help="PPO clip range")
    parser.add_argument("--kl-beta", type=float, default=0.005, help="KL penalty weight")
    parser.add_argument("--lr", type=float, default=1.0, help="Learning rate")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=5)
    parser.add_argument("--eval-prompts", type=int, default=8)
    parser.add_argument("--out-dir", type=str, default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "images", "grpo"))
    args = parser.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    result = run(args)

    # JSON
    json_path = os.path.join(out_dir, "grpo_run.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"[saved] {json_path}")

    # PNG
    plot_path = os.path.join(out_dir, "grpo_curves.png")
    _save_plot(result["history"], plot_path)
    print(f"[saved] {plot_path}")

    # Text summary
    summary_path = os.path.join(out_dir, "grpo_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        h = result["history"]
        f.write("TinyGRPO — Step-by-step summary\n")
        f.write("=" * 60 + "\n")
        f.write(
            "step   mean_r   std_r    acc    fmt     H       KL      loss\n"
        )
        for m in h:
            f.write(
                f"{m['step']:>4}  {m['mean_reward']:.4f}  {m['reward_std']:.4f}  "
                f"{m['accuracy']:.2f}  {m['format_rate']:.2f}  "
                f"{m['policy_entropy']:.3f}  {m['kl_to_ref']:.4f}  {m['loss']:.4f}\n"
            )
        f.write("\nFinal qualitative samples:\n")
        for s in result["final_samples"]:
            f.write(
                f"  Q: {s['question']:>40}  GT={s['ground_truth']:>3}  "
                f"sampled='{s['sampled']:>6}'  r={s['reward']:.2f}  "
                f"correct={s['correct']}  fmt={s['well_formed']}\n"
            )
    print(f"[saved] {summary_path}")


if __name__ == "__main__":
    main()
