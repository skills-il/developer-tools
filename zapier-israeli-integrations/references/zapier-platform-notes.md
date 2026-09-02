# Zapier Platform Notes (2026)

Vendor-side facts about Zapier itself. These move faster than the Israeli content in
the skill; re-check plan names, limits and product names before quoting any of them.

## Plans and prices

Verified against `https://zapier.com/pricing` on 2026-09-02. The page renders **annual** pricing; a
monthly-billing figure is not published there, so do not quote one.

| | Free | Professional | Team | Enterprise |
|---|---|---|---|---|
| Price | 0 | from $19.99/mo (annual) | from $69/mo (annual) | Contact Sales |
| Tasks | 100/mo | tiered, entry tier 750 | tiered | custom |
| Zap steps | Two-step | Multi-step | Multi-step | Multi-step |
| Polling time | 15 min | faster tiers | faster tiers | faster tiers |
| Tables records | 2,500/account | 100,000/account | 500,000/account | Contact Sales |
| Tables fields | 100/table | 100/table | 100/table | 100/table |
| Forms pages | 10/account | 50/account | 150/account | Contact Sales |
| Managed access | (blank) | 100 users | 500 users | Contact Sales |
| Copilot (Beta) | daily message limit | Unlimited | Unlimited | Unlimited |

**There is no Starter plan.** It was discontinued on 2 April 2024 and Professional became the
lowest-cost paid plan. Higher task volumes are a tier choice *within* Professional, not a separate
plan. Older tutorials that price "Starter" are describing a plan that no longer exists.

## Tables and Forms

**Zapier Interfaces is now Zapier Forms**; `zapier.com/interfaces` redirects to `zapier.com/forms`, and older tutorials still say Interfaces. Both Tables and Forms are available on every plan including Free, but "available" is not "unmetered": on Free, Tables is capped at 2,500 records per account (100,000 on Professional, 500,000 on Team) with 100 fields per table, and Forms at 10 pages per account (50 Professional, 150 Team). The pricing table's `Managed access` row is blank on Free, 100 users on Professional and 500 on Team. An invoice log for a real business will outgrow the Free tier, so size it before you build on it.

**Zapier Tables** (replace Google Sheets for structured data):
- Native database within Zapier, no external app connection needed
- Supports field types: text, number, date, email, URL, dropdown, checkbox
- Built-in views, filters, and linked records
- Triggers available: "New Record" and "Updated Record" can start Zaps
- Better for: client databases, invoice logs, payment records, expense tracking

**When to use Tables vs Google Sheets:**

| Scenario | Use Zapier Tables | Use Google Sheets |
|----------|-------------------|-------------------|
| Simple payment log | Yes (faster, no auth) | Overkill |
| Shared with accountant | No (accountant needs Google access) | Yes |
| CRM-style client list | Yes (linked records, views) | Limited |
| Complex formulas/pivots | No | Yes |
| VAT period reporting | Either works | Yes if accountant reviews directly |

**Zapier Forms**, formerly Interfaces (custom forms and dashboards):
- Build client intake forms, payment request pages, and dashboards without code
- Forms submit directly to Zapier Tables or trigger Zaps
- Useful for: freelancer client onboarding forms, payment request links, service feedback forms



## AI features

**Zapier Copilot** (labeled Beta; on all plans, but Free has a daily message limit and paid plans are unlimited):
- AI assistant that helps build Zaps from natural language descriptions
- Describe your workflow in English or Hebrew: "When I receive a Cardcom payment, create a receipt in Morning and email it"
- Copilot suggests the trigger, actions, and field mappings
- Can troubleshoot failing Zaps and suggest fixes

**Zapier Agents** (autonomous AI agents):
- Create AI agents that work across 9,000+ apps autonomously
- Lives at `agents.zapier.com`. It was previously **Zapier Central**, so older tutorials and forum posts call it that. The rename is evidenced by redirects (`zapier.com/central` now lands on `zapier.com/agents`, and `central.zapier.com` on `agents.zapier.com`), not by a Zapier announcement we could locate, so do not cite a Zapier statement for it
- Example: "Monitor my Morning account for unpaid invoices older than 30 days and send reminder emails in Hebrew"
- Agents can make decisions based on context without predefined Zap steps
- Agents burn a separate **activity** allowance, not your Zap task quota. Each agent run has a built-in activity cap (10 on Free, 40 on paid), so a chatty agent depletes the monthly activity quota faster than people expect

