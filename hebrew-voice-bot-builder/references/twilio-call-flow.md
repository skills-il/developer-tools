# Twilio Call Flow for an Israeli Business (tested)

A complete, runnable Flask call flow for the Step 7 IVR in SKILL.md. Every route
exists, every `<Gather>` and `<Record>` has an `action`, and the flow was exercised
with Flask's test client on 2026-10-01 (signed and unsigned requests, holiday
dates including Erev Purim and Yom HaAtzma'ut, a Hebcal outage, retry exhaustion,
voicemail fetch). `transcribe_hebrew` is the Step 2
function; `handle_voicemail_text` is your business logic.

What it handles that a minimal sample does not:

- **Webhook signatures.** Twilio signs every request with `X-Twilio-Signature`;
  the `twilio_signed` decorator rejects anything else with 403.
- **Holidays and erev chag.** Business hours come from Hebcal's Israel schedule
  (`i=on`): `yomtov` days and Yom HaAtzma'ut (a modern holiday, returned only with
  `mod=on`) are closed, and the day before a yom tov closes at 13:00. Matching on
  the "Erev" title instead would also shorten Erev Purim and Erev Tish'a B'Av,
  which are working days. A plain weekday check answers "open" on Yom Kippur.
  `prefetch_holidays()` fetches this year and next at startup (and should run
  daily inside the app process, e.g. a background thread, since each worker
  keeps its own in-memory copy) and persists them to `HOLIDAY_CACHE_FILE`, so a Hebcal outage keeps the
  last good table. If a year is missing AND Hebcal is down, the code logs at
  ERROR, retries at most every 10 minutes, and applies `HOLIDAY_FALLBACK`:
  `closed` (default, callers go to voicemail) or `open` (weekday hours). Chol
  hamoed, Yom HaZikaron and other partial days are operator choices; add them to
  the table if your business closes.
- **Bounded retries.** The attempt number rides in the URL; after 3 the caller
  goes to an agent instead of looping forever.
- **No `<Record>` loop.** Without `action`, `<Record>` re-requests the current
  document URL, which replays the prompt and records again.
- **Voicemail fetch.** The recording may not be accessible yet when the `action`
  callback fires, so the download runs from `recordingStatusCallback`.
- **E.164.** Twilio sends `From` as `+972...`; `to_e164_il` converts local
  `05X-XXXXXXX` / `0X-XXXXXXX` numbers for lookups. It raises on anything that
  is not an Israeli subscriber number with the right digit count (star codes,
  short codes, 1-700/1-800, an extension), so a bad number fails loudly instead
  of dialing someone else.

