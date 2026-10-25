#!/usr/bin/env python3
"""Analyze chatbot conversation logs for key metrics.

Reads conversation logs in JSON format and produces an analytics report
covering core outcome rates (with the share of sessions whose outcome is
unknown), drop-off points, conversation loops, intent confidence,
response-time percentiles, Israeli traffic patterns, D1/D7/repeat-contact
retention, Hebrew/English code-switching, free-text opt-out requests, sessions
that contain a gap longer than the inactivity timeout, and, when outbound
messages carry the WhatsApp `pricing` object, billable message counts by
category, by pricing type and per business phone number per month.

This script deliberately does NOT compute sentiment. Sentiment requires the
DictaBERT path in Step 4 of SKILL.md (torch + transformers); keeping
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
patterns come back empty. Python 3.10 reached end of life on 2026-10-01.

Time zone: hour-of-day, weekday and calendar-day figures are reported in
Israel time (Asia/Jerusalem). Timestamps that carry an offset or a trailing
"Z" (BigQuery exports are UTC) are converted; timestamps with no offset are
assumed to be Israel local time already, and the report counts them. Without
the conversion a UTC export puts a Saturday 23:30 UTC session on Saturday
when it actually started on Sunday morning in Israel.

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
                    "sender": "user|bot|agent",
                    "text": "message text",
                    "intent": "optional-detected-intent",
                    "intent_confidence": 0.92,
                    "response_time_ms": 340,
                    "pricing": {"billable": true, "category": "service"}
                }
            ],
            "outcome": "resolved|escalated|abandoned|unknown",
            "satisfaction_score": 4.5
        }
    ]

    "sender" is "agent" for a human who took over; bot-only metrics (loops,
    response times) ignore agent messages, but billing counts them, because
    Meta bills a human's replies on the same number as service messages.
    "text" may be null or absent (media messages); "intent_confidence" may be
    null or absent (it is then excluded from low-confidence counts, not read as
    0). "pricing" is optional: copy it from the WhatsApp Cloud API status
    webhook for the outbound message if you want billable counts. Put the
    business phone number id in conversation["metadata"]["business_phone_number_id"]
    to get service-message counts per number per month (the free tier is 1,000
    per number per month).
"""

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")
    except ZoneInfoNotFoundError:
        # Windows without the tzdata package has no system tz database.
        ISRAEL_TZ = None
except ImportError:  # pragma: no cover
    ISRAEL_TZ = None

KNOWN_OUTCOMES = {"resolved", "escalated", "abandoned", "unknown"}
UNKNOWN_OUTCOME_WARN_SHARE = 0.20
SERVICE_FREE_TIER = 1000

# Opt-out screen. Under Section 30A(d)(1) of the Communications Law a recipient
# may refuse "in the way the advertisement was sent", so a WhatsApp reply of
# "הסר" or "stop" is a refusal, not a fallback. This is a SCREEN, not a
# classifier: it flags candidates for a confirmation step. A bare opt-out word
# counts only when it is (almost) the whole message, because "איך להסיר את
# הכרטיס" or "how do I stop my subscription" are support requests; longer
# messages count only on an explicit phrase about the sender or the list.
REFUSAL_WORDS = {"הסר", "הסירו", "הסירי", "הסרה", "להסיר", "תסירו", "תסיר", "תסירי", "stop", "unsubscribe", "סטופ"}
REFUSAL_PHRASES = [
    "הסר אותי", "הסירו אותי", "הסירי אותי", "תסירו אותי", "תסיר אותי", "תסירי אותי", "להסיר אותי",
    "תורידו אותי", "תוריד אותי", "תורידי אותי", "אותי מהרשימה", "מרשימת התפוצה", "די לשלוח", "תפסיקו לשלוח", "לא רוצה לקבל הודעות",
    "unsubscribe me", "stop sending", "remove me",
]

_naive_timestamps = 0


def msg_text(msg: dict) -> str:
    """Message text, or "" for media messages whose text is null or absent."""
    text = msg.get("text")
    return text if isinstance(text, str) else ""


def to_israel_time(value: str, count_naive: bool = False) -> datetime:
    """Parse an ISO-8601 timestamp and express it in Israel local time.

    Aware timestamps are converted to Asia/Jerusalem. Naive ones are assumed
    to be Israel local already. Pass count_naive=True from exactly one pass
    per session, so the report counts each naive session once.
    """
    global _naive_timestamps
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        if count_naive:
            _naive_timestamps += 1
        return dt
    if ISRAEL_TZ is None:
        return dt
    return dt.astimezone(ISRAEL_TZ)


