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
| ייצוא SBOM (SPDX או CycloneDX) | Xray | POST /api/v1/sbom או jf scan --format=cyclonedx | כן |
| סינון חבילות OSS לפני הורדה | Curation | מוגדר לכל remote repo | כן (מנהל) |
| ניהול מודלי ML (Hugging Face, MLflow, NIM) | Artifactory ML repo | jf rt upload או FrogML SDK | כן |
| ניקוי artifacts ישנים | Artifactory | AQL + מחיקה או מדיניות שמירה | כן (מנהל) |

### שלב 2: הגדרת אימות

**אפשרות א: JFrog CLI (מומלץ):**
```bash
# Configure JFrog CLI with access token (recommended)
jf config add my-server \
  --url="https://mycompany.jfrog.io" \
  --access-token="YOUR_ACCESS_TOKEN" \
  --interactive=false

# Verify connection
jf rt ping
```

**אפשרות ב: REST API עם curl:**
```bash
# Using access token (recommended)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://mycompany.jfrog.io/artifactory/api/system/ping"

# Using identity token (reference token, also works as Bearer)
curl -H "Authorization: Bearer YOUR_REFERENCE_TOKEN" \
  "https://mycompany.jfrog.io/artifactory/api/system/ping"
```

> מפתחות API ישנים (header של `X-JFrog-Art-Api`) הגיעו לסוף חיים ברבעון הרביעי של 2024 ומכובים כברירת מחדל מ-Artifactory 7.98 ואילך. השתמשו ב-access tokens או reference tokens (שניהם נשלחים כ-`Authorization: Bearer`).

**אפשרות ג: OIDC ל-CI (בלי סודות ארוכי-טווח):**
```yaml
# דוגמת GitHub Actions עם jfrog/setup-jfrog-cli
- uses: jfrog/setup-jfrog-cli@v4
  with:
    oidc-provider-name: my-github-oidc-provider
  env:
    JF_URL: https://mycompany.jfrog.io
```
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
# Login to Artifactory Docker registry
docker login mycompany.jfrog.io

# Push image through Artifactory
docker tag myapp:latest mycompany.jfrog.io/docker-local/myapp:1.0.0
docker push mycompany.jfrog.io/docker-local/myapp:1.0.0

# Pull image through Artifactory (also caches remote images)
docker pull mycompany.jfrog.io/docker-remote/nginx:latest
```

**שימוש ב-JFrog CLI עבור Docker (מוסיף מידע build):**
```bash
# Push with build info collection
jf docker push mycompany.jfrog.io/docker-local/myapp:1.0.0 \
  --build-name=myapp-build --build-number=42

# Pull with build info collection
jf docker pull mycompany.jfrog.io/docker-remote/nginx:latest \
  --build-name=myapp-build --build-number=42
```

### שלב 4: מידע Build וקידום

**פרסום מידע build מצינור CI:**
```bash
# Collect environment variables
jf rt build-collect-env myapp-build 42

# Upload artifacts with build info
jf rt upload "target/*.jar" libs-release-local/com/mycompany/myapp/1.0.0/ \
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
jf docker scan mycompany.jfrog.io/docker-local/myapp:1.0.0

# Scan with fail threshold (for CI)
jf audit --fail --min-severity=High

# Generate SBOM in CycloneDX (with VEX data from Xray 3.67+)
jf scan --format=cyclonedx mycompany.jfrog.io/docker-local/myapp:1.0.0 > sbom.json

# Generate SBOM in SPDX (ISO/IEC standard, OSS-friendly)
jf scan --format=spdx mycompany.jfrog.io/docker-local/myapp:1.0.0 > sbom.spdx.json
```

מ-Xray 3.131 ואילך, ה-CycloneDX כולל גם CBOM (Cryptography Bill of Materials, ממצאי תעודות וסודות) כשמפעילים את JFrog Advanced Security עם סריקת secrets. Xray גם יודע לקלוט SBOM חיצוניים בפורמט SPDX או CycloneDX (כולל VEX לניתוח קונטקסטואלי) כדי לבדוק artifacts של ספקים.

**Frogbot לסריקת pull requests (חינם עם חשבון free-tier של JFrog):**
```yaml
# .github/workflows/frogbot-scan-pr.yml
- uses: jfrog/frogbot@v2
  env:
    JF_URL: ${{ secrets.JF_URL }}
    JF_ACCESS_TOKEN: ${{ secrets.JF_ACCESS_TOKEN }}
    JF_GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
