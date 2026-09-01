# JFrog DevOps

## הוראות

### שלב 1: זיהוי פעולת ה-DevOps
| פעולה | כלי JFrog | API/CLI | נדרש אימות |
|-------|----------|---------|------------|
| העלאת/פריסת artifact | Artifactory | PUT /{repo}/{path} או jf rt upload | כן |
| הורדת artifact | Artifactory | GET /{repo}/{path} או jf rt download | כן (אלא אם אנונימי) |
| חיפוש artifacts | Artifactory | AQL או jf rt search | כן |
| Docker push/pull | Artifactory | Docker API או jf docker | כן |
| פרסום מידע build | Artifactory | PUT /api/build או jf rt build-publish | כן |
| קידום build | Artifactory | POST /api/build/promote | כן (מנהל) |
| סריקת CVE | Xray | POST /api/v1/scanArtifact או jf xr scan | כן |
| יצירת watch/policy | Xray | POST /api/v2/watches | כן (מנהל) |
| הפקת דוח | Xray | POST /api/v1/reports/vulnerabilities | כן |
| ייצוא SBOM (SPDX או CycloneDX) | Xray | POST /xray/api/v2/component/exportDetails, או jf scan --format=cyclonedx (CycloneDX בלבד) | כן |
| סינון חבילות OSS לפני הורדה | Curation | מוגדר לכל remote repo | כן (מנהל) |
| ניהול מודלי ML (Hugging Face, MLflow, NIM) | Artifactory ML repo | jf rt upload או FrogML SDK | כן |
| ניקוי artifacts ישנים | Artifactory | AQL + מחיקה או מדיניות שמירה | כן (מנהל) |

### שלב 2: הגדרת אימות

**אפשרות א: JFrog CLI (מומלץ):**
```bash
# Configure JFrog CLI with access token (recommended)
jf config add my-server \
  --url="https://acme.jfrog.io" \
  --access-token="YOUR_ACCESS_TOKEN" \
  --interactive=false

# Verify connection
jf rt ping
```

**אפשרות ב: REST API עם curl:**
```bash
# Read the host and token from the environment so neither is hardcoded
# or left in shell history. JF_URL is your platform base URL.
export JF_URL="https://acme.jfrog.io"

# Using access token (recommended)
curl -H "Authorization: Bearer $JF_ACCESS_TOKEN" \
  "$JF_URL/artifactory/api/system/ping"

# Using identity token (reference token, also works as Bearer)
curl -H "Authorization: Bearer $JF_REFERENCE_TOKEN" \
  "$JF_URL/artifactory/api/system/ping"
```

> מפתחות API ישנים (header של `X-JFrog-Art-Api`) הגיעו לסוף חיים ברבעון הרביעי של 2024 ומכובים כברירת מחדל מ-Artifactory 7.98 ואילך. השתמשו ב-access tokens או reference tokens (שניהם נשלחים כ-`Authorization: Bearer`).

**אפשרות ג: OIDC ל-CI (בלי סודות ארוכי-טווח):**
```yaml
# דוגמת GitHub Actions עם jfrog/setup-jfrog-cli
- uses: jfrog/setup-jfrog-cli@v5
  with:
    oidc-provider-name: my-github-oidc-provider
  env:
    JF_URL: https://acme.jfrog.io
```
> גרסה v5 רצה על runtime של node24. גרסה v4 נשארת על node20 ועדיין נתמכת, אז הצמידו `@v4` רק אם ה-runner שלכם תקוע על גרסה ישנה. אחרת השתמשו ב-`@v5`.
מגדירים את ה-OIDC integration פעם אחת ב-JFrog (Administration > Identity and Access > Integrations > OIDC), ואז ה-CI מחליף JWT קצר-טווח ל-access token בזמן ריצה. זה הנתיב המומלץ של JFrog ל-GitHub Actions, GitLab, Buildkite ו-Jenkins.