def normalize_outcome(value) -> str:
    """Map a missing, null or unrecognised outcome to "unknown".

    Case and surrounding whitespace are ignored, so "Resolved" counts as
    resolved instead of silently lowering the resolution rate.
    """
    if not isinstance(value, str):
        return "unknown"
    value = value.strip().lower()
    return value if value in KNOWN_OUTCOMES else "unknown"


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
        "--session-timeout-minutes",
        type=int,
        default=30,
        help="Inactivity timeout used to flag sessions that contain a longer gap (default: 30)",
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

    outcomes = Counter(normalize_outcome(c.get("outcome")) for c in conversations)
    unrecognised = sum(
        1 for c in conversations
        if c.get("outcome") is not None and normalize_outcome(c.get("outcome")) == "unknown"
        and str(c.get("outcome")).strip().lower() != "unknown"
    )
    resolved = outcomes.get("resolved", 0)
    escalated = outcomes.get("escalated", 0)
    abandoned = outcomes.get("abandoned", 0)

    session_lengths = []
    session_durations = []
    duration_excluded = 0
    for c in conversations:
        msg_count = len(c.get("messages", []))
        session_lengths.append(msg_count)

        if c.get("started_at") and c.get("ended_at"):
            try:
                start = datetime.fromisoformat(c["started_at"])
                end = datetime.fromisoformat(c["ended_at"])
                session_durations.append((end - start).total_seconds())
            except (ValueError, TypeError) as exc:
                duration_excluded += 1
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
        "unknown_outcome_rate": round(outcomes.get("unknown", 0) / total, 4),
        "unrecognised_outcome_values": unrecognised,
        "avg_session_length": round(statistics.mean(session_lengths), 1) if session_lengths else 0,
        "median_session_length": statistics.median(session_lengths) if session_lengths else 0,
        "avg_session_duration_seconds": round(statistics.mean(session_durations), 1) if session_durations else 0,
        "median_session_duration_seconds": round(statistics.median(session_durations), 1) if session_durations else 0,
        "sessions_excluded_from_duration": duration_excluded,
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
        if normalize_outcome(convo.get("outcome")) != "abandoned":
            continue

        abandoned_count += 1
        messages = convo.get("messages", [])
        if not messages:
            continue

        drop_offs_by_depth[len(messages)] += 1

        for msg in reversed(messages):
            if msg.get("sender") == "bot":
                truncated = msg_text(msg)[:100] or "(media or no text)"
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
            msg_text(m)
            for m in convo.get("messages", [])
            if m.get("sender") == "bot"
        ]

        repeat_count = 1
        for i in range(1, len(bot_messages)):
            # Media and interactive messages with no text are not repeats of
            # each other: three catalog images in a row are not a loop.
            if bot_messages[i] and bot_messages[i] == bot_messages[i - 1]:
                repeat_count += 1
                if repeat_count >= threshold:
                    loops.append({
                        "session_id": convo.get("session_id", "unknown"),
                        "repeated_message": bot_messages[i][:100],
                        "repeat_count": repeat_count,
                        "total_messages": len(convo.get("messages", [])),
                        "outcome": normalize_outcome(convo.get("outcome")),
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
    missing_confidence = 0
    total_user_messages = 0

    for convo in conversations:
        for msg in convo.get("messages", []):
            if msg.get("sender") != "user":
                continue

            total_user_messages += 1
            intent = msg.get("intent", "")
            confidence = msg.get("intent_confidence")

            if intent:
                intent_counts[intent] += 1
                # A missing confidence is not a confidence of 0. Counting it
                # as one put every unscored message in the low-confidence list.
                if not isinstance(confidence, (int, float)):
                    missing_confidence += 1
                elif confidence < 0.6:
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
        "intents_without_confidence": missing_confidence,
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
                dt = to_israel_time(convo["started_at"], count_naive=True)
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
        # Divide by every calendar day in the span, not only the days that had
        # traffic, or empty Saturdays drop out and inflate the average.
        "avg_daily_volume": round(
            sum(daily_volumes.values()) / _span_days(daily_volumes), 2
        ) if daily_volumes else 0,
        "timezone": "Asia/Jerusalem" if ISRAEL_TZ else "as given (no tz database found)",
    }


def _span_days(daily_volumes: Counter) -> int:
    days = [datetime.strptime(d, "%Y-%m-%d").date() for d in daily_volumes]
    return (max(days) - min(days)).days + 1


def analyze_retention(conversations: list[dict]) -> dict:
    """D1, D7 and repeat-contact rates per stable user_id (Israel-local dates).

    D1: returned on the day after the first contact. D7: returned on any of
    days 2-7 after it. Repeat contact: more than one distinct day in total.
    Users first seen in the last 7 days of the log have not had a full D7
    window yet, so D7 is computed only over users whose first contact is at
    least 7 days before the last day in the log.
    """
    user_days: dict[str, set] = defaultdict(set)
    for convo in conversations:
        uid = convo.get("user_id")
        if not uid or not convo.get("started_at"):
            continue
        try:
            user_days[uid].add(to_israel_time(convo["started_at"]).date())
        except (ValueError, TypeError):
            continue

    if not user_days:
        return {"unique_users": 0}

    last_day = max(max(days) for days in user_days.values())
    d1_eligible = d1_returned = d7_eligible = d7_returned = repeat_users = 0
    for days in user_days.values():
        first = min(days)
        if len(days) > 1:
            repeat_users += 1
        if first + timedelta(days=1) <= last_day:
            d1_eligible += 1
            if first + timedelta(days=1) in days:
                d1_returned += 1
        if first + timedelta(days=7) <= last_day:
            d7_eligible += 1
            if any(first + timedelta(days=n) in days for n in range(2, 8)):
                d7_returned += 1

    return {
        "unique_users": len(user_days),
        "d1_return_rate": round(d1_returned / d1_eligible, 4) if d1_eligible else None,
        "d1_eligible_users": d1_eligible,
        "d7_return_rate": round(d7_returned / d7_eligible, 4) if d7_eligible else None,
        "d7_eligible_users": d7_eligible,
        "repeat_contact_rate": round(repeat_users / len(user_days), 4),
    }


def analyze_whatsapp_billing(conversations: list[dict]) -> dict:
    """Count delivered outbound messages by WhatsApp pricing category and type.

    Reads the optional `pricing` object (as carried on Cloud API status
    webhooks: billable, category, type). Bot AND human-agent messages count,
    since Meta bills both. When `billable` is absent or null, `type` decides: "regular"
    is billable, a type starting with "free" is free, anything else is unknown.
    Service messages are also counted per business phone number per month
    (Israel-local month; Meta resets the tier by the Messaging account's time
    zone, so a boundary day may differ). That count is an UPPER BOUND on what
    Meta meters against the 1,000-message tier (it includes free-entry-point
    and unknown-billability messages). Log one pricing object per message (the
    "delivered" status); a message carrying an "id" is counted once even if a
    second status row repeats it.
    """
    billable = Counter()
    free = Counter()
    unknown = Counter()
    by_type = Counter()
    service_per_number_month = Counter()
    seen_ids = set()
    for convo in conversations:
        number = (convo.get("metadata") or {}).get("business_phone_number_id")
        for msg in convo.get("messages", []):
            pricing = msg.get("pricing")
            if msg.get("sender") == "user" or not isinstance(pricing, dict):
                continue
            if msg.get("id"):
                if msg["id"] in seen_ids:
                    continue
                seen_ids.add(msg["id"])
            category = pricing.get("category") or "unknown"
            ptype = pricing.get("type") or "unknown"
            by_type[ptype] += 1
            if pricing.get("billable") is not None:
                is_billable = bool(pricing["billable"])
            elif ptype == "regular":
                is_billable = True
            elif ptype.startswith("free"):
                is_billable = False
            else:
                unknown[category] += 1
                is_billable = None
            if is_billable is True:
                billable[category] += 1
            elif is_billable is False:
                free[category] += 1
            stamp = msg.get("timestamp") or convo.get("started_at")
            if category == "service" and number and stamp:
                try:
                    month = to_israel_time(stamp).strftime("%Y-%m")
                    service_per_number_month[f"{number} {month}"] += 1
                except (ValueError, TypeError):
                    pass
    return {
        "messages_with_pricing": sum(by_type.values()),
        "billable_by_category": dict(billable.most_common()),
        "free_by_category": dict(free.most_common()),
        "unknown_billability_by_category": dict(unknown.most_common()),
        "by_pricing_type": dict(by_type.most_common()),
        "service_messages_per_number_month": dict(sorted(service_per_number_month.items())),
        "numbers_past_free_service_tier": sorted(
            k for k, v in service_per_number_month.items() if v > SERVICE_FREE_TIER
        ),
    }


def is_refusal_candidate(text: str) -> bool:
    """True when a user message looks like an opt-out (see REFUSAL_WORDS)."""
    import re
    lowered = text.lower()
    if any(phrase in lowered for phrase in REFUSAL_PHRASES):
        return True
    tokens = re.findall(r"[\u05D0-\u05EAa-zA-Z]+", lowered)
    # Strip a leading conjunction or relative prefix: "ולהסיר", "שתסירו".
    tokens = [t[1:] if len(t) > 3 and t[0] in "וש" and t[1:] in REFUSAL_WORDS else t for t in tokens]
    return 0 < len(tokens) <= 3 and any(t in REFUSAL_WORDS for t in tokens)


def analyze_refusals_and_gaps(conversations: list[dict], timeout_minutes: int) -> dict:
    """Likely free-text opt-out requests, and sessions with an inactivity gap.

    A gap longer than the inactivity timeout means the input was not cut into
    sessions with the rule in SKILL.md Step 1 (WhatsApp has no session object),
    so abandonment and handle time for those sessions are not comparable.
    """
    import re
    refusal_sessions = []
    refusal_messages = 0
    gap_sessions = []
    for convo in conversations:
        hit = False
        stamps = []
        for msg in convo.get("messages", []):
            if msg.get("sender") == "user" and is_refusal_candidate(msg_text(msg)):
                refusal_messages += 1
                hit = True
            if msg.get("timestamp"):
                try:
                    stamps.append(datetime.fromisoformat(msg["timestamp"]))
                except (ValueError, TypeError):
                    pass
        if hit:
            refusal_sessions.append(convo.get("session_id", "unknown"))
        try:
            stamps.sort()
            if any((b - a).total_seconds() > timeout_minutes * 60 for a, b in zip(stamps, stamps[1:])):
                gap_sessions.append(convo.get("session_id", "unknown"))
        except TypeError:
            pass  # naive and aware timestamps mixed in one session
    return {
        "refusal_candidates": refusal_messages,
        "sessions_with_refusal": refusal_sessions,
        "session_timeout_minutes": timeout_minutes,
        "sessions_with_gap_over_timeout": gap_sessions,
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

            text = msg_text(msg)
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

            # Primary language uses the SAME rule as the mixed Hebrew-English
            # section of Step 9 in SKILL.md: >= 0.5 Hebrew characters is a Hebrew
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
    for warning in report.get("warnings", []):
        lines.append(f"WARNING: {warning}")

    core = report["core_metrics"]
    lines.append(f"\nTotal conversations: {core['total_conversations']:,}")
    lines.append(f"Resolution rate:     {core['resolution_rate']:.1%}")
    lines.append(f"Escalation rate:     {core['escalation_rate']:.1%}")
    lines.append(f"Abandonment rate:    {core['abandonment_rate']:.1%}")
    lines.append(f"Unknown outcome:     {core['unknown_outcome_rate']:.1%}"
                 + (f" ({core['unrecognised_outcome_values']} unrecognised values)"
                    if core['unrecognised_outcome_values'] else ""))
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

    if report.get("naive_timestamps"):
        lines.append(f"Timestamps without offset (assumed Israel time): {report['naive_timestamps']:,}")

    ret = report["retention"]
    if ret.get("unique_users"):
        lines.append(f"\n--- Retention ---")
        lines.append(f"Unique users:        {ret['unique_users']:,}")
        for key, label in (("d1_return_rate", "D1 return rate:     "),
                           ("d7_return_rate", "D7 return rate:     ")):
            value = ret.get(key)
            lines.append(f"{label} {value:.1%}" if value is not None else f"{label} n/a (window not elapsed)")
        lines.append(f"Repeat contact:      {ret['repeat_contact_rate']:.1%}")

    billing = report["whatsapp_billing"]
    if billing["messages_with_pricing"]:
        lines.append(f"\n--- WhatsApp billing ---")
        for category, count in billing["billable_by_category"].items():
            lines.append(f"  billable {category}: {count:,}")
        for category, count in billing["free_by_category"].items():
            lines.append(f"  free {category}: {count:,}")
        for category, count in billing["unknown_billability_by_category"].items():
            lines.append(f"  unknown billability {category}: {count:,}")
        for key in billing["numbers_past_free_service_tier"]:
            lines.append(f"  may be past the 1,000 free service messages (upper bound): {key}")

    refusals = report["refusals_and_gaps"]
    if refusals["refusal_candidates"]:
        lines.append(f"\n--- Likely opt-out requests (confirm each; the screen may miss some) ---")
        lines.append(f"Candidates: {refusals['refusal_candidates']:,} in "
                     f"{len(refusals['sessions_with_refusal']):,} sessions")

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
    for warning in report.get("warnings", []):
        lines.append(f"> **Warning:** {warning}\n")

    core = report["core_metrics"]
    lines.append("## Core Metrics\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Conversations | {core['total_conversations']:,} |")
    lines.append(f"| Resolution Rate | {core['resolution_rate']:.1%} |")
    lines.append(f"| Escalation Rate | {core['escalation_rate']:.1%} |")
    lines.append(f"| Abandonment Rate | {core['abandonment_rate']:.1%} |")
    lines.append(f"| Unknown Outcome | {core['unknown_outcome_rate']:.1%} |")
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
        if report.get("naive_timestamps"):
            lines.append(f"| Timestamps without offset (assumed Israel time) | {report['naive_timestamps']} |")

    ret = report.get("retention") or {}
    if ret.get("unique_users"):
        lines.append("\n## Retention\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Unique users | {ret['unique_users']:,} |")
        for key, label in (("d1_return_rate", "D1 return rate"), ("d7_return_rate", "D7 return rate")):
            value = ret.get(key)
            lines.append(f"| {label} | {value:.1%} |" if value is not None else f"| {label} | n/a |")
        lines.append(f"| Repeat contact rate | {ret['repeat_contact_rate']:.1%} |")

    billing = report.get("whatsapp_billing") or {}
    if billing.get("messages_with_pricing"):
        lines.append("\n## WhatsApp Billing\n")
        lines.append("| Category | Billable | Free | Unknown |")
        lines.append("|----------|----------|------|---------|")
        cats = sorted(set(billing["billable_by_category"]) | set(billing["free_by_category"])
                      | set(billing["unknown_billability_by_category"]))
        for cat in cats:
            lines.append(f"| {cat} | {billing['billable_by_category'].get(cat, 0):,} | "
                         f"{billing['free_by_category'].get(cat, 0):,} | "
                         f"{billing['unknown_billability_by_category'].get(cat, 0):,} |")
        if billing["numbers_past_free_service_tier"]:
            lines.append("\nMay be past the 1,000 free service messages (upper bound): "
                         + ", ".join(billing["numbers_past_free_service_tier"]))

    refusals = report.get("refusals_and_gaps") or {}
    if refusals.get("refusal_candidates"):
        lines.append(f"\n## Likely Opt-out Requests\n")
        lines.append(f"{refusals['refusal_candidates']:,} candidate refusals in "
                     f"{len(refusals['sessions_with_refusal']):,} sessions. This is a keyword screen that may miss requests, so review all messages for opt-outs: "
                     "confirm each, and stop marketing sends to anyone who did refuse (Section 30A(d)(1)).")

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
        "retention": analyze_retention(conversations),
        "whatsapp_billing": analyze_whatsapp_billing(conversations),
        "refusals_and_gaps": analyze_refusals_and_gaps(conversations, args.session_timeout_minutes),
    }
    report["naive_timestamps"] = _naive_timestamps

    unknown_share = report["core_metrics"].get("unknown_outcome_rate", 0)
    report["warnings"] = []
    if unknown_share > UNKNOWN_OUTCOME_WARN_SHARE:
        report["warnings"].append(
            f"{unknown_share:.0%} of sessions have no usable outcome; derive outcome first (Step 1)."
        )
    gaps = report["refusals_and_gaps"]["sessions_with_gap_over_timeout"]
    if gaps:
        report["warnings"].append(
            f"{len(gaps)} sessions contain a gap longer than {args.session_timeout_minutes} minutes; "
            "re-cut them with the Step 1 inactivity rule before trusting abandonment or handle time."
        )
    if unknown_share > UNKNOWN_OUTCOME_WARN_SHARE:
        print(
            f"Warning: {unknown_share:.0%} of sessions have no usable outcome. "
            "Derive outcome first (SKILL.md Step 1); every rate in this report "
            "is computed against a base that bucket cannot fill.",
            file=sys.stderr,
        )
    if ISRAEL_TZ is None:
        print("Warning: no time zone database found (install tzdata); hour and "
              "weekday figures use the timestamps as given, not Israel time.",
              file=sys.stderr)

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