הבוט Frogbot סורק PRs עם SCA, SAST ו-IaC, מגיב על ממצאים, ויודע לפתוח PRs לתיקונים. נקודת התחלה טובה לפרויקטי OSS ישראליים שעדיין לא משלמים ל-JFrog.

### שלב 5b: ניהול מודלי AI ו-ML (JFrog ML + AI Catalog)

הפלטפורמות JFrog ML (מרץ 2025, פרי רכישת Qwak) ו-AI Catalog (ספטמבר 2025) מרחיבים את Artifactory ו-Xray כך שיתמכו במודלי ML. סוג ה-repo החדש **Machine Learning** ב-Artifactory 7.111.1+ שומר מודלים של Hugging Face לצד PyTorch, ONNX, .pkl, .joblib, .pth ו-.cbm באותו repo פורמט-אגנוסטי, עם FrogML SDK ותמיכת Xet.

```bash
# יוצרים ML repo (דרך ממשק הניהול או REST):
# Administration > Repositories > Add Repository > Local > Machine Learning

# מעלים מודל עם build info
jf rt upload "model.onnx" ml-local/myapp/v1.0.0/ \
  --build-name=ml-build --build-number=42

# Xray סורק מודלים בדיוק כמו שסורק Docker images
jf docker scan mycompany.jfrog.io/ml-local/myapp:v1.0.0
```

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
- `scripts/artifactory_client.py`, לקוח מלא ל-REST API של JFrog Artifactory התומך בבדיקות תקינות, רשימת/יצירת מאגרים, העלאת/הורדת/מחיקת artifacts, חיפוש AQL, ניהול properties, שליפת מידע build וקידום build. מאומת דרך access token (ארגומנט CLI או משתנה סביבה JFROG_ACCESS_TOKEN). הרצה: `python scripts/artifactory_client.py --help`
- `scripts/xray_client.py`, לקוח REST API של JFrog Xray לסריקת פגיעויות, ניהול מדיניות אבטחה ו-watches, חיפוש הפרות והפקת דוחות פגיעויות. השתמשו בו לסריקת artifacts עבור CVE, יצירת שערי אבטחה שחוסמים פגיעויות קריטיות, והפקת דוחות עמידה. הרצה: `python scripts/xray_client.py --help`

### חומרי עזר
- `references/api-reference.md`, מדריך מהיר לנקודות קצה של REST API ב-Artifactory וב-Xray מאורגנים לפי קטגוריה (מערכת, מאגרים, artifacts, חיפוש, properties, מידע build, סריקה, מדיניות, הפרות), דף פקודות JFrog CLI, תבניות שאילתות AQL, הסברי סוגי מאגרים ומוסכמות מבנה מאגר סטנדרטיות. עיינו בו בעת בניית קריאות API, כתיבת שאילתות AQL, או הגדרת מבני מאגרים.

## מלכודות נפוצות

