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
        audio_path: Path to the audio file (WAV, MP3, FLAC, etc.)
        verbose: If True, return detailed results with timestamps

    Returns:
        Dictionary with transcript and optional metadata
    """
    import openai

    client = openai.OpenAI()

    file_size = os.path.getsize(audio_path)
    if file_size > 25 * 1024 * 1024:
        print(f"Warning: File size ({file_size / 1024 / 1024:.1f}MB) exceeds Whisper's 25MB limit.")
        print("Consider splitting the audio into smaller segments.")
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
            "segments": [
                {
                    "text": seg.get("text", ""),
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
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


def calculate_accuracy(expected: str, actual: str) -> dict:
    """
    Calculate word-level accuracy between expected and actual transcripts.

    Uses simple word overlap metric (not WER, which requires alignment).
    """
    expected_words = set(expected.strip().split())
    actual_words = set(actual.strip().split())

    correct = expected_words & actual_words
    missing = expected_words - actual_words
    extra = actual_words - expected_words

    precision = len(correct) / len(actual_words) if actual_words else 0
    recall = len(correct) / len(expected_words) if expected_words else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "expected_words": len(expected_words),
        "actual_words": len(actual_words),
        "correct_words": len(correct),
        "missing_words": list(missing),
        "extra_words": list(extra),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
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
        help="Path to Hebrew audio file (WAV, MP3, FLAC, M4A, OGG, WEBM)",
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
        print(f"  Precision: {accuracy['precision']:.1%}")
        print(f"  Recall:    {accuracy['recall']:.1%}")
        print(f"  F1 Score:  {accuracy['f1_score']:.1%}")
        if accuracy["missing_words"]:
            print(f"  Missing:   {', '.join(accuracy['missing_words'])}")
        if accuracy["extra_words"]:
            print(f"  Extra:     {', '.join(accuracy['extra_words'])}")
        result["accuracy"] = accuracy

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {args.output_json}")

    print()


if __name__ == "__main__":
    main()
