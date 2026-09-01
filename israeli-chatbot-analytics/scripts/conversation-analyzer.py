#!/usr/bin/env python3
"""Analyze chatbot conversation logs for key metrics.

Reads conversation logs in JSON format and produces an analytics report
covering core outcome rates, drop-off points, conversation loops, intent
confidence, response-time percentiles, Israeli traffic patterns and
Hebrew/English code-switching.

This script deliberately does NOT compute sentiment. Sentiment requires the
DictaBERT path in Step 4 of SKILL.md (torch + transformers, ~500MB); keeping
this script pure standard library is what lets it run anywhere with no
install. See references/hebrew-sentiment-guide.md to build that layer.

Usage:
    python3 conversation-analyzer.py --input conversations.json
    python3 conversation-analyzer.py --input conversations.json --output report.json
    python3 conversation-analyzer.py --input conversations.json --format markdown
    python3 conversation-analyzer.py --help

Requires Python 3.11 or newer: datetime.fromisoformat only parses the full
ISO-8601 range (including a trailing "Z") from 3.11 onward. On 3.10 the
timestamps in the schema below fail to parse, and durations and traffic
patterns come back empty.

Input Format:
    A JSON file containing a list of conversation objects. Each conversation
    should follow this schema:

    [
        {
            "session_id": "uuid-string",
            "user_id": "optional-user-id",
            "channel": "whatsapp|telegram|web|app",
            "language": "he",
            "started_at": "2026-03-10T10:00:00+02:00",
            "ended_at": "2026-03-10T10:05:00+02:00",
            "messages": [
                {
                    "timestamp": "2026-03-10T10:00:00+02:00",
                    "sender": "user|bot",
                    "text": "message text",
                    "intent": "optional-detected-intent",
                    "intent_confidence": 0.92,
                    "response_time_ms": 340
                }
            ],
            "outcome": "resolved|escalated|abandoned|unknown",
            "satisfaction_score": 4.5
        }
    ]
"""

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze chatbot conversation logs for key metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input conversations.json
  %(prog)s --input conversations.json --output report.json
  %(prog)s --input conversations.json --format markdown
  %(prog)s --input conversations.json --top-n 20

Input file should be a JSON array of conversation objects.
See the module docstring at the top of this file for the expected schema.
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to JSON file containing conversation logs",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write the report (default: stdout)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top items to show in rankings (default: 10)",
    )
    parser.add_argument(
        "--loop-threshold",
        type=int,
        default=3,
        help="Consecutive repeated bot messages to flag as a loop (default: 3)",
    )
    return parser.parse_args()


def load_conversations(path: str) -> list[dict]:
    """Load conversation logs from a JSON file."""
    file_path = Path(path)
    if not file_path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: Input JSON must be a list of conversation objects", file=sys.stderr)
        sys.exit(1)

    return data


def compute_core_metrics(conversations: list[dict]) -> dict:
    """Compute core conversation metrics."""
    total = len(conversations)
    if total == 0:
        return {"total_conversations": 0}

    outcomes = Counter(c.get("outcome", "unknown") for c in conversations)
    resolved = outcomes.get("resolved", 0)
    escalated = outcomes.get("escalated", 0)
    abandoned = outcomes.get("abandoned", 0)

    session_lengths = []
    session_durations = []
    for c in conversations:
        msg_count = len(c.get("messages", []))
        session_lengths.append(msg_count)

        if c.get("started_at") and c.get("ended_at"):
            try:
                start = datetime.fromisoformat(c["started_at"])
                end = datetime.fromisoformat(c["ended_at"])
                session_durations.append((end - start).total_seconds())
            except (ValueError, TypeError) as exc:
                print(
                    f"Warning: could not parse session timestamps "
                    f"({c.get('started_at')!r} .. {c.get('ended_at')!r}): {exc}",
                    file=sys.stderr,
                )

    csat_scores = [
        c["satisfaction_score"]
        for c in conversations
        if c.get("satisfaction_score") is not None
    ]

    return {
        "total_conversations": total,
        "outcomes": dict(outcomes.most_common()),
        "resolution_rate": round(resolved / total, 4) if total > 0 else 0,
        "escalation_rate": round(escalated / total, 4) if total > 0 else 0,
        "abandonment_rate": round(abandoned / total, 4) if total > 0 else 0,
        "avg_session_length": round(statistics.mean(session_lengths), 1) if session_lengths else 0,
        "median_session_length": statistics.median(session_lengths) if session_lengths else 0,
        "avg_session_duration_seconds": round(statistics.mean(session_durations), 1) if session_durations else 0,
        "median_session_duration_seconds": round(statistics.median(session_durations), 1) if session_durations else 0,
        "avg_csat": round(statistics.mean(csat_scores), 2) if csat_scores else None,
        "csat_responses": len(csat_scores),
    }