**Zapier Chatbots:**
- Build customer-facing chatbots that connect to your Zaps
- Usable for Hebrew customer support
- Can answer questions about orders, payments, and services by querying your Zapier Tables
- The underlying model changes as Zapier migrates providers, so do not hardcode a model name into your process docs

**Zapier MCP Server:**
- Connects AI coding tools (Claude Code, ChatGPT, Cursor) to 30,000+ actions across 9,000+ apps
- Agents can invoke Zapier actions directly from the development environment
- Useful for building and testing Israeli business automations programmatically

**AI Guardrails:**
- PII detection to prevent sensitive data (Israeli ID numbers, credit card details) from leaking
- Toxic language filtering
- Prompt injection prevention for chatbot-based flows



## WhatsApp: the two Zapier apps, and the BSP options

Zapier has **two different WhatsApp apps** and they are routinely confused. Pick by who you are messaging.

| Zapier app | Who it can message | What it does |
|------------|--------------------|--------------|
| **WhatsApp Notifications** | **Only yourself.** Zapier's help page states you use it "to send yourself WhatsApp messages to your WhatsApp account", and setup authenticates by confirming your own number with an OTP | Exactly one action and zero triggers: `Send Message`. Limited to seven prefilled templates (New Lead, New Message, Payment Confirmation, New Order, Shipping Confirmation, Calendar Reminder, Zap Error), 1024-character cap, and "custom templates cannot be created". Good for "alert me when a payment lands". Not usable for customers. |
| **WhatsApp Business** | **Your customers** | Triggers `New Message Received` (a customer messages your WhatsApp Business number) and `Message Status Updated` (sent, delivered, read, failed). Actions `Send Template Message`, `Send Freeform Message`, `Send Media Message`, `Get Attachment`. |

**Use WhatsApp Business for customer-facing Hebrew messaging.** It requires a WhatsApp Business account connected to Zapier, and the usual Meta rules apply:
- Outside the 24-hour customer-service window you must use a Meta-approved template. Templates are submitted for approval in advance; Meta's own template documentation says review can take up to 24 hours. Hebrew templates are supported but must be submitted with the Hebrew text.
- Example approved template: "שלום {{1}}, קיבלנו את התשלום שלך בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
- **Inside** the 24-hour window, opened when the customer messages you first, `Send Freeform Message` sends arbitrary Hebrew text with no template. This is the path for live support replies and follow-up questions.
- A payment confirmation sent proactively is outside the window, so it needs a template. A reply to a customer who just asked "did my payment go through?" does not.

**Israeli alternative:** InforUMobile's native Zapier app carries a `Send Whatsapp Template Message` action. If you already use InforUMobile for SMS, this avoids adding a second vendor.

**BSP providers**, worth adding only if you need high volume, a shared team inbox, or multi-channel routing that the native app does not cover:

| Provider | Zapier Integration | Hebrew Support | Approval Required |
|----------|-------------------|----------------|-------------------|
| Twilio WhatsApp Business API | Native Zapier app ("Twilio") | Yes, via pre-approved templates | Meta Business verification + template approval |
| WATI | Native Zapier app ("WATI") | Yes, via pre-approved templates | Meta Business verification + template approval |
| Respond.io | Native Zapier app (search "Respond.io", app slug `respondio`) | Yes | Meta Business verification |



## Zapier versus Make.com and n8n