**אפשרות ד: לקוח Python:**
```python
import requests

class ArtifactoryClient:
    """Client for JFrog Artifactory REST API."""

    def __init__(self, base_url, access_token):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def ping(self):
        """Health check."""
        r = self.session.get(f"{self.base_url}/api/system/ping")
        return r.text == "OK"

    def list_repos(self, repo_type=None):
        """List repositories, optionally filtered by type."""
        params = {}
        if repo_type:
            params["type"] = repo_type
        r = self.session.get(f"{self.base_url}/api/repositories", params=params)
        return r.json()

    def deploy_artifact(self, repo_key, path, file_path, properties=None):
        """Deploy (upload) an artifact to a repository."""
        url = f"{self.base_url}/{repo_key}/{path}"
        if properties:
            prop_str = ";".join(f"{k}={v}" for k, v in properties.items())
            url += f";{prop_str}"
        with open(file_path, "rb") as f:
            r = self.session.put(url, data=f,
                                 headers={"Content-Type": "application/octet-stream"})
        return r.json()

    def download_artifact(self, repo_key, path, dest_path):
        """Download an artifact from a repository."""
        r = self.session.get(f"{self.base_url}/{repo_key}/{path}", stream=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest_path

    def search_aql(self, aql_query):
        """Search using Artifactory Query Language."""
        r = self.session.post(
            f"{self.base_url}/api/search/aql",
            data=aql_query,
            headers={"Content-Type": "text/plain"}
        )
        return r.json()

    def get_build_info(self, build_name, build_number):
        """Get build information."""
        r = self.session.get(f"{self.base_url}/api/build/{build_name}/{build_number}")
        return r.json()

    def promote_build(self, build_name, build_number, target_repo,
                      status="released", copy=False):
        """Promote a build to a target repository."""
        r = self.session.post(
            f"{self.base_url}/api/build/promote/{build_name}/{build_number}",
            json={
                "status": status, "targetRepo": target_repo,
                "copy": copy, "artifacts": True, "dependencies": False
            }
        )
        return r.json()
```

### שלב 3: פעולות Docker Registry

**הגדרת Docker לעבודה עם Artifactory:**
```bash
# התחברות ל-Docker registry של Artifactory.
# שם המארח של ה-registry תלוי בדרך שבה מגיעים לפלטפורמה:
#   SaaS / שיטת subdomain:        acme.jfrog.io/<repo-key>
#   שיטת repository-path:         <host>/artifactory/api/docker/<repo-key>
#   שיטת port (self-hosted):      <host>:<port>
# למטה מוצגת רק הצורה הראשונה. ב-Artifactory self-hosted בלי reverse proxy
# שמוגדר לשיטת ה-subdomain, הצורה הקצרה לא נפתרת וצריך אחת מהשתיים האחרות.
docker login acme.jfrog.io

# Push image through Artifactory
docker tag myapp:latest acme.jfrog.io/docker-local/myapp:1.0.0
docker push acme.jfrog.io/docker-local/myapp:1.0.0

# Pull image through Artifactory (also caches remote images)
docker pull acme.jfrog.io/docker-remote/nginx:latest
```

> **הפקודה `jf config add` לא מחברת את ה-Docker daemon.** היא מגדירה את מאגר הפרטים של JFrog CLI עצמו. תחת OIDC (אפשרות ג) אין בכלל סיסמה ארוכת טווח להזין ל-`docker login`, וזו בדיוק המטרה של OIDC. שלושה מסלולים עובדים: הריצו `jf docker push/pull`, שמתווך ל-daemon דרך ההגדרות של ה-CLI; או ייצאו את ה-access token שהוחלף והזרימו אותו, `echo "$JF_ACCESS_TOKEN" | docker login acme.jfrog.io -u <username> --password-stdin`; או תנו ל-`jfrog/setup-jfrog-cli` לייצא את הטוקן ל-job והשתמשו באותה הזרמה. לעולם אל תשימו את הטוקן בארגומנט `docker login -p`, ששם אותו ב-argv ובהיסטוריית ה-shell.

**שימוש ב-JFrog CLI עבור Docker (מוסיף מידע build):**
```bash
# Push with build info collection
jf docker push acme.jfrog.io/docker-local/myapp:1.0.0 \
  --build-name=myapp-build --build-number=42

# Pull with build info collection
jf docker pull acme.jfrog.io/docker-remote/nginx:latest \
  --build-name=myapp-build --build-number=42
```