def analyze_drop_offs(conversations: list[dict], top_n: int = 10) -> dict:
    """Analyze where users drop off in conversations."""
    drop_offs_by_depth = Counter()
    drop_offs_by_intent = Counter()
    drop_offs_by_last_bot_msg = Counter()

    abandoned_count = 0

    for convo in conversations:
        if convo.get("outcome") != "abandoned":
            continue

        abandoned_count += 1
        messages = convo.get("messages", [])
        if not messages:
            continue

        drop_offs_by_depth[len(messages)] += 1

        for msg in reversed(messages):
            if msg.get("sender") == "bot":
                truncated = msg.get("text", "")[:100]
                drop_offs_by_last_bot_msg[truncated] += 1
                break

        # Keep "fallback" in this bucket. Fallback-then-abandon is the most
        # common real drop-off pattern, so excluding it empties the report for
        # exactly the sessions that most need attention.
        for msg in reversed(messages):
            if msg.get("intent"):
                drop_offs_by_intent[msg["intent"]] += 1
                break

    return {
        "total_abandoned": abandoned_count,
        "by_depth": dict(drop_offs_by_depth.most_common(top_n)),
        "by_intent": dict(drop_offs_by_intent.most_common(top_n)),
        "by_last_bot_message": dict(drop_offs_by_last_bot_msg.most_common(top_n)),
    }


def detect_loops(conversations: list[dict], threshold: int = 3) -> list[dict]:
    """Detect conversations with repeated bot responses."""
    loops = []

    for convo in conversations:
        bot_messages = [
            m.get("text", "")
            for m in convo.get("messages", [])
            if m.get("sender") == "bot"
        ]

        repeat_count = 1
        for i in range(1, len(bot_messages)):
            if bot_messages[i] == bot_messages[i - 1]:
                repeat_count += 1
                if repeat_count >= threshold:
                    loops.append({
                        "session_id": convo.get("session_id", "unknown"),
                        "repeated_message": bot_messages[i][:100],
                        "repeat_count": repeat_count,
                        "total_messages": len(convo.get("messages", [])),
                        "outcome": convo.get("outcome", "unknown"),
                    })
                    break
            else:
                repeat_count = 1

    return loops


def analyze_intent_accuracy(conversations: list[dict], top_n: int = 10) -> dict:
    """Analyze intent recognition patterns."""
    intent_counts = Counter()
    low_confidence_intents = defaultdict(list)
    fallback_count = 0
    total_user_messages = 0

    for convo in conversations:
        for msg in convo.get("messages", []):
            if msg.get("sender") != "user":
                continue

            total_user_messages += 1
            intent = msg.get("intent", "")
            confidence = msg.get("intent_confidence", 0)

            if intent:
                intent_counts[intent] += 1
                if confidence < 0.6:
                    low_confidence_intents[intent].append(confidence)
                if intent == "fallback":
                    fallback_count += 1

    low_conf_summary = {}
    for intent, confidences in low_confidence_intents.items():
        low_conf_summary[intent] = {
            "count": len(confidences),
            "avg_confidence": round(statistics.mean(confidences), 3),
        }

    return {
        "total_user_messages": total_user_messages,
        "intent_distribution": dict(intent_counts.most_common(top_n)),
        "fallback_count": fallback_count,
        "fallback_rate": round(fallback_count / total_user_messages, 4) if total_user_messages > 0 else 0,
        "low_confidence_intents": dict(sorted(
            low_conf_summary.items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )[:top_n]),
    }