```python
import json
import logging
import os
import re
import tempfile
import time
from datetime import datetime, date, timedelta
from functools import wraps

import pytz
import requests
from flask import Flask, request, abort
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
VOICE = {"language": "he-IL", "voice": "Google.he-IL-Wavenet-A"}
MAX_ATTEMPTS = 3
# Department numbers in E.164. Twilio sends and expects +972..., not 05X.
DEPARTMENTS = {
    "1": os.environ.get("DEPT_RECEPTION", "+972500000001"),
    "2": os.environ.get("DEPT_NURSE", "+972500000002"),
    "0": os.environ.get("DEPT_AGENT", "+972500000000"),
}


def to_e164_il(local: str) -> str:
    """'054-1234567' or '03-1234567' -> '+972541234567' / '+97231234567'.

    Only Israeli subscriber numbers are converted: 05X and 07X with 9 digits
    after the 0, landlines 02/03/04/08/09 with 8. Star codes (*2700), short
    codes (101) and 1-XXX service numbers (1-700, 1-800) are not subscriber
    numbers, and a wrong digit count or an extension ('ext 5', 'שלוחה 5')
    would dial a stranger, so all of these raise. A number that is already
    E.164 for another country is returned unchanged."""
    s = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]", "", local).strip()
    s = s.removeprefix("tel:")
    if s.startswith(("*", "#")):
        raise ValueError(f"star code has no E.164 form: {local!r}")
    if re.search(r"[^\d\s+()\-.]", s):
        raise ValueError(f"extension or text in the number: {local!r}")
    digits = "".join(ch for ch in s if ch.isdigit())
    if digits.startswith("00"):
        digits = digits[2:]  # international prefix: 00972...
    elif not s.startswith("+") and not (digits.startswith("972") and len(digits) >= 11):
        digits = "972" + digits.lstrip("0")  # national form: 0X / 05X / 07X
    if not digits.startswith("972"):
        return "+" + digits  # already international, another country
    national = digits[3:].lstrip("0")  # also drops the "(0)" in +972 (0)54...
    if not re.fullmatch(r"[57]\d{8}|[2-489]\d{7}", national):
        raise ValueError(f"not an Israeli landline or mobile number: {local!r}")
    return "+972" + national


def twilio_signed(view):
    """Reject requests that do not carry a valid X-Twilio-Signature."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
        # Behind a proxy, request.url must be the public URL Twilio called.
        if not validator.validate(
            request.url, request.form, request.headers.get("X-Twilio-Signature", "")
        ):
            abort(403)
        return view(*args, **kwargs)
    return wrapper


# Holiday table: {year: {date: "closed" | "short"}}, kept in memory AND on disk,
# so a Hebcal outage keeps serving the last good copy.
# Use an absolute path on a writable volume (many container images have a
# read-only working directory).
HOLIDAY_CACHE_FILE = os.environ.get("HOLIDAY_CACHE_FILE", "holidays_cache.json")
# What to do when a year's table is missing AND Hebcal is unreachable:
# "closed" (default) routes callers to voicemail, so an outage can never answer
# "open" on Yom Kippur; "open" falls back to plain weekday hours.
HOLIDAY_FALLBACK = os.environ.get("HOLIDAY_FALLBACK", "closed")
_HOLIDAY_CACHE: dict = {}
_FAILED_AT: dict = {}


def _load_cache_file() -> None:
    try:
        with open(HOLIDAY_CACHE_FILE) as f:
            for year, days in json.load(f).items():
                _HOLIDAY_CACHE[int(year)] = {
                    date.fromisoformat(d): kind for d, kind in days.items()
                }
    except FileNotFoundError:
        pass
    except (OSError, ValueError):
        logging.exception("Holiday cache file %s is unreadable", HOLIDAY_CACHE_FILE)


def _save_cache_file() -> None:
    """Best effort: a failed write is logged and never fails a call."""
    tmp = None
    try:
        snapshot = dict(_HOLIDAY_CACHE)  # copy first: another thread may add a year
        data = {str(y): {d.isoformat(): k for d, k in days.items()}
                for y, days in snapshot.items()}
        # Unique temp name per writer, so concurrent workers do not collide.
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(HOLIDAY_CACHE_FILE) or ".",
                                   suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f)
        os.chmod(tmp, 0o644)  # mkstemp creates 0600; workers under another user must read it
        os.replace(tmp, HOLIDAY_CACHE_FILE)  # atomic: readers never see half a file
        tmp = None
    except (OSError, RuntimeError):
        logging.exception("Could not write holiday cache %s", HOLIDAY_CACHE_FILE)
    finally:
        if tmp is not None:  # the write failed after mkstemp: do not leave it behind
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _fetch_year(year: int) -> dict:
    """{date: 'closed' | 'short'} from Hebcal's Israel schedule (i=on).

    Closed: yom tov days, and Yom HaAtzma'ut (a modern holiday, so it needs
    mod=on and has no yomtov flag). Short: the day BEFORE a yom tov (erev chag,
    including Hoshana Raba). A bare "Erev ..." title match would also shorten
    Erev Purim and Erev Tish'a B'Av, which are ordinary working days.
    """
    resp = requests.get(
        "https://www.hebcal.com/hebcal",
        params={"v": 1, "cfg": "json", "maj": "on", "mod": "on",
                "i": "on", "year": year},
        timeout=5,
    )
    resp.raise_for_status()
    days, yomtov = {}, []
    for item in resp.json().get("items", []):
        day = date.fromisoformat(item["date"][:10])
        if item.get("yomtov"):
            days[day] = "closed"
            yomtov.append(day)
        elif item.get("title", "").startswith("Yom HaAtzma"):
            days[day] = "closed"
    for day in yomtov:
        days.setdefault(day - timedelta(days=1), "short")
    return days


def prefetch_holidays(years=None) -> None:
    """Call at startup and once a day (cron): fills this year and next ahead of
    time, so a live call never waits on Hebcal and an outage has a copy."""
    _load_cache_file()
    this_year = datetime.now(ISRAEL_TZ).year
    for year in years or (this_year, this_year + 1):
        try:
            _HOLIDAY_CACHE[year] = _fetch_year(year)
        except (requests.RequestException, ValueError, KeyError):
            # Keep the copy already loaded from disk, if any.
            logging.exception("Hebcal prefetch failed for %s", year)
    if _HOLIDAY_CACHE:
        _save_cache_file()


def israeli_holidays(year: int):
    """The year's table, or None when it is not cached and Hebcal is down."""
    if year in _HOLIDAY_CACHE:
        return _HOLIDAY_CACHE[year]
    if time.time() - _FAILED_AT.get(year, 0) < 600:
        return None  # recent failure: do not block every call on a 5 s timeout
    try:
        _HOLIDAY_CACHE[year] = _fetch_year(year)
    except (requests.RequestException, ValueError, KeyError):
        logging.error("Hebcal unreachable for %s and no cached table; "
                      "HOLIDAY_FALLBACK=%s", year, HOLIDAY_FALLBACK, exc_info=True)
        _FAILED_AT[year] = time.time()
        return None
    _save_cache_file()
    return _HOLIDAY_CACHE[year]


def is_open(now: datetime) -> bool:
    """Sun-Thu 9-17, Fri and erev chag 9-13; closed on Shabbat, yom tov
    and Yom HaAtzma'ut."""
    holidays = israeli_holidays(now.year)
    if holidays is None and HOLIDAY_FALLBACK != "open":
        return False
    special = (holidays or {}).get(now.date())
    if special == "closed" or now.weekday() == 5:
        return False
    if special == "short" or now.weekday() == 4:
        return 9 <= now.hour < 13
    return 9 <= now.hour < 17


prefetch_holidays()


@app.route("/voice/incoming", methods=["POST"])
@twilio_signed
def incoming():
    attempt = int(request.args.get("attempt", "1"))
    response = VoiceResponse()
    if attempt == 1:
        response.say("שלום, הגעתם למרפאה. השיחה מוקלטת.", **VOICE)
    if not is_open(datetime.now(ISRAEL_TZ)):
        # Closed: say so, and give the emergency number BEFORE voicemail,
        # so nobody leaves an urgent symptom on a recording until morning.
        response.say("המרפאה סגורה כעת. במקרה חירום רפואי, נתקו וחייגו "
                     "מאה ואחת, מגן דוד אדום.", **VOICE)
        response.redirect("/voice/voicemail")
        return str(response)
    if attempt > MAX_ATTEMPTS:
        response.redirect("/voice/dial?key=0")
        return str(response)
    gather = Gather(num_digits=1, action=f"/voice/menu?attempt={attempt}", timeout=8)
    gather.say("לקביעת תור, הקישו 1. לאחות, הקישו 2. לנציג, הקישו 0.", **VOICE)
    response.append(gather)
    response.redirect(f"/voice/incoming?attempt={attempt + 1}")
    return str(response)


@app.route("/voice/menu", methods=["POST"])
@twilio_signed
def menu():
    digit = request.form.get("Digits", "")
    attempt = int(request.args.get("attempt", "1"))
    response = VoiceResponse()
    if digit in DEPARTMENTS:
        response.redirect(f"/voice/dial?key={digit}")
    else:
        response.say("בחירה לא תקינה.", **VOICE)
        response.redirect(f"/voice/incoming?attempt={attempt + 1}")
    return str(response)


@app.route("/voice/dial", methods=["POST"])
@twilio_signed
def dial():
    response = VoiceResponse()
    # If nobody answers, Twilio requests the action URL: send to voicemail.
    response.dial(DEPARTMENTS[request.args.get("key", "0")],
                  timeout=25, action="/voice/voicemail")
    return str(response)


@app.route("/voice/voicemail", methods=["POST"])
@twilio_signed
def voicemail():
    response = VoiceResponse()
    if request.form.get("DialCallStatus") == "completed":
        response.hangup()
        return str(response)
    response.say("השאירו הודעה אחרי הצפצוף ונחזור אליכם.", **VOICE)
    # Without `action`, <Record> re-requests THIS url and loops.
    response.record(max_length=120, play_beep=True,
                    action="/voice/voicemail-done",
                    recording_status_callback="/voice/recording-ready")
    return str(response)


@app.route("/voice/voicemail-done", methods=["POST"])
@twilio_signed
def voicemail_done():
    response = VoiceResponse()
    response.say("תודה, ההודעה נקלטה.", **VOICE)
    response.hangup()
    return str(response)


@app.route("/voice/recording-ready", methods=["POST"])
@twilio_signed
def recording_ready():
    # RecordingUrl may not be fetchable yet in the <Record> action callback,
    # which is why this runs from recordingStatusCallback instead.
    url = request.form["RecordingUrl"] + ".wav"
    audio = requests.get(url, auth=(os.environ["TWILIO_ACCOUNT_SID"],
                                    os.environ["TWILIO_AUTH_TOKEN"]), timeout=30)
    audio.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio.content)
        tmp.flush()
        text = transcribe_hebrew(tmp.name)  # Step 2 of SKILL.md
    handle_voicemail_text(request.form.get("CallSid"), text)  # your business logic
    return ("", 204)
```