### שלב 4: מידע Build וקידום

**פרסום מידע build מצינור CI:**
```bash
# Collect environment variables
jf rt build-collect-env myapp-build 42

# Upload artifacts with build info
jf rt upload "target/*.jar" libs-release-local/com/acme/myapp/1.0.0/ \
  --build-name=myapp-build --build-number=42

# Publish build info
jf rt build-publish myapp-build 42

# Promote build from staging to release
jf rt build-promote myapp-build 42 libs-release-local \
  --status="released" --copy
```

**תבנית צינור קידום:**
```
[Build] -> libs-snapshot-local (פיתוח)
        -> libs-staging-local (אושר ע"י QA)
        -> libs-release-local (מוכן לייצור)
```

### שלב 5: סריקות אבטחה עם Xray

**שימוש ב-JFrog CLI לסריקה:**
```bash
# Audit current project dependencies
jf audit --watches "prod-security-watch"

# Scan a specific Docker image
jf docker scan acme.jfrog.io/docker-local/myapp:1.0.0

# Real CI gate on the SOURCE tree: policy comes from an Xray watch
jf audit --watches=prod-security-watch --fail=true   # exit code 3 when a Fail Build rule matches

# Real CI gate on the BUILD you just published (what most pipelines actually want)
jf build-scan my-build 42 --fail --vuln

# --min-severity only filters what is DISPLAYED. Without --watches, --project or
# --repo-path no policy violations are evaluated at all, so this gates nothing:
jf audit --min-severity=High

# Generate SBOM in CycloneDX (with VEX data from Xray 3.67+)
jf scan --format=cyclonedx --sbom "build/libs/*.jar" > sbom.cdx.json
```