| Factor | Zapier | Make.com (Integromat) | n8n |
|--------|--------|----------------------|-----|
| Ease of use | Simplest, visual builder + Copilot AI | Visual, slightly steeper learning curve | Requires self-hosting or cloud plan, most technical |
| Native integrations | 9,000+ apps | 3,000+ apps | 2,100+ integrations per n8n.io/integrations |
| Israeli app support | Native apps for SUMIT, Priority ERP, InforUMobile, Responder and Responder Live (רב מסר), Monday.com and Wix; webhook-based for Morning, Cardcom, Tranzila, iCount, EZcount, Rivhit and Grow | Webhook-based + some HTTP modules | Full HTTP/webhook flexibility |
| AI features | Copilot, Agents, Chatbots, MCP Server | AI modules available | AI nodes (self-configured) |
| Free tier | Unlimited 2-step Zaps, 100 tasks/month | 1,000 ops/month, limited scenarios | Self-host free, cloud plan has limits |
| Best for | Non-technical users, quick setup, AI-assisted building | Complex multi-branch workflows, cost-sensitive high-volume | Developers, self-hosted, full control |
| Israeli community | Large | Growing | Small but technical |

**Recommendation**: For non-technical Israeli business owners who want fast results, Zapier with Copilot AI is the easiest path. For complex workflows with high task volumes, Make.com may be more cost-effective. For developers who want full control and self-hosting, use n8n.


## וואטסאפ: שתי אפליקציות Zapier ואפשרויות ה-BSP (עברית)

ל-Zapier יש **שתי אפליקציות וואטסאפ שונות**, ומבלבלים ביניהן דרך קבע. בחרו לפי מי שאתם מתכוונים להודיע לו.

| אפליקציה ב-Zapier | למי אפשר לשלוח | מה היא עושה |
|-------------------|----------------|-------------|
| **WhatsApp Notifications** | **רק לעצמכם.** בדף העזרה של Zapier כתוב שמשתמשים בה "כדי לשלוח לעצמכם הודעות וואטסאפ לחשבון הוואטסאפ שלכם", וההתחברות מאמתת את המספר שלכם בקוד חד-פעמי | פעולה אחת בלבד ואפס טריגרים: `Send Message`. מוגבלת לשבע תבניות מוכנות מראש (New Lead, New Message, Payment Confirmation, New Order, Shipping Confirmation, Calendar Reminder, Zap Error), עד 1024 תווים, ו"אי אפשר ליצור תבניות מותאמות". מתאימה להתראות פנימיות. לא שימושית ללקוחות. |
| **WhatsApp Business** | **ללקוחות שלך** | טריגרים `New Message Received` (לקוח שולח הודעה למספר העסקי שלך) ו-`Message Status Updated` (נשלח, נמסר, נקרא, נכשל). פעולות `Send Template Message`, `Send Freeform Message`, `Send Media Message`, `Get Attachment`. |

**השתמשו ב-WhatsApp Business לתקשורת בעברית עם לקוחות.** נדרש חשבון WhatsApp Business מחובר ל-Zapier, וכללי Meta הרגילים חלים:
- מחוץ לחלון שירות הלקוחות של 24 שעות חובה להשתמש בתבנית מאושרת על ידי Meta. תבניות מוגשות לאישור מראש; לפי תיעוד התבניות של Meta הבדיקה יכולה לקחת עד 24 שעות. תבניות בעברית נתמכות אך צריך להגיש אותן עם הטקסט בעברית.
- דוגמה לתבנית מאושרת: "שלום {{1}}, קיבלנו את התשלום שלך בסך {{2}} ש\"ח. מספר אישור: {{3}}. תודה!"
- **בתוך** חלון 24 השעות, שנפתח כשהלקוח פונה אליכם ראשון, הפעולה `Send Freeform Message` שולחת טקסט חופשי בעברית ללא תבנית. זה המסלול לתשובות תמיכה ולשאלות המשך.
- אישור תשלום שנשלח ביוזמתכם הוא מחוץ לחלון ולכן דורש תבנית. תשובה ללקוח ששאל הרגע "התשלום עבר?" לא דורשת.

**חלופה ישראלית:** לאפליקציה המובנית של InforUMobile יש פעולת `Send Whatsapp Template Message`. אם אתם כבר משתמשים בה ל-SMS, זה חוסך ספק נוסף.

**ספקי BSP**, שכדאי להוסיף רק אם צריך נפח גבוה, תיבת דואר משותפת לצוות, או ניתוב רב-ערוצי שהאפליקציה המובנית לא מכסה:

