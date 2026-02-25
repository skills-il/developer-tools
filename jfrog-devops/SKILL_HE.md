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

# Using API key
curl -H "X-JFrog-Art-Api: YOUR_API_KEY" \
  "https://mycompany.jfrog.io/artifactory/api/system/ping"
```

**אפשרות ג: לקוח Python:**
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
```

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
תוצאה: הגדרת מאגר Docker וירטואלי, הגדרת docker login ב-CI, דחיפת images עם מידע build באמצעות jf docker push, סריקה עם Xray, קידום מ-staging לייצור.

### דוגמה 3: שער אבטחה
המשתמש אומר: "חסמו פריסת artifacts עם CVE קריטיים"
תוצאה: יצירת מדיניות אבטחה ב-Xray שחוסמת CVE קריטיים, יצירת watch על מאגרי ייצור, הגדרת פעולת fail_build לשילוב CI, הגדרת התראות על הפרות.

### דוגמה 4: ניקוי אחסון
המשתמש אומר: "נקו artifacts ישנים כדי לפנות מקום ב-Artifactory"
תוצאה: שימוש ב-AQL לאיתור artifacts שלא הורדו 90+ יום, זיהוי artifacts מסוג snapshot ישנים מ-30 יום, יצירת סקריפט ניקוי עם מצב dry-run, תזמון ניקוי קבוע.

## משאבים מצורפים

### סקריפטים
- `scripts/artifactory_client.py` — לקוח מלא ל-REST API של JFrog Artifactory התומך בבדיקות תקינות, רשימת/יצירת מאגרים, העלאת/הורדת/מחיקת artifacts, חיפוש AQL, ניהול properties, שליפת מידע build וקידום build. מאומת באמצעות access token (ארגומנט CLI או משתנה סביבה JFROG_ACCESS_TOKEN). הרצה: `python scripts/artifactory_client.py --help`
- `scripts/xray_client.py` — לקוח REST API של JFrog Xray לסריקת פגיעויות, ניהול מדיניות אבטחה ו-watches, חיפוש הפרות והפקת דוחות פגיעויות. השתמשו בו לסריקת artifacts עבור CVE, יצירת שערי אבטחה שחוסמים פגיעויות קריטיות, והפקת דוחות עמידה. הרצה: `python scripts/xray_client.py --help`

### חומרי עזר
- `references/api-reference.md` — מדריך מהיר לנקודות קצה של REST API ב-Artifactory וב-Xray מאורגנים לפי קטגוריה (מערכת, מאגרים, artifacts, חיפוש, properties, מידע build, סריקה, מדיניות, הפרות), דף פקודות JFrog CLI, תבניות שאילתות AQL, הסברי סוגי מאגרים ומוסכמות מבנה מאגר סטנדרטיות. עיינו בו בעת בניית קריאות API, כתיבת שאילתות AQL, או הגדרת מבני מאגרים.

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