> הדגל `--fail` הוא ברירת המחדל ממילא, אז העברה שלו לבדה לא משנה כלום. מה שהופך את השער לאמיתי זה `--watches`, `--project` או `--repo-path`, ו**שלושתם סותרים זה את זה**: התיעוד של `--watches` אומר "Incompatible with --project and --repo-path", וכל אחד מהשניים האחרים מתקבל "only if" השניים האחרים חסרים. העברה של שניים מהם היא שגיאת CLI קשיחה, לא צמצום.
>
> **הפקודות `jf audit` ו-`jf build-scan` שומרות על אובייקטים שונים.** הפקודה `audit` פותרת את התלויות המוצהרות בעץ המקור. הפקודה `build-scan <name> <number>` סורקת את ה-build info ואת ה-artifacts שהפייפליין באמת פרסם, וזה מה שתופס CVE שיושב בשכבה מוצללת, מוטמעת או בבסיס ה-image ולא מופיע ב-manifest שלכם. פרסמו build info (שלב 4) ואז שימו שער עם `build-scan`. הדגלים שלה הם `--fail`, `--vuln`, `--violations`, `--rescan`, `--trigger-scan-retries`, `--format`, `--project`.
>
> **מה הופך שער ל-no-op בשקט**, בערך לפי סדר השכיחות:
> 1. הרפוזיטורי שאתם סורקים לא באינדקס של Xray. שום דבר לא נכנס לאינדקס כברירת מחדל, ראו את ההערה על אינדוקס למטה. repo בלי אינדקס מחזיר אפס הפרות ובניה ירוקה.
> 2. ה-watch קיים אבל לא פעיל, או שלמדיניות שלו אין כלל עם `fail_build`. הפעולה `block_download` היא פעולה אחרת ולא מפילה בניה.
> 3. משאבי ה-watch לא כוללים בפועל את ה-repo או ה-build שנסרק.
> 4. כלל ignore או waiver כבר מדכא את ההפרה.
> 5. הוגדר `--format=cyclonedx`: ה-help של הדגל מזהיר שפורמט CycloneDX נושא פגיעויות ולא הפרות, אז ההקשר של המדיניות הולך לאיבוד.
> 6. הוגדר `--vuln`, שמדווח על כל הפגיעויות בלי קשר למדיניות.
> 7. הסורקים SAST, IaC וניתוח קונטקסטואלי הם זכאויות של JFrog Advanced Security, אז שער נכון מבנית עדיין עלול לסרוק פחות ממה שאתם מניחים.
> 8. קוד יציאה 3 נבלע על ידי `continue-on-error`, `|| true` או pipe. ודאו שהשלב באמת נכשל.
>
> **אינדוקס ב-Xray הוא תנאי מקדים, לא שלב פתרון בעיות.** ברפוזיטורי חדש Xray לא מאנדקס כלום עד שמוסיפים אותו תחת Indexed Resources, ורק סוגי חבילות נתמכים נכנסים לאינדקס בכלל. ודאו שה-repo מאונדקס **וגם** שה-artifact הספציפי נסרק (`POST /xray/api/v1/artifact/status`, או הפקודה `scan-status` בסקריפט `xray_client.py` המצורף) לפני שאתם מתייחסים לתוצאה ריקה כאל נקי. שימו לב לאסימטריה: `jf audit` לא צריך אינדוקס כי הוא קורא את ה-manifests שלכם, ואילו `jf docker scan`, `jf build-scan`, watches ו-API הסיכום כן צריכים.
> פורמט CycloneDX הוא ה-SBOM היחיד ש-JFrog CLI מפיק. אין `jf scan --format=spdx` וה-CLI פשוט דוחה אותו, וה-help של פקודת enrich אומר במפורש ש-"Input must be CycloneDX JSON; SPDX or other formats are not accepted". פורמט SPDX מגיע רק מממשק ה-Xray (Scans List, ואז More Options, ואז Export Scan Data) או מ-`POST /xray/api/v2/component/exportDetails` עם `"spdx": true` **ובנוסף** `"spdx_format"` (בערך `json` או `tag-value`), שהוא חובה בכל פעם שבוחרים `spdx`. קריאה בלי אף content selector מחזירה 400.
> הפקודה `jf docker scan` מקבלת בדיוק את אותם ערכי `--format` כמו `jf scan` (table, json, simple-json, sarif, cyclonedx), כי שתי הפקודות חולקות הגדרת flag אחת. אפשר להפיק SBOM של image ישירות עם `jf docker scan --format=cyclonedx`.
> הדגל `--sbom` הוא **בוליאני** לתצוגה, לא בורר קלט: הוא גורם לפלט להציג את כל רכיבי ה-SBOM ולא רק את המושפעים, והוא מתעלם ממנו אלא אם `--format` הוא `table` או `cyclonedx`. יעד הסריקה נשאר ארגומנט המיקום.

הראשי תיבות CBOM כאן הן **Cryptography** Bill of Materials, לא דוח secrets. עם JFrog Advanced Security, אפשרות ה-CBOM מעשירה SBOM בפורמט CycloneDX בנכסים הקריפטוגרפיים שסריקת ה-secrets מצאה, ומשבצת כל אחד מהם כרכיב `cryptographic-asset` (תעודות, מפתחות API ומפתחות סוד, וסודות גנריים). זו העשרה של ה-SBOM, לא ייצוא של ממצאי ה-secrets. Xray גם יודע לקלוט SBOM חיצוניים בפורמט SPDX או CycloneDX (כולל VEX לניתוח קונטקסטואלי) כדי לבדוק artifacts של ספקים.