def analyze_response_times(conversations: list[dict]) -> dict:
    """Analyze bot response time performance."""
    response_times = []

    for convo in conversations:
        for msg in convo.get("messages", []):
            if msg.get("sender") == "bot" and msg.get("response_time_ms") is not None:
                response_times.append(msg["response_time_ms"])

    if not response_times:
        return {"total_responses": 0}

    sorted_rt = sorted(response_times)

    def percentile(pct: float) -> float:
        """Nearest-rank percentile.

        `int(n * 0.95)` truncates, so on n=20 it returns index 19, the maximum,
        and reports it as p95. Israeli bots often have exactly this kind of
        small sample, which is where the error is largest and least visible.
        """
        rank = math.ceil(pct * len(sorted_rt))
        return sorted_rt[max(0, min(rank - 1, len(sorted_rt) - 1))]

    return {
        "total_responses": len(response_times),
        "avg_ms": round(statistics.mean(response_times), 1),
        "median_ms": round(statistics.median(response_times), 1),
        "p50_ms": percentile(0.50),
        "p95_ms": percentile(0.95),
        "p99_ms": percentile(0.99),
        "max_ms": sorted_rt[-1],
        "min_ms": sorted_rt[0],
    }


def analyze_traffic_patterns(conversations: list[dict]) -> dict:
    """Analyze traffic volume patterns."""
    hour_counts = Counter()
    day_counts = Counter()
    channel_counts = Counter()
    daily_volumes = Counter()

    for convo in conversations:
        channel_counts[convo.get("channel", "unknown")] += 1

        if convo.get("started_at"):
            try:
                dt = datetime.fromisoformat(convo["started_at"])
                hour_counts[dt.hour] += 1
                day_counts[dt.strftime("%A")] += 1
                daily_volumes[dt.strftime("%Y-%m-%d")] += 1
            except (ValueError, TypeError) as exc:
                print(
                    f"Warning: could not parse started_at "
                    f"({convo.get('started_at')!r}): {exc}",
                    file=sys.stderr,
                )

    return {
        "by_hour": dict(sorted(hour_counts.items())),
        "by_day_of_week": dict(day_counts.most_common()),
        "by_channel": dict(channel_counts.most_common()),
        "daily_volumes": dict(sorted(daily_volumes.items())),
        "peak_hour": hour_counts.most_common(1)[0][0] if hour_counts else None,
        "busiest_day": day_counts.most_common(1)[0][0] if day_counts else None,
        "avg_daily_volume": round(statistics.mean(daily_volumes.values()), 1) if daily_volumes else 0,
    }


def analyze_language(conversations: list[dict]) -> dict:
    """Analyze language distribution in messages."""
    import re

    hebrew_msg_count = 0
    english_msg_count = 0
    mixed_msg_count = 0
    unclassifiable_msg_count = 0
    classifiable_messages = 0
    total_user_messages = 0

    for convo in conversations:
        for msg in convo.get("messages", []):
            if msg.get("sender") != "user":
                continue

            text = msg.get("text", "")
            total_user_messages += 1

            hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            total_chars = hebrew_chars + english_chars

            # Messages with no Hebrew or Latin letters at all (emoji, digits,
            # an image caption) are not classifiable and must not inflate the
            # denominator, or every rate below is computed against a larger
            # base than the buckets can ever fill.
            if total_chars == 0:
                unclassifiable_msg_count += 1
                continue

            classifiable_messages += 1
            he_ratio = hebrew_chars / total_chars

            # Primary language uses the SAME rule as detect_message_language()
            # in Step 9 of SKILL.md: >= 0.5 Hebrew characters is a Hebrew
            # message. The mixed band is a SEPARATE, overlapping measure of
            # code-switching, not a third primary-language bucket, so a
            # message can be both Hebrew and mixed. Reporting them as three
            # mutually exclusive buckets is what made the script and the
            # skill disagree on the same log.
            if he_ratio >= 0.5:
                hebrew_msg_count += 1
            else:
                english_msg_count += 1

            if 0.2 < he_ratio < 0.8:
                mixed_msg_count += 1

    return {
        "total_user_messages": total_user_messages,
        "classifiable_messages": classifiable_messages,
        "unclassifiable_messages": unclassifiable_msg_count,
        "hebrew_messages": hebrew_msg_count,
        "english_messages": english_msg_count,
        "mixed_messages": mixed_msg_count,
        "mixed_rate": round(mixed_msg_count / classifiable_messages, 4) if classifiable_messages > 0 else 0,
    }