| ספק | אינטגרציית Zapier | תמיכה בעברית | דרישת אישור |
|-----|-------------------|-------------|-------------|
| Twilio WhatsApp Business API | אפליקציה מובנית ("Twilio") | כן, דרך תבניות מאושרות | אימות Meta Business + אישור תבניות |
| WATI | אפליקציה מובנית ("WATI") | כן, דרך תבניות מאושרות | אימות Meta Business + אישור תבניות |
| Respond.io | אפליקציה מובנית (חפשו "Respond.io", מזהה `respondio`) | כן | אימות Meta Business |



## Tables ו-Forms (עברית)

**המוצר Zapier Interfaces נקרא היום Zapier Forms**; הכתובת `zapier.com/interfaces` מפנה ל-`zapier.com/forms`, ומדריכים ישנים עדיין אומרים Interfaces. Tables ו-Forms קיימים בכל מסלול כולל החינמי, אבל "קיים" זה לא "בלי מגבלה": בחינמי Tables מוגבל ל-2,500 רשומות לחשבון (100,000 ב-Professional, 500,000 ב-Team) עם 100 שדות לטבלה, ו-Forms ל-10 עמודים לחשבון (50 ב-Professional, 150 ב-Team). שורת `Managed access` בטבלת המחירים ריקה בחינמי, 100 משתמשים ב-Professional ו-500 ב-Team. יומן חשבוניות של עסק אמיתי יגלוש מהמסלול החינמי, אז העריכו את הנפח לפני שבונים על זה.

**Zapier Tables** (חלופה ל-Google Sheets לנתונים מובנים):
- בסיס נתונים מובנה בתוך Zapier, לא צריך חיבור לאפליקציה חיצונית
- תומך בסוגי שדות: טקסט, מספר, תאריך, אימייל, URL, רשימה נפתחת, תיבת סימון
- תצוגות, סינונים ורשומות מקושרות מובנים
- טריגרים זמינים: "רשומה חדשה" ו"רשומה עודכנה" יכולים להפעיל Zaps
- עדיף עבור: מאגרי לקוחות, יומני חשבוניות, רשומות תשלום, מעקב הוצאות

**מתי להשתמש ב-Tables מול Google Sheets:**