**Frogbot לסריקת pull requests:**
```yaml
# .github/workflows/frogbot-scan-pr.yml
- uses: jfrog/frogbot@v3
  env:
    JF_URL: ${{ secrets.JF_URL }}
    JF_ACCESS_TOKEN: ${{ secrets.JF_ACCESS_TOKEN }}
    JF_GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
הבוט Frogbot סורק PRs, מגיב על ממצאים, ויודע לפתוח PRs לתיקונים. Frogbot עצמו הוא קוד פתוח וחינמי להרצה, אבל הסורקים לא אחידים: SCA דורש חיבור ל-JFrog Platform, ואילו SAST, IaC וניתוח קונטקסטואלי הם פיצ'רים של JFrog Advanced Security. אמתו אילו מהם המנוי שלכם באמת כולל לפני שאתם מבטיחים שער על PRs. זו עדיין נקודת התחלה טובה לפרויקט OSS ישראלי. הצמידו `@v3`: גרסה V3 סורקת סטטית בלי להריץ את מנהלי החבילות שלכם, אז היא מחזירה ממצאים גם כשה-build נכשל, והיא מזהה לבד repos מקוננים ורב-חבילתיים. גרסה V2 נמצאת בסאנסט (רק תיקוני באגים ואבטחה קריטיים, בלי פיצ'רים חדשים).

### שלב 5b: ניהול מודלי AI ו-ML (JFrog ML + AI Catalog)

הפלטפורמות JFrog ML (מרץ 2025, פרי רכישת Qwak) ו-AI Catalog (ספטמבר 2025) מרחיבים את Artifactory ו-Xray כך שיתמכו במודלי ML. סוג ה-repo **Machine Learning** שומר מודלים של Hugging Face לצד PyTorch, ONNX, .pkl, .joblib, .pth ו-.cbm באותו repo פורמט-אגנוסטי, עם תמיכת FrogML SDK. הגרסה 7.111.1 היא לא מינימום: רפוזיטוריות Hugging Face נתמכות מ-Artifactory 7.77, ומ-7.111.1 כל רפוזיטורי Hugging Face חדש, מקומי או מרוחק, משתמש ב-layout של Machine Learning **כברירת מחדל**. תמיכת פרוטוקול Xet מתועדת ספציפית לרפוזיטוריות Hugging Face.

```bash
# יוצרים ML repo (דרך ממשק הניהול או REST):
# Administration > Repositories > Add Repository > Local > Machine Learning

# מעלים מודל עם build info
jf rt upload "model.onnx" ml-local/myapp/v1.0.0/ \
  --build-name=ml-build --build-number=42

# Scan model files for embedded code-execution payloads (needs JFrog Advanced Security)
jf malicious-scan --working-dirs=./models

# Binary-scan a model artifact you already have on disk
jf scan ./model.onnx --format=sarif
```

> סריקת מודלים היא לא המסלול של Docker. הפקודה `jf docker scan` מאתרת images דרך ה-daemon המקומי, ולכן הפניה שלה לנתיב של repo מסוג ML פשוט נכשלת. הפקודה `jf malicious-scan` (בבטא) מכוונת למשפחת ההתקפות של pickle deserialization, שסריקת קונטיינרים לא מכסה.

**AI Catalog** מאפשר לצוותי פלטפורמה לנהל באופן מרכזי גישה ל-OpenAI, Anthropic, NVIDIA NIM (כולל מודלי Nemotron עם משקלות פתוחים) ו-Hugging Face, מאחורי שכבת governance אחת: סריקה, lineage, model cards ופריסה ב-click אחד.

### שלב 6: תבניות AQL (Artifactory Query Language)

**שאילתות AQL נפוצות לניהול artifacts:**

```
// חיפוש artifacts שנוצרו ב-7 הימים האחרונים
items.find({"created": {"$last": "7d"}, "repo": "libs-release-local"})

// חיפוש Docker images לפי שם
items.find({
    "repo": "docker-local",
    "path": {"$match": "myapp/*"},
    "name": "manifest.json"
}).include("repo", "path", "name", "created", "size")

// חיפוש artifacts גדולים מ-100MB
items.find({
    "size": {"$gt": 104857600},
    "repo": {"$match": "libs-*-local"}
}).sort({"$desc": ["size"]})

// חיפוש artifacts שלא הורדו 90 יום
items.find({
    "stat.downloaded": {"$before": "90d"},
    "repo": "libs-release-local"
})

