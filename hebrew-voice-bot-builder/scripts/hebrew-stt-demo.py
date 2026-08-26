#!/usr/bin/env python3
"""
Hebrew Speech-to-Text Demo

Demonstrates Hebrew STT using OpenAI Whisper. Can transcribe existing
Hebrew audio files or generate a test audio file using TTS and then
transcribe it back to verify the pipeline.

Usage:
    # Transcribe an existing Hebrew audio file
    python hebrew-stt-demo.py --input recording.wav

    # Transcribe with verbose output (timestamps + confidence)
    python hebrew-stt-demo.py --input recording.wav --verbose

    # Generate a test audio file with Hebrew TTS, then transcribe it
    python hebrew-stt-demo.py --generate-test

    # Compare STT accuracy against known text
    python hebrew-stt-demo.py --input recording.wav --expected "שלום עולם"

Requirements:
    pip install openai

Optional (for TTS test generation):
    pip install google-cloud-texttospeech
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path


def check_openai_key():
    """Verify OpenAI API key is set."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='your-key-here'", file=sys.stderr)
        sys.exit(1)


def transcribe_hebrew(audio_path: str, verbose: bool = False) -> dict:
    """
    Transcribe a Hebrew audio file using OpenAI Whisper.

    Args:
        audio_path: Path to the audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
        verbose: If True, return detailed results with timestamps

    Returns:
        Dictionary with transcript and optional metadata
    """
    import openai

    client = openai.OpenAI()

    file_size = os.path.getsize(audio_path)
    if file_size > 25 * 1024 * 1024:
        print(f"Error: file size ({file_size / 1024 / 1024:.1f}MB) exceeds the 25MB API limit.",
              file=sys.stderr)
        print("Split the audio into smaller segments and transcribe each.", file=sys.stderr)
        sys.exit(1)

    print(f"Transcribing: {audio_path}")
    print(f"File size: {file_size / 1024:.1f} KB")
    print()

    start_time = time.time()

    with open(audio_path, "rb") as audio_file:
        if verbose:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="he",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
        else:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="he",
                response_format="text",
            )

    elapsed = time.time() - start_time

    if verbose:
        return {
            "transcript": result.text,
            "language": getattr(result, "language", "he"),
            "duration": getattr(result, "duration", None),
            # result.segments holds TranscriptionSegment pydantic models, NOT
            # dicts. seg.get(...) raises AttributeError and seg["text"] raises
            # TypeError on every current openai SDK, so read the attributes.
            "segments": [
                {
                    "text": seg.text,
                    "start": seg.start,
                    "end": seg.end,
                }
                for seg in (getattr(result, "segments", None) or [])
            ],
            "processing_time_seconds": round(elapsed, 2),
        }
    else:
        return {
            "transcript": result,
            "processing_time_seconds": round(elapsed, 2),
        }


def generate_test_audio(output_path: str) -> str:
    """
    Generate a Hebrew test audio file using Google Cloud TTS.

    Returns the test text for accuracy comparison.
    """
    try:
        from google.cloud import texttospeech
    except ImportError:
        print("Error: google-cloud-texttospeech not installed.", file=sys.stderr)
        print("Install with: pip install google-cloud-texttospeech", file=sys.stderr)
        sys.exit(1)

    test_text = "שלום, ברוכים הבאים לשירות הלקוחות. לתמיכה טכנית, הקישו אחת. למכירות, הקישו שתיים."

    print(f"Generating test audio with text:")
    print(f'  "{test_text}"')
    print()

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=test_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="he-IL",
        name="he-IL-Wavenet-A",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.95,
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    print(f"Test audio saved to: {output_path}")
    print(f"Audio size: {os.path.getsize(output_path) / 1024:.1f} KB")
    print()

    return test_text


# Spoken Hebrew cardinals used on a keypad. Whisper renders spoken "אחת" as the
# digit "1", while a TTS reference script writes it out, so without this map a
# word-perfect transcription scores a large fabricated WER.
_HEBREW_NUMERALS = {
    "אפס": "0", "אחת": "1", "אחד": "1", "שתיים": "2", "שניים": "2",
    "שלוש": "3", "שלושה": "3", "ארבע": "4", "ארבעה": "4", "חמש": "5",
    "חמישה": "5", "שש": "6", "שישה": "6", "שבע": "7", "שבעה": "7",
    "שמונה": "8", "תשע": "9", "תשעה": "9", "עשר": "10", "עשרה": "10",
}

# Punctuation to drop before aligning. Includes the Hebrew geresh and gershayim,
# which Whisper emits inside acronyms and abbreviations.
_WER_PUNCT = ".,!?;:\"'()[]{}\u05f3\u05f4\u2019\u201c\u201d-"


def _normalize_for_wer(text: str) -> list:
    """Lowercase, strip punctuation, and map Hebrew number words to digits.

    A WER computed on raw tokens penalises differences that are not recognition
    errors at all: a trailing comma, or "אחת" against "1". Normalising first is
    what standard WER tooling does. Without it this check reports a word-perfect
    transcription as substantially wrong, which is just as useless as the
    set-overlap score it replaced reporting a scrambled one as perfect.
    """
    words = []
    for w in text.strip().split():
        w = w.strip(_WER_PUNCT).lower()
        if not w:
            continue
        words.append(_HEBREW_NUMERALS.get(w, w))
    return words


