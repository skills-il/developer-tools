# Hebrew filler words for video-use Step 3 post-pass

ElevenLabs Scribe does NOT tag fillers per word in any language, `no_verbatim=true` is destructive (drops them), and `tag_audio_events` only marks `(laughter)`/`(applause)` style events. So filler detection in Hebrew (and English) needs a client-side lexicon match over the `words[].text` stream from Scribe with `no_verbatim=false`.

This is a working list of the most common spoken-Israeli-Hebrew fillers, compiled from a mix of native-speaker conventions and the discourse-marker literature on Modern Hebrew. It is not an authoritative academic taxonomy. Apply as a post-pass on Scribe word timestamps before generating cut candidates, and extend the list as you encounter speaker-specific tics.

## How to use

Iterate Scribe's `words[]` array. For each word whose normalized form (lowercased, nikud stripped, surrounding punctuation removed) is in the **ALWAYS-FILLER** list, mark the timestamp range as a silence-equivalent cut candidate, subject to the same 30-200ms padding and word-boundary snap rules as upstream.

For words in the **CONTEXT-DEPENDENT** list, do NOT auto-cut. Surface them to the editor sub-agent with a flag and let it decide based on surrounding context.

## ALWAYS-FILLER

Pure verbal tics with no semantic content. Safe to cut whenever a better take exists.

| Form | Note |
|------|------|
| אֶה | The most common Hebrew filler, equivalent to English "uh" |
| אה | Bare alef-heh, often Scribe's transcription of the same sound |
| אם | Single em, equivalent to "umm" |
| אֶמ | Em with segol mark, same sound |
| אממ | Doubled mem, sustained "ummm" |
| אמממ | Tripled mem, even longer hesitation |
| אהמ | Combined ah-em |
| המ | Closed-mouth humming hesitation |
| ממ | Closed-mouth humming variant (distinct from the affirmative "הממ" used as "mm-hm") |

## CONTEXT-DEPENDENT (flag, do not auto-cut)

These words function as fillers in casual speech but carry meaning in other contexts. Flag for editor judgment.

| Form | Filler use | Meaning-bearing use |
|------|------------|---------------------|
| כאילו | "like" filler, mid-sentence verbal tic ("זה כאילו לא עבד") | "as if", literal comparison ("התנהגה כאילו לא קרה כלום") |
| יעני | Equivalent to "I mean" hedge (Arabic loanword) | Sometimes intentional emphasis |
| בעצם | "actually" mid-sentence hedge | "in essence", genuine clarification at sentence start |
| טוב | "ok" turn-marker | "good", literal positive |
| טוב נו | Compound discourse marker: "tov" (acceptance/shift) + "nu" (impatience/move-on); used to restart or change topic | Rarely literal |
| אוקיי | "ok" filler | Affirmative response |
| סבבה | "alright" casual filler | Affirmative slang |
| נו | "nu" prompt filler / impatience cue | "well?", genuine prompt for response |
| האמת | "the truth is" hedge | Genuine truth-claim setup |
| בסדר | "ok" turn-marker | "alright", literal agreement |
| וואלה | Contentless turn-starter / mild affirmation (Arabic loanword) | Genuine "really?" / "wow!", distinguish by prosody |
| אז | "so" sentence-starter filler | "then", temporal/causal connector |
| אז ככה | "so like this" turn-marker | Genuine introductory phrase |
| כזה | "like" hedge ("הוא בא, ככה, כזה, מתוח") | Real demonstrative "like this one" |
| ככה | Hedge/filler in spoken Hebrew | Literal "in this manner" |
| נכון | Tag-question filler at sentence-end ("...הפאנל, נכון?") | Literal "correct" |
| פשוט | "simply" as hedge/intensifier filler ("זה פשוט... זה מדהים") | Real adverb when contrastively marking simplicity |
| ממש | "really/literally" intensifier that empties out semantically when overused ("זה ממש ממש טוב") | Literal "really" or "exactly" |
| סוג של | "kind of" hedge softening commitment to the next claim (calque on English "sort of") | Real meaning when classifying a subtype |
| בקיצור | Discourse marker to wrap up or restart, rarely literally shortening | Literal "in short" |
| כנראה | Hesitation hedge while thinking | Genuine epistemic "apparently/seemingly" |
| לדעתי | Stalling hedge rather than asserting a view | Genuine "in my opinion" |
| את יודע | "you know" (m→f filler) | Genuine knowledge check |
| את יודעת | "you know" (f→f filler) | Genuine knowledge check |
| אתה יודע | "you know" (→m filler) | Genuine knowledge check |
| אתה מבין | "you understand?" listener-engagement marker, parallel to "you know" | Real interrogative when actually asking |
| את מבינה | "you understand?" (→f) listener-engagement marker | Real interrogative when actually asking |
| הבנת | "got it?" sentence-final filler | Genuine comprehension check |
| תראה | "look" turn-starter / attention-grabber ("תראה, אני חושב ש...") | Literal "look at this" |
| תראי | "look" (→f) turn-starter | Literal "look" |
| שמע | "listen" turn-starter, routinely opens turns with no literal listening request | Real imperative |
| שמעי | "listen" (→f) turn-starter | Real imperative |
| בוא | "come" softener / turn-starter for proposals ("בוא נגיד ש...") | Real "come here" |
| בואי | "come" (→f) softener / turn-starter | Real "come here" |