// חיפוש artifacts לפי property
items.find({
    "@build.name": "myapp-build",
    "@build.number": "42"
})
```

## דוגמאות

### דוגמה 1: הקמת מאגר Maven
המשתמש אומר: "הקימו מבנה מאגר Maven ב-Artifactory"
תוצאה: יצירת מאגר מקומי (libs-release-local, libs-snapshot-local), מאגר מרוחק (jcenter-remote המצביע ל-Maven Central), מאגר וירטואלי (libs המאגד מקומי + מרוחק), הגדרת resolution ופריסה.

### דוגמה 2: צינור CI/CD עם Docker
המשתמש אומר: "שלבו את Artifactory כ-Docker registry בצינור ה-CI שלנו"
תוצאה: הגדרת מאגר Docker וירטואלי, הגדרת docker login ב-CI, דחיפת images עם מידע build דרך jf docker push, סריקה עם Xray, קידום מ-staging לייצור.

### דוגמה 3: שער אבטחה
המשתמש אומר: "חסמו פריסת artifacts עם CVE קריטיים"
תוצאה: יצירת מדיניות אבטחה ב-Xray שחוסמת CVE קריטיים, יצירת watch על מאגרי ייצור, הגדרת פעולת fail_build לשילוב CI, הגדרת התראות על הפרות.

### דוגמה 4: ניקוי אחסון
המשתמש אומר: "נקו artifacts ישנים כדי לפנות מקום ב-Artifactory"
תוצאה: שימוש ב-AQL לאיתור artifacts שלא הורדו 90+ יום, זיהוי artifacts מסוג snapshot ישנים מ-30 יום, יצירת סקריפט ניקוי עם מצב dry-run, תזמון ניקוי קבוע.

## משאבים מצורפים

### סקריפטים
- `scripts/artifactory_client.py`, לקוח ל-REST API של JFrog Artifactory שמכסה בדיקות תקינות, רשימת ויצירת מאגרים, העלאה/הורדה/מחיקה של artifacts, חיפוש AQL, ניהול properties, שליפת מידע build וקידום build. קורא את הטוקן מ-`JFROG_ACCESS_TOKEN` בלבד, לעולם לא מ-argv. קידום מעתיק כברירת מחדל, ו-`--move` הוא opt-in. דורש `requests` (`pip3 install requests`). הרצה: `python3 scripts/artifactory_client.py --help`
- `scripts/xray_client.py`, לקוח REST API של JFrog Xray. הפקודה `summary` **קוראת** תוצאת סריקה קיימת ולא סורקת; `trigger-scan` מתחילה סריקה ומקבלת component ID (בערך `docker://image:tag`) ולא נתיב repo; `scan-status` מבדילה בין "נסרק ונקי" לבין "מעולם לא נסרק", מה ש-summary ריק לא יכול. הלקוח מכסה גם ניהול מדיניות ו-watches, חיפוש הפרות והפקת דוחות. קורא את הטוקן מ-`JFROG_ACCESS_TOKEN` בלבד, לעולם לא מ-argv. דורש `requests` (`pip3 install requests`). הרצה: `python3 scripts/xray_client.py --help`

### חומרי עזר
- `references/domain-checklist.md`, חוזה הכיסוי של הסקיל הזה, כולל רישום מתוארך של מה שהוא במכוון עוד לא מכסה ולמה. קראו אותו לפני שאתם מניחים שנושא מסוים מטופל.
- `references/api-reference.md`, מדריך מהיר לנקודות קצה של REST API ב-Artifactory וב-Xray מאורגנים לפי קטגוריה (מערכת, מאגרים, artifacts, חיפוש, properties, מידע build, סריקה, מדיניות, הפרות), דף פקודות JFrog CLI, תבניות שאילתות AQL, הסברי סוגי מאגרים ומוסכמות מבנה מאגר סטנדרטיות. עיינו בו בעת בניית קריאות API, כתיבת שאילתות AQL, או הגדרת מבני מאגרים.

## מלכודות נפוצות