def calculate_accuracy(expected: str, actual: str) -> dict:
    """
    Calculate Word Error Rate between expected and actual transcripts.

    This is a real WER over the word SEQUENCE (Levenshtein alignment), not a
    set-overlap score. The distinction is not academic. A set-based metric
    ignores order and collapses duplicates, so for an IVR prompt it reports a
    perfect score for a transcript that is reversed, that dropped a repeated
    word, or that swapped the menu options ("press 1 for sales" instead of
    "press 1 for support"). Those are exactly the errors this check exists to
    catch, and a Hebrew IVR that mis-routes a caller is the failure that
    matters most.

    Returns substitution / deletion / insertion counts alongside WER so a
    failure says WHAT went wrong, not just that something did.
    """
    ref = _normalize_for_wer(expected)
    hyp = _normalize_for_wer(actual)

    # Levenshtein over words, tracking the edit type at each cell.
    rows, cols = len(ref) + 1, len(hyp) + 1
    dist = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dist[i][0] = i
    for j in range(cols):
        dist[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            if ref[i - 1] == hyp[j - 1]:
                dist[i][j] = dist[i - 1][j - 1]
            else:
                dist[i][j] = 1 + min(
                    dist[i - 1][j - 1],  # substitution
                    dist[i - 1][j],      # deletion
                    dist[i][j - 1],      # insertion
                )

    # Walk the matrix back to count each error type.
    subs = dels = ins = 0
    i, j = len(ref), len(hyp)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref[i - 1] == hyp[j - 1] and dist[i][j] == dist[i - 1][j - 1]:
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and dist[i][j] == dist[i - 1][j - 1] + 1:
            subs += 1
            i, j = i - 1, j - 1
        elif i > 0 and dist[i][j] == dist[i - 1][j] + 1:
            dels += 1
            i -= 1
        else:
            ins += 1
            j -= 1

    errors = subs + dels + ins
    wer = errors / len(ref) if ref else (1.0 if hyp else 0.0)
    accuracy = max(0.0, 1.0 - wer)

    return {
        "reference_words": len(ref),
        "hypothesis_words": len(hyp),
        "substitutions": subs,
        "deletions": dels,
        "insertions": ins,
        "errors": errors,
        "wer": round(wer, 3),
        "accuracy": round(accuracy, 3),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Hebrew Speech-to-Text Demo using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Transcribe a Hebrew audio file:
    %(prog)s --input recording.wav

  Transcribe with timestamps and segment details:
    %(prog)s --input recording.wav --verbose

  Generate test audio (requires Google Cloud TTS) and transcribe:
    %(prog)s --generate-test

  Compare transcription against expected text:
    %(prog)s --input recording.wav --expected "שלום עולם"

Environment:
  OPENAI_API_KEY        Required. Your OpenAI API key.
  GOOGLE_APPLICATION_CREDENTIALS  Optional. For --generate-test TTS feature.
        """,
    )

    parser.add_argument(
        "--input",
        type=str,
        help="Path to Hebrew audio file. OpenAI accepts mp3, mp4, mpeg, mpga, m4a, wav and webm; FLAC and OGG are NOT accepted and are rejected after upload",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output with timestamps and segments",
    )
    parser.add_argument(
        "--generate-test",
        action="store_true",
        help="Generate a Hebrew test audio file using Google TTS, then transcribe it",
    )
    parser.add_argument(
        "--expected",
        type=str,
        help="Expected transcript text for accuracy comparison",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        help="Save results to JSON file",
    )

    args = parser.parse_args()

    if not args.input and not args.generate_test:
        parser.error("Either --input or --generate-test is required")

    check_openai_key()

    print("=" * 60)
    print("  Hebrew Speech-to-Text Demo")
    print("  Provider: OpenAI Whisper")
    print("=" * 60)
    print()

    expected_text = args.expected

    if args.generate_test:
        if args.expected:
            print("Note: --expected is ignored with --generate-test; comparing "
                  "against the generated reference text instead.", file=sys.stderr)
        test_audio_path = "hebrew_test_audio.mp3"
        expected_text = generate_test_audio(test_audio_path)
        audio_path = test_audio_path
    else:
        audio_path = args.input

    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    result = transcribe_hebrew(audio_path, verbose=args.verbose)

    print("Transcription Result:")
    print("-" * 60)
    print(f"  {result['transcript']}")
    print("-" * 60)
    print(f"  Processing time: {result['processing_time_seconds']}s")

    if args.verbose and "segments" in result:
        print()
        print("Segments:")
        for i, seg in enumerate(result["segments"], 1):
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")

    if expected_text:
        print()
        print("Accuracy Analysis:")
        print("-" * 60)
        accuracy = calculate_accuracy(expected_text, result["transcript"])
        print(f"  Expected:  {expected_text}")
        print(f"  Got:       {result['transcript']}")
        print(f"  WER:       {accuracy['wer']:.1%} "
              f"({accuracy['errors']} errors over {accuracy['reference_words']} words)")
        print(f"  Accuracy:  {accuracy['accuracy']:.1%}")
        print(f"  Breakdown: {accuracy['substitutions']} substitutions, "
              f"{accuracy['deletions']} deletions, {accuracy['insertions']} insertions")
        result["accuracy"] = accuracy

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {args.output_json}")

    print()


if __name__ == "__main__":
    main()