- **JFrog Pipelines הגיע לסוף חיים ב-1 במאי 2026.** לקוחות חדשים כבר לא יכולים להקצות Pipelines, ולקוחות קיימים חייבים להיות אחרי ההגירה. JFrog ממליצים על GitHub Actions, GitLab CI, Jenkins או Azure DevOps עם `jfrog/setup-jfrog-cli`. אם צוות ישראלי עדיין על Pipelines, ההגירה כבר באיחור: אין יותר feature updates ואין תמיכה.
- **רפוזיטוריות Hugging Face הישנות מוצאות משימוש ביוני 2026.** סוג ה-repo המקורי של Artifactory בשם "Hugging Face" (מ-7.77.x) מאבד פונקציונליות מלאה ויש לעבור ל-layout החדש "Machine Learning" (הוצג ב-Artifactory 7.111.1). ההגירה היא חד-כיוונית בפועל (ה-API של `restore_layout` מוחק חבילות שנוספו אחרי השדרוג), repos של federation לא יכולים לערבב layouts, ומכסות ה-rate limit של Hugging Face Hub עולות בזמן ה-cache warming. צוותי ML ישראליים שמשתמשים ב-Artifactory כפרוקסי ל-Hugging Face צריכים למפות ולהגר, רצוי אחרי שדרוג ה-identity ב-Hub ל-Enterprise.
- **מפתחות API הגיעו לסוף חיים ברבעון הרביעי של 2024.** מפתחות ישנים עוד עובדים על מופעים ישנים, אבל אי אפשר ליצור חדשים. הגרו כל שימוש ב-`X-JFrog-Art-Api` ל-access tokens או reference tokens (שניהם נשלחים כ-`Authorization: Bearer ...`).
- **OIDC הוא היום שיטת האימות המומלצת של JFrog ל-GitHub Actions.** דורש JFrog CLI 2.75.0+ וה-workflow צריך `permissions: id-token: write`. טוקני access ארוכי טווח ב-GitHub secrets עדיין נתמכים, אבל לא מומלצים ל-pipelines חדשים.
- אזורי SaaS של JFrog הם רשימה קבועה (us-east, us-west, eu-frankfurt, eu-west, ap-southeast). לדרישות אחסון מידע בישראל, פריסות BYOL על AWS `il-central-1` הן אפשרות, אבל JFrog SaaS עצמו לא מארח בישראל. בדקו את אזור המופע ב-jfrog.com/help/r/jfrog-platform-administration-documentation/jfrog-saas-regions.
- **שקיפות תמחור משתנה לפי tier.** JFrog מפרסמים בפומבי Pro בערך 150 דולר לחודש ו-Enterprise X בערך 950 דולר לחודש ל-SaaS, כשה-Enterprise+ ב-quote. תמחור self-managed (סביב 27,000 דולר לשנה ל-Pro X ו-48,000 דולר לשנה ל-Enterprise X) כמעט אף פעם לא פומבי. קונים ישראלים צריכים לאמת את המחירים מול JFrog ישראל לפני התכנון.
- טוקני אימות JFrog CLI לפריסות ארגוניות ישראליות דורשים לעיתים קרובות אינטגרציית SSO עם Azure AD או Okta שמוגדרים לטננטים ישראליים. סוכנים עלולים ליצור קונפיגורציות basic auth שלא עובדות.
- צוותי פיתוח ישראליים עובדים במחזורי פריסה ראשון-חמישי. Pipelines של CI/CD שמוגדרים לשני-שישי עלולים לפספס את יום העבודה הראשון או לרוץ מיותר ביום שישי.
- סריקת אבטחה של JFrog Xray עלולה לסמן תלויות שעומדות ברגולציה הישראלית אך מסומנות על ידי בקרות יצוא אמריקאיות. צוותים ישראליים צריכים לבדוק התראות Xray בהקשר הרגולטורי המקומי.

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| תיעוד פלטפורמת JFrog | https://jfrog.com/help/r/jfrog-platform-administration-documentation | ניהול רפוזיטוריות, הרשאות, הגדרות HA |
| Artifactory REST API | https://jfrog.com/help/r/jfrog-rest-apis/artifactory-rest-apis | נקודות קצה, תחביר שאילתות, AQL |
| תיעוד Xray | https://jfrog.com/xray/ | סריקת פגיעויות, ציות רישוי, מדיניות, SBOM ו-VEX |
| JFrog CLI Releases | https://github.com/jfrog/jfrog-cli/releases | גרסה אחרונה של ה-CLI (2.103.0 נכון לאפריל 2026), changelog |
| JFrog Docker Registry | https://jfrog.com/help/r/jfrog-artifactory-documentation/docker-registry | ניהול אימג'י Docker, פרוקסי Docker Hub |
| JFrog ML | https://jfrog.com/jfrog-ml/ | פלטפורמת MLOps (מרכישת Qwak), model registry, FrogML SDK |
| JFrog AI Catalog | https://jfrog.com/press-room/jfrog-launches-ai-catalog-to-secure-and-govern-ai-model-delivery/ | Governance ל-OpenAI, Anthropic, NVIDIA NIM ו-Hugging Face |
| Machine Learning Repositories | https://jfrog.com/help/r/jfrog-artifactory-documentation/log-hugging-face-models | סוג ה-repo החדש, הגירת HF ביוני 2026 |
| JFrog Curation | https://jfrog.com/curation/ | סינון חבילות OSS, Compliant Version Selection, תווית MCP Servers |
| Frogbot | https://github.com/jfrog/frogbot | בוט סריקת PR חינמי, SCA + SAST + IaC |
| OIDC עם GitHub Actions | https://jfrog.com/help/r/jfrog-platform-administration-documentation/configure-jfrog-platform-oidc-integration-with-github-actions | האימות המומלץ ל-CI, דורש CLI 2.75.0+ |
| Pipelines End of Life | https://jfrog.com/help/r/jfrog-release-information/pipelines-end-of-life | EOL ב-1 במאי 2026, הנחיות הגירה |

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