- **JFrog Pipelines הגיע לסוף חיים ב-1 במאי 2026.** לקוחות חדשים כבר לא יכולים להקצות Pipelines, ולקוחות קיימים חייבים להיות אחרי ההגירה. JFrog ממליצים על GitHub Actions, GitLab CI, Jenkins או Azure DevOps עם `jfrog/setup-jfrog-cli`. אם צוות ישראלי עדיין על Pipelines, ההגירה כבר באיחור: אין יותר feature updates ואין תמיכה.
- **המועד האחרון להגירת רפוזיטוריות Hugging Face הישנות חלף ביוני 2026.** כל repo מסוג Hugging Face שעדיין על ה-layout הישן, כלומר כל אחד שנוצר לפני ש-Artifactory 7.111.1 הפך את ה-layout החדש לברירת המחדל, ולא הועבר ל-layout של "Machine Learning" רץ היום ללא תמיכה, ואין יותר התחייבות לפונקציונליות מלאה. התייחסו ל-repo שלא הוגר כאל תקלה פתוחה, לא כאל משימה שממתינה בתור. ההגירה היא חד-כיוונית בפועל (ה-API של `restore_layout` מוחק חבילות שנוספו אחרי השדרוג), repos של federation לא יכולים לערבב layouts, ומכסות ה-rate limit של Hugging Face Hub עולות בזמן ה-cache warming, אז תכננו את החיתוך מראש ולא תוך כדי תנועה.
- **מפתחות API הגיעו לסוף חיים ברבעון הרביעי של 2024.** מפתחות ישנים עוד עובדים על מופעים ישנים, אבל אי אפשר ליצור חדשים. הגרו כל שימוש ב-`X-JFrog-Art-Api` ל-access tokens או reference tokens (שניהם נשלחים כ-`Authorization: Bearer ...`).
- **OIDC הוא היום שיטת האימות המומלצת של JFrog ל-GitHub Actions.** דורש JFrog CLI 2.75.0+ וה-workflow צריך `permissions: id-token: write`. טוקני access ארוכי טווח ב-GitHub secrets עדיין נתמכים, אבל לא מומלצים ל-pipelines חדשים.
- **אזורי JFrog Cloud בישראל: תשאלו, אל תניחו.** JFrog כבר לא מפרסמת רשימת אזורי ענן פומבית. הדף שהסקיל הזה ציטט קודם נטען ריק, הכתובת `jfrog.com/cloud-service-providers-and-regions/` מחזירה 404, ודף האזורים במודלי האירוח עושה 301 לדף ארכיטקטורה של self-managed שאין בו אזורים בכלל (שלושתם נבדקו מחדש ב-2026-09-02). לכן אנחנו לא יכולים לאמת מול שום מקור רשמי אילו אזורים בישראל, אם בכלל, קיימים ב-JFrog SaaS. **אל תגידו לקונה ישראלי ששמירת המידע בישראל אפשרית על JFrog SaaS בלי לאמת את זה מול JFrog ישירות.** הנקודה המבנית עדיין נכונה ושווה להעלות ברכש: האזור נקבע בזמן פתיחת המנוי ואי אפשר לשנות אותו אחר כך בלי הגירה, אז סגרו את נושא שמירת המידע לפני ה-onboarding ולא אחריו.
- **שקיפות תמחור משתנה לפי tier.** JFrog מפרסמים בפומבי Pro בערך 150 דולר לחודש ו-Enterprise X בערך 950 דולר לחודש ל-SaaS, כשה-Enterprise+ ב-quote. תמחור self-managed לא מתפרסם בכלל. המספרים שמסתובבים עליו מגיעים ממעקבים של צד שלישי שלא הצלחנו לאמת, אז אל תצטטו אף אחד מהם. קונים ישראלים צריכים לקבל תמחור עדכני ישירות מ-JFrog ישראל לפני התכנון.
- **JFrog היא חברה ישראלית**, שהוקמה ויושבת בנתניה (נסחרת בנאסד"ק תחת FROG) עם נוכחות פיתוח משמעותית בישראל. לצוות ישראלי זה אומר תמיכה ארגונית באזור הזמן שלכם, ארגון מכירות ו-solution architects מקומי, ואנשי SE דוברי עברית. זה שיקול רכש אמיתי בפני עצמו. הוא לא מתפרש לשמירת מידע בישראל: ראו את סעיף האזורים למעלה, שלא הצלחנו לאמת מול שום מקור רשמי.
- **הפרת רישוי היא לא תמיד המדיניות שלכם מדברת.** לפני שאתם מתייחסים אליה כאל חסם אמיתי, בדקו איזו מדיניות ה-watch באמת ירש: מדיניות פנימית מתירנית עדיין עלולה להציף הפרות מרשימת רישיונות חסומים שהגיעה עם תבנית של חברת אם שאתם לא כתבתם. לא אימתנו כיצד Xray מייצג זהות רישיון פנימית, אז קראו את המדיניות במקום להניח את המנגנון.

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| Artifactory REST API | https://docs.jfrog.com/artifactory/reference | נקודות קצה, תחביר שאילתות, AQL. האינדקס הקריא-למכונה נמצא ב-https://docs.jfrog.com/artifactory/llms.txt |
| תיעוד Xray | https://jfrog.com/xray/ | סריקת פגיעויות, ציות רישוי, מדיניות, SBOM ו-VEX |
| JFrog CLI Releases | https://github.com/jfrog/jfrog-cli/releases | גרסה אחרונה של ה-CLI (2.122.0 נכון לאוגוסט 2026), changelog |
| JFrog Docker Registry | https://jfrog.com/help/r/jfrog-artifactory-documentation/docker-repositories | ניהול אימג'י Docker, פרוקסי Docker Hub |
| JFrog ML | https://jfrog.com/jfrog-ml/ | פלטפורמת MLOps (מרכישת Qwak), model registry, FrogML SDK |
| JFrog AI Catalog | https://jfrog.com/press-room/jfrog-launches-ai-catalog-to-secure-and-govern-ai-model-delivery/ | Governance ל-OpenAI, Anthropic, NVIDIA NIM ו-Hugging Face |
| Machine Learning Repositories | https://jfrog.com/help/r/jfrog-artifactory-documentation/log-hugging-face-models | סוג ה-repo החדש, הגירת HF ביוני 2026 |
| JFrog Curation | https://jfrog.com/curation/ | סינון חבילות OSS, Compliant Version Selection, וכלי MCP לניהול בקשות waiver ב-Curation |
| Frogbot | https://github.com/jfrog/frogbot | בוט סריקת PR חינמי, SCA + SAST + IaC. V3 היא הנוכחית, V2 בסאנסט |
| OIDC עם GitHub Actions | https://jfrog.com/help/r/jfrog-platform-administration-documentation/configure-jfrog-platform-oidc-integration-with-github-actions | האימות המומלץ ל-CI, דורש CLI 2.75.0+ |
| Pipelines End of Life | https://docs.jfrog.com/releases/docs/pipeline-deprecation-end-of-life | EOL ב-1 במאי 2026, הנחיות הגירה |
| מודלי אירוח של JFrog Cloud | https://docs.jfrog.com/installation/docs/system-architecture | סקירת מודלי האירוח. שימו לב: רשימת האזורים הפומבית כבר לא מתפרסמת, אז אמתו זמינות אזור מול JFrog ישירות |
| Xray SBOM Export API | https://docs.jfrog.com/security/reference/export-component-details-v1-deprecated_components-v2-openapi | POST /xray/api/v2/component/exportDetails, המסלול התוכנתי היחיד ל-SPDX |

## פתרון בעיות

### שגיאה: "401 Unauthorized" בקריאות API
סיבה: access token לא תקין או שפג תוקפו, או הרשאות לא מספיקות
פתרון: צרו access token חדש בממשק JFrog (Administration, לאחר מכן Identity and Access, ואז Access Tokens). ודאו שלטוקן יש את ההרשאות הנדרשות לפעולה. מפתחות API נמצאים בתהליך הוצאה משימוש -- העדיפו access tokens.

### שגיאה: "Docker push נכשל עם unknown blob"
סיבה: דחיפת שכבת Docker client נכשלה או הפרעה ברשת
פתרון: נסו שוב את הדחיפה. אם הבעיה חוזרת, בדקו את תקינות שכבת האחסון של Artifactory. ודאו שמאגר ה-Docker מקבל את ארכיטקטורת ה-image (linux/amd64 מול arm64). בדקו את גודל ההעלאה המרבי בהגדרות Artifactory.

### שגיאה: "סריקת Xray לא מציגה תוצאות"
סיבה: אינדוקס Xray אינו מופעל למאגר, או שהאינדוקס טרם הושלם
פתרון: ודאו ש-Xray מוגדר לאנדקס את המאגר היעד (Administration, לאחר מכן Xray, ואז Indexed Resources). מאגרים חדשים צריכים להתווסף באופן מפורש. אינדוקס ראשוני של מאגרים גדולים עשוי לקחת שעות.
