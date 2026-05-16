# Hebrew filler words for video-use Step 3 post-pass

ElevenLabs Scribe tags English fillers (`umm`, `uh`, `like`, `you know`, false starts) but NOT Hebrew ones. This is a working list of the most common spoken-Israeli-Hebrew fillers, based on common patterns in Israeli conversational speech , not an authoritative linguistic taxonomy. Apply as a post-pass on Scribe word timestamps before generating cut candidates, and extend the list as you encounter speaker-specific tics.

## How to use

Iterate Scribe's word array. For each word whose normalized form (lowercased, nikud stripped) is in the **always-filler** list, mark the timestamp range as a silence-equivalent cut candidate, subject to the same 30-200ms padding and word-boundary snap rules as upstream.

For words in the **context-dependent** list, do NOT auto-cut, present them to the editor sub-agent with a flag and let it decide based on surrounding context.

## Always-filler

These are pure verbal tics with no semantic load. Safe to cut whenever a better take exists.

| Form | Note |
|------|------|
| אֶה | Most common Hebrew filler, equivalent to English "uh" |
| אה | Bare alef-heh, often Scribe's transcription of the same sound |
| אם | Single em, equivalent to "umm" |
| אֶמ | Em with segol mark, same sound |
| אממ | Doubled mem, sustained "ummm" |
| אמממ | Tripled mem, even longer hesitation |
| אהמ | Combined ah-em |

## Context-dependent (flag, do not auto-cut)

These words function as fillers in casual speech but carry meaning in other contexts. Flag for editor judgment.

| Form | Filler use | Meaning-bearing use |
|------|------------|---------------------|
| כאילו | "like" filler, mid-sentence verbal tic | "as if", literal comparison |
| יעני | Equivalent to "I mean" hedge | Loanword from Arabic, sometimes intentional emphasis |
| בעצם | "actually" hedge filler | "in essence", genuine clarification |
| טוב | "ok" turn-marker | "good", literal positive |
| אוקיי | "ok" filler | Affirmative response |
| סבבה | "alright" casual filler | Affirmative slang |
| נו | "nu" prompt filler | "well?", genuine prompt for response |
| האמת | "the truth is" hedge | Genuine truth-claim setup |
| בסדר | "ok" turn-marker | "alright", literal agreement |
| אז | "so" sentence-starter filler | "then", temporal/causal connector |
| אז ככה | "so like this" turn-marker | Genuine introductory phrase |
| את יודע | "you know" (m.→f. speaker) filler | Genuine knowledge check |
| את יודעת | "you know" (f.→f. speaker) filler | Genuine knowledge check |
| אתה יודע | "you know" (m./f.→m. speaker) filler | Genuine knowledge check |

## Editorial guidance

- **Frequency budget**: Working heuristic , leaving a small number of context-dependent fillers per minute reads as natural Israeli speech; cutting all of them sounds robotic. Per upstream's "Unavoidable slips are kept if no better take exists" rule, prefer leaving them in over multiple cuts in tight succession. Calibrate to your speaker and audience.
- **Speaker personality**: some speakers use "כאילו" or "יעני" as a verbal signature. Cutting them all flattens their voice. Confirm with the user during the conversation phase whether to preserve voice or maximize content density.
- **Code-switched fillers**: "אז like" is a real construction in Israeli tech speech (Hebrew turn-marker + English filler). Treat the English "like" as a filler via Scribe's English tagging, and the "אז" as context-dependent via this list.

## False positives to avoid

Do NOT add these even though they sometimes get categorized as fillers in English-only research:

- **בעצם** at the start of a sentence is almost always meaning-bearing ("Actually, what I meant was..."). Only flag mid-sentence occurrences.
- **טוב** when it directly modifies a noun ("מאמר טוב") is the adjective "good", not a filler.
- **נו** at the end of a question ("מה דעתך, נו?") is a genuine prompt for response, not a filler.

## Pre-scan integration

Upstream Step 2 ("Pre-scan for problems") is the right place to flag any of these for the editor sub-agent. Output format:

```
- [012.34] אֶה (always-filler, recommend cut)
- [045.67] כאילו (context-dependent, editor decides)
- [089.12] אז (context-dependent, mid-sentence , likely filler)
```

The editor sub-agent then resolves the context-dependent items in its strategy decision, not at cut time.