## Editorial guidance

- **Frequency budget**: working heuristic, leaving a small number of context-dependent fillers per minute reads as natural Israeli speech; cutting all of them sounds robotic. Per upstream's "Unavoidable slips are kept if no better take exists" rule, prefer leaving them in over multiple cuts in tight succession. Calibrate to your speaker and audience.
- **Speaker personality**: some speakers use "כאילו", "יעני", or "וואלה" as a verbal signature. Cutting them all flattens their voice. Confirm with the user during the conversation phase whether to preserve voice or maximize content density.
- **Code-switched fillers**: "אז like" is a real construction in Israeli tech speech (Hebrew turn-marker + English filler). Cut the English "like" via your English lexicon, leave the "אז" as CONTEXT-DEPENDENT.
- **`no_verbatim=true` is the wrong knob.** That ElevenLabs flag is destructive, it drops fillers from the transcript entirely, which means the editor sub-agent never sees them and can't decide which to keep. Use `no_verbatim=false` (the default) and run this lexicon yourself.

## False positives to avoid

Do NOT auto-flag these even when they look like fillers:

- **בעצם** at the start of a sentence is almost always meaning-bearing ("Actually, what I meant was..."). Only flag mid-sentence occurrences.
- **טוב** when it directly modifies a noun ("מאמר טוב") is the adjective "good", not a filler.
- **נו** at the end of a question ("מה דעתך, נו?") is a genuine prompt for response.
- **ממש** before a noun ("ממש בית") is a real intensifier ("an actual house"), not filler.
- **וואלה** with rising intonation in response to a claim is genuine surprise, not filler.

## Pre-scan integration

Upstream Step 2 ("Pre-scan for problems") is the right place to flag any of these for the editor sub-agent. Output format:

```
- [012.34] אֶה (ALWAYS-FILLER, recommend cut)
- [045.67] כאילו (CONTEXT-DEPENDENT, editor decides)
- [089.12] אז (CONTEXT-DEPENDENT, mid-sentence, likely filler)
- [102.45] תראה (CONTEXT-DEPENDENT, turn-starter, likely filler)
```

The editor sub-agent then resolves the context-dependent items in its strategy decision, not at cut time.

## Sources

- ElevenLabs Scribe API behavior: https://github.com/elevenlabs/skills/blob/main/speech-to-text/references/transcription-options.md (word `type` field values, `no_verbatim` semantics).
- ElevenLabs Hebrew benchmark: https://elevenlabs.io/speech-to-text/hebrew (15.2% WER on FLEURS).
- Discourse markers in spoken Modern Hebrew: Maschler et al., John Benjamins (https://benjamins.com/catalog/prag.7.2.04mas).
- Filled-pauses analysis in Hebrew: ResearchGate, "Is It a Filler or a Pause? A Quantitative Analysis of Filled Pauses in Hebrew" (https://www.researchgate.net/publication/354527243).
- "tov" as discourse marker in Israeli Hebrew talk-in-interaction (Academia.edu, https://www.academia.edu/47718372).
- Native-speaker filler conventions: HebrewPod101 spoken-Hebrew filler guide; WordReference Modern Hebrew filler thread.