## Spoken input inside `<Gather>`

Twilio's only Hebrew row for Google (`iw-IL`) is in a language table it marks
deprecated (Google v1 STT, Gather 1.0). For Gather 2.0, Twilio maps Deepgram models
to Deepgram's own language list, and Deepgram lists Hebrew (`he`) for Nova-3, so
`<Gather input="dtmf speech" speechModel="deepgram_nova-3" language="he">` is the
documented route to test. Keep DTMF in `input` as the fallback. `googlev2_chirp_3`
is accepted as a speechModel, but Twilio shows no Hebrew row for it.

## Live audio for a conversational bot

A TwiML webhook carries no audio. A conversational bot (Step 1, "Voice bot")
needs one of:

- **Media Streams** (`<Connect><Stream>`): the audio arrives over a WebSocket as
  base64 `audio/x-mulaw` at `8000` Hz, always. Convert it before sending it to an
  STT engine that expects linear PCM at another rate. On a bidirectional stream,
  send the bot's speech back as `media` messages in the same format, send a
  `mark` after each TTS chunk to learn when it has played, and send `clear` when
  the caller starts talking: Twilio empties its audio buffer, which is how
  barge-in works.
- **OpenAI Realtime over SIP**: point a SIP trunk at
  `sip:$PROJECT_ID@sip.api.openai.com;transport=tls` (or
  `sip:$PROJECT_ID@sip-eu.api.openai.com;transport=tls` for European data
  residency) and handle the `realtime.call.incoming` webhook.

If you use `gpt-live-transcribe` for streaming STT, note that it does not
support `server_vad` or `semantic_vad`: your application must detect the end of
each turn and commit the audio itself (and run your own VAD to trigger `clear`).

Twilio ConversationRelay is the managed alternative, but its voice-configuration
page lists no Hebrew voice; it points to the Twilio TTS voice table for Google
voices, which does have `he-IL`. Test Hebrew speech in and out end to end before
choosing it over the two routes above.

## Clinics and other sensitive callers

A clinic IVR that records voicemails about symptoms or medication, or asks for a
Teudat Zehut, is collecting health and identity data and sending it to a speech
vendor abroad by default. Collect the minimum (route medication questions to a
nurse line rather than free-text voicemail), set a retention period, prefer the
vendors' EU endpoints (`europe-west4` / `eu` on Google, the OpenAI EU SIP
endpoint), and confirm the privacy and data-transfer obligations that apply to
the business with a qualified professional before launch.