| תרחיש | Zapier Tables | Google Sheets |
|--------|---------------|---------------|
| יומן תשלומים פשוט | כן (מהיר יותר, ללא אימות) | מוגזם |
| שיתוף עם רואה חשבון | לא (רו"ח צריך גישת Google) | כן |
| רשימת לקוחות בסגנון CRM | כן (רשומות מקושרות, תצוגות) | מוגבל |
| נוסחאות מורכבות/טבלאות ציר | לא | כן |
| דוח תקופת מע"מ | שניהם עובדים | כן אם רו"ח צריך גישה ישירה |

**Zapier Forms**, שנקרא בעבר Interfaces (טפסים ודשבורדים ללא קוד):
- בנה טפסי קליטת לקוח, דפי בקשת תשלום ודשבורדים ללא כתיבת קוד
- טפסים מזינים ישירות ל-Zapier Tables או מפעילים Zaps
- שימושי עבור: טופס קליטת לקוח חדש לפרילנסרים, קישורי בקשת תשלום, טפסי משוב שירות



## יכולות AI (עברית)

**Zapier Copilot** (מסומן Beta; קיים בכל המסלולים, אבל בחינמי יש מגבלת הודעות יומית ובמסלולים בתשלום הוא ללא הגבלה):
- עוזר AI שבונה Zaps מתיאור בשפה חופשית
- תאר את התהליך שלך בעברית או אנגלית: "כשאני מקבל תשלום בקארדקום, צור קבלה ב-Morning ושלח אותה במייל"
- Copilot מציע טריגר, פעולות ומיפויי שדות
- יכול לפתור בעיות ב-Zaps כושלים ולהציע תיקונים

**Zapier Agents** (סוכני AI אוטונומיים):
- יצירת סוכני AI שעובדים מול יותר מ-9,000 אפליקציות באופן עצמאי
- המוצר יושב ב-`agents.zapier.com`. קודם הוא נקרא Zapier Central, ולכן מדריכים ופוסטים ישנים קוראים לו כך. השינוי מוכח מהפניות (`zapier.com/central` מוביל היום ל-`zapier.com/agents`, ו-`central.zapier.com` ל-`agents.zapier.com`) ולא מהודעה רשמית שמצאנו, אז אל תצטטו הצהרה של Zapier בעניין
- דוגמה: "עקוב אחרי חשבון ה-Morning שלי עבור חשבוניות שלא שולמו יותר מ-30 יום ושלח תזכורות במייל בעברית"
- סוכנים יכולים לקבל החלטות לפי הקשר בלי שלבי Zap מוגדרים מראש
- סוכנים צורכים מכסת **activity** נפרדת ולא את מכסת המשימות של ה-Zaps. לכל ריצת סוכן יש תקרת activity מובנית (10 בחינמי, 40 בתשלום), ולכן סוכן פעיל שוחק את המכסה החודשית מהר משמצפים

**Zapier Chatbots:**
- בניית צ'אטבוטים ללקוחות שמחוברים ל-Zaps שלך
- שימושי לשירות לקוחות בעברית
- יכולים לענות על שאלות לגבי הזמנות, תשלומים ושירותים על ידי שאילתות ב-Zapier Tables
- המודל שמאחורי המוצר מתחלף כש-Zapier מעבירה ספקים, ולכן אין לקבע שם מודל במסמכי התהליך שלכם

**Zapier MCP Server:**
- מחבר כלי קידוד עם AI (Claude Code, ChatGPT, Cursor) ליותר מ-30,000 פעולות ביותר מ-9,000 אפליקציות
- סוכנים יכולים להפעיל פעולות Zapier ישירות מסביבת הפיתוח
- שימושי לבנייה ובדיקה תכנותית של אוטומציות עסקיות ישראליות

**AI Guardrails:**
- זיהוי מידע אישי רגיש (מספרי ת.ז., פרטי כרטיס אשראי) למניעת דליפות
- סינון שפה פוגענית
- הגנה מפני prompt injection בתהליכים מבוססי צ'אטבוט



## Zapier מול Make.com ו-n8n (עברית)

| גורם | Zapier | Make.com (Integromat) | n8n |
|-------|--------|----------------------|-----|
| קלות שימוש | הכי פשוט, בונה ויזואלי + Copilot AI | ויזואלי, עקומת למידה קצת יותר תלולה | דורש אירוח עצמי או תוכנית ענן, הכי טכני |
| אינטגרציות מובנות | 9,000+ אפליקציות | 3,000+ אפליקציות | 2,100+ אינטגרציות לפי n8n.io/integrations |
| תמיכה באפליקציות ישראליות | אפליקציות מובנות ל-SUMIT, Priority ERP, InforUMobile, Responder ו-Responder Live (רב מסר), Monday.com ו-Wix; מבוסס webhook ל-Morning, קארדקום, טרנזילה, iCount, EZcount, ריווחית ו-Grow | מבוסס webhook + מודולי HTTP | גמישות מלאה ב-HTTP/webhook |
| יכולות AI | Copilot, Agents, Chatbots, MCP Server | מודולי AI זמינים | nodes של AI (הגדרה עצמית) |
| מסלול חינמי | Zaps ללא הגבלה בשני שלבים, 100 משימות/חודש | 1,000 פעולות/חודש, תרחישים מוגבלים | אירוח עצמי חינם, תוכנית ענן מוגבלת |
| מתאים ל | משתמשים לא-טכניים, הקמה מהירה, בנייה בעזרת AI | תהליכים מורכבים רב-ענפיים, רגישות לעלויות בנפחים גבוהים | מפתחים, אירוח עצמי, שליטה מלאה |
| קהילה ישראלית | גדולה | בצמיחה | קטנה אך טכנית |

**המלצה**: לבעלי עסקים ישראליים לא-טכניים שרוצים תוצאות מהירות, Zapier עם Copilot AI היא הדרך הקלה ביותר. לתהליכים מורכבים עם נפחי משימות גבוהים, Make.com עשוי להיות חסכוני יותר. למפתחים שרוצים שליטה מלאה ואירוח עצמי, n8n.