def format_summary(report: dict) -> str:
    """Format report as a human-readable summary."""
    lines = []
    lines.append("=" * 60)
    lines.append("CHATBOT ANALYTICS REPORT")
    lines.append("=" * 60)

    core = report["core_metrics"]
    lines.append(f"\nTotal conversations: {core['total_conversations']:,}")
    lines.append(f"Resolution rate:     {core['resolution_rate']:.1%}")
    lines.append(f"Escalation rate:     {core['escalation_rate']:.1%}")
    lines.append(f"Abandonment rate:    {core['abandonment_rate']:.1%}")
    lines.append(f"Avg session length:  {core['avg_session_length']:.1f} messages")
    lines.append(f"Avg session duration: {core['avg_session_duration_seconds']:.0f}s")
    if core.get("avg_csat"):
        lines.append(f"Average CSAT:        {core['avg_csat']:.1f}/5 ({core['csat_responses']} responses)")

    lines.append(f"\n--- Drop-off Analysis ---")
    drop = report["drop_off_analysis"]
    lines.append(f"Total abandoned: {drop['total_abandoned']}")
    if drop["by_intent"]:
        lines.append("Top drop-off intents:")
        for intent, count in list(drop["by_intent"].items())[:5]:
            lines.append(f"  {intent}: {count}")
    if drop["by_last_bot_message"]:
        lines.append("Top drop-off bot messages:")
        for msg, count in list(drop["by_last_bot_message"].items())[:5]:
            lines.append(f"  \"{msg[:60]}...\": {count}")

    loops = report["conversation_loops"]
    if loops:
        lines.append(f"\n--- Conversation Loops ---")
        lines.append(f"Total looping sessions: {len(loops)}")
        for loop in loops[:5]:
            lines.append(f"  Session {loop['session_id'][:12]}...: "
                        f"repeated {loop['repeat_count']}x, "
                        f"outcome={loop['outcome']}")

    intent = report["intent_analysis"]
    lines.append(f"\n--- Intent Analysis ---")
    lines.append(f"Total user messages: {intent['total_user_messages']:,}")
    lines.append(f"Fallback rate:       {intent['fallback_rate']:.1%}")
    if intent["intent_distribution"]:
        lines.append("Top intents:")
        for name, count in list(intent["intent_distribution"].items())[:5]:
            lines.append(f"  {name}: {count:,}")

    perf = report["response_times"]
    if perf.get("total_responses", 0) > 0:
        lines.append(f"\n--- Response Times ---")
        lines.append(f"Avg:  {perf['avg_ms']:.0f}ms")
        lines.append(f"P50:  {perf['p50_ms']:.0f}ms")
        lines.append(f"P95:  {perf['p95_ms']:.0f}ms")
        lines.append(f"P99:  {perf['p99_ms']:.0f}ms")

    traffic = report["traffic_patterns"]
    lines.append(f"\n--- Traffic ---")
    if traffic.get("peak_hour") is not None:
        lines.append(f"Peak hour:       {traffic['peak_hour']}:00")
    if traffic.get("busiest_day"):
        lines.append(f"Busiest day:     {traffic['busiest_day']}")
    lines.append(f"Avg daily volume: {traffic['avg_daily_volume']:.0f}")
    if traffic["by_channel"]:
        lines.append("Channel distribution:")
        for channel, count in traffic["by_channel"].items():
            lines.append(f"  {channel}: {count:,}")

    lang = report["language_analysis"]
    if lang["total_user_messages"] > 0:
        lines.append(f"\n--- Language ---")
        lines.append(f"Hebrew messages:  {lang['hebrew_messages']:,}")
        lines.append(f"English messages: {lang['english_messages']:,}")
        lines.append(f"Mixed messages:   {lang['mixed_messages']:,} ({lang['mixed_rate']:.1%})")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_markdown(report: dict) -> str:
    """Format report as Markdown."""
    lines = []
    lines.append("# Chatbot Analytics Report\n")

    core = report["core_metrics"]
    lines.append("## Core Metrics\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Conversations | {core['total_conversations']:,} |")
    lines.append(f"| Resolution Rate | {core['resolution_rate']:.1%} |")
    lines.append(f"| Escalation Rate | {core['escalation_rate']:.1%} |")
    lines.append(f"| Abandonment Rate | {core['abandonment_rate']:.1%} |")
    lines.append(f"| Avg Session Length | {core['avg_session_length']:.1f} messages |")
    lines.append(f"| Avg Session Duration | {core['avg_session_duration_seconds']:.0f}s |")
    if core.get("avg_csat"):
        lines.append(f"| Average CSAT | {core['avg_csat']:.1f}/5 ({core['csat_responses']} responses) |")

    drop = report["drop_off_analysis"]
    lines.append(f"\n## Drop-off Analysis\n")
    lines.append(f"Total abandoned sessions: {drop['total_abandoned']}\n")
    if drop["by_intent"]:
        lines.append("### By Intent\n")
        lines.append("| Intent | Count |")
        lines.append("|--------|-------|")
        for intent, count in drop["by_intent"].items():
            lines.append(f"| {intent} | {count} |")

    loops = report["conversation_loops"]
    if loops:
        lines.append(f"\n## Conversation Loops\n")
        lines.append(f"Found {len(loops)} looping sessions.\n")
        lines.append("| Session | Repeats | Messages | Outcome |")
        lines.append("|---------|---------|----------|---------|")
        for loop in loops[:10]:
            lines.append(
                f"| {loop['session_id'][:16]}... | "
                f"{loop['repeat_count']} | "
                f"{loop['total_messages']} | "
                f"{loop['outcome']} |"
            )

    intent = report["intent_analysis"]
    lines.append(f"\n## Intent Analysis\n")
    lines.append(f"- Total user messages: {intent['total_user_messages']:,}")
    lines.append(f"- Fallback rate: {intent['fallback_rate']:.1%}\n")
    if intent["intent_distribution"]:
        lines.append("| Intent | Count |")
        lines.append("|--------|-------|")
        for name, count in intent["intent_distribution"].items():
            lines.append(f"| {name} | {count:,} |")

    perf = report["response_times"]
    if perf.get("total_responses", 0) > 0:
        lines.append(f"\n## Response Times\n")
        lines.append("| Percentile | Latency |")
        lines.append("|------------|---------|")
        lines.append(f"| Average | {perf['avg_ms']:.0f}ms |")
        lines.append(f"| P50 | {perf['p50_ms']:.0f}ms |")
        lines.append(f"| P95 | {perf['p95_ms']:.0f}ms |")
        lines.append(f"| P99 | {perf['p99_ms']:.0f}ms |")

    traffic = report.get("traffic_patterns") or {}
    if traffic:
        lines.append("\n## Traffic Patterns\n")
        lines.append("| Dimension | Value |")
        lines.append("|-----------|-------|")
        if traffic.get("peak_hour") is not None:
            lines.append(f"| Peak hour (Israel Time) | {traffic['peak_hour']}:00 |")
        if traffic.get("busiest_day"):
            lines.append(f"| Busiest day | {traffic['busiest_day']} |")
        for label, value in (traffic.get("by_channel") or {}).items():
            lines.append(f"| Channel: {label} | {value} |")

    lang = report.get("language_analysis") or {}
    if lang.get("classifiable_messages"):
        lines.append("\n## Language Distribution\n")
        lines.append("| Bucket | Messages |")
        lines.append("|--------|----------|")
        lines.append(f"| Hebrew (primary) | {lang['hebrew_messages']:,} |")
        lines.append(f"| English (primary) | {lang['english_messages']:,} |")
        lines.append(f"| Code-switching (20-80% Hebrew) | {lang['mixed_messages']:,} |")
        lines.append(f"| Unclassifiable (no letters) | {lang['unclassifiable_messages']:,} |")
        lines.append(f"\nCode-switching rate: {lang['mixed_rate']:.1%} of classifiable messages.")

    return "\n".join(lines)


def main():
    args = parse_args()

    conversations = load_conversations(args.input)

    if not conversations:
        print("No conversations found in input file.", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {len(conversations)} conversations...", file=sys.stderr)

    report = {
        "core_metrics": compute_core_metrics(conversations),
        "drop_off_analysis": analyze_drop_offs(conversations, args.top_n),
        "conversation_loops": detect_loops(conversations, args.loop_threshold),
        "intent_analysis": analyze_intent_accuracy(conversations, args.top_n),
        "response_times": analyze_response_times(conversations),
        "traffic_patterns": analyze_traffic_patterns(conversations),
        "language_analysis": analyze_language(conversations),
    }

    if args.format == "json":
        output = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    elif args.format == "markdown":
        output = format_markdown(report)
    else:
        output = format_summary(report)

    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {output_path}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
