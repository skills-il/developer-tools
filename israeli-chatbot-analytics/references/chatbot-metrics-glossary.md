# Chatbot Analytics Metrics Glossary / מילון מונחי אנליטיקת צ'אטבוט

A comprehensive glossary of chatbot analytics metrics with Hebrew translations and industry benchmarks. Use this reference when defining KPIs, building dashboards, or explaining metrics to Hebrew-speaking stakeholders.

## Core Metrics / מדדים מרכזיים

### Resolution Rate / שיעור פתרון
**Definition:** Percentage of conversations where the chatbot successfully resolved the user's issue without human intervention.
**Hebrew:** אחוז השיחות שבהן הצ'אטבוט פתר את הבעיה של המשתמש בלי התערבות אנושית.
**Formula:** `resolved_conversations / total_conversations * 100`
**Benchmark:** Good > 70%, Average 50-70%, Needs improvement < 50%
**Also known as:** Containment rate, automation rate

### First Contact Resolution (FCR) / פתרון במגע ראשון
**Definition:** Percentage of issues resolved in a single conversation session, without the user returning for the same issue.
**Hebrew:** אחוז הבעיות שנפתרו בסשן שיחה אחד, בלי שהמשתמש חזר לאותה בעיה.
**Formula:** `single_session_resolutions / total_resolutions * 100`
**Benchmark:** Good > 65%, Average 45-65%, Needs improvement < 45%

### Escalation Rate / שיעור הסלמה
**Definition:** Percentage of conversations transferred to a human agent.
**Hebrew:** אחוז השיחות שהועברו לנציג אנושי.
**Formula:** `escalated_conversations / total_conversations * 100`
**Benchmark:** Good < 15%, Average 15-30%, Needs improvement > 30%

### Abandonment Rate / שיעור נטישה
**Definition:** Percentage of conversations where the user left before reaching a resolution or escalation.
**Hebrew:** אחוז השיחות שבהן המשתמש עזב לפני שהגיע לפתרון או הסלמה.
**Formula:** `abandoned_conversations / total_conversations * 100`
**Benchmark:** Good < 20%, Average 20-35%, Needs improvement > 35%

### Fallback Rate / שיעור Fallback
**Definition:** Percentage of user messages that the chatbot could not classify into a known intent.
**Hebrew:** אחוז ההודעות שהצ'אטבוט לא הצליח לסווג לכוונה מוכרת.
**Formula:** `fallback_messages / total_user_messages * 100`
**Benchmark:** Good < 10%, Average 10-20%, Needs improvement > 20%

## User Satisfaction Metrics / מדדי שביעות רצון

### CSAT (Customer Satisfaction Score) / ציון שביעות רצון לקוח
**Definition:** Average satisfaction rating from post-chat surveys, typically on a 1-5 scale.
**Hebrew:** ממוצע דירוגי שביעות רצון מסקרים אחרי שיחה, בדרך כלל בסקאלה 1-5.
**Formula:** `sum(ratings) / count(ratings)`
**Benchmark:** Good > 4.0, Average 3.0-4.0, Needs improvement < 3.0

### NPS (Net Promoter Score) / ציון NPS
**Definition:** Measures likelihood of recommending the chatbot. Scale 0-10. Promoters (9-10) minus Detractors (0-6).
**Hebrew:** מודד סבירות להמליץ על הצ'אטבוט. סקאלה 0-10. מקדמים (9-10) פחות מלעיזים (0-6).
**Formula:** `(promoters_pct - detractors_pct) * 100`
**Range:** -100 to +100
**Benchmark:** Good > 30, Average 0-30, Needs improvement < 0

### Thumbs Up Ratio / יחס אגודלים למעלה
**Definition:** Percentage of positive thumbs ratings out of all thumbs ratings.
**Hebrew:** אחוז דירוגי האגודל למעלה מתוך כל דירוגי האגודלים.
**Formula:** `thumbs_up / (thumbs_up + thumbs_down) * 100`
**Benchmark:** Good > 80%, Average 60-80%, Needs improvement < 60%

## Conversation Quality Metrics / מדדי איכות שיחה

### Average Session Length / אורך סשן ממוצע
**Definition:** Average number of messages per conversation session.
**Hebrew:** מספר הודעות ממוצע לכל סשן שיחה.
**Formula:** `sum(session_message_counts) / total_sessions`
**Benchmark:** 4-8 messages is ideal. Too short may mean unresolved issues; too long suggests confusion.

### Average Handle Time (AHT) / זמן טיפול ממוצע
**Definition:** Average duration of a conversation from start to end.
**Hebrew:** משך ממוצע של שיחה מתחילתה ועד סופה.
**Formula:** `sum(session_durations) / total_sessions`
**Benchmark:** Varies by domain. E-commerce: 2-5 min, Support: 5-10 min, Complex services: 10-20 min.

### Loop Rate / שיעור לולאות
**Definition:** Percentage of conversations where the bot repeated the same response 3+ times consecutively.
**Hebrew:** אחוז השיחות שבהן הבוט חזר על אותה תגובה 3 פעמים או יותר ברצף.
**Benchmark:** Good < 3%, Needs improvement > 5%

### Conversation Depth at Drop-off / עומק שיחה בנקודת נטישה
**Definition:** The message index at which users most commonly abandon conversations.
**Hebrew:** מיקום ההודעה שבו משתמשים נוטשים בתדירות הגבוהה ביותר.
**Usage:** Identify problematic bot prompts at common drop-off depths.

## Intent Accuracy Metrics / מדדי דיוק כוונות

### Intent Recognition Accuracy / דיוק זיהוי כוונות
**Definition:** Percentage of user messages where the detected intent matches the actual user intent.
**Hebrew:** אחוז ההודעות שבהן הכוונה שזוהתה תואמת את הכוונה האמיתית של המשתמש.
**Formula:** `correct_predictions / total_predictions * 100`
**Benchmark:** Good > 85%, Average 70-85%, Needs improvement < 70%
**Note:** Requires ground truth labels from manual annotation.

### Confidence Distribution / התפלגות רמת ביטחון
**Definition:** Distribution of confidence scores across intent predictions.
**Hebrew:** התפלגות ציוני ביטחון בתחזיות כוונה.
**Usage:** Look for bimodal distributions (many high + many low) as a sign that certain intents need more training data.

### Confusion Rate / שיעור בלבול
**Definition:** For a specific intent pair, the percentage of times intent A was classified as intent B.
**Hebrew:** עבור זוג כוונות ספציפי, אחוז הפעמים שכוונה A סווגה ככוונה B.
**Usage:** Identify intent pairs that need better differentiation.

## Performance Metrics / מדדי ביצועים

### Average Response Time / זמן תגובה ממוצע
**Definition:** Average time between receiving a user message and sending the bot response.
**Hebrew:** זמן ממוצע בין קבלת הודעת משתמש לשליחת תגובת הבוט.
**Benchmark:** Good < 1s, Average 1-3s, Needs improvement > 3s

### P95 Response Time / זמן תגובה P95
**Definition:** 95th percentile response time. 95% of responses are faster than this value.
**Hebrew:** זמן תגובה באחוזון ה-95. 95% מהתגובות מהירות יותר מערך זה.
**Benchmark:** Good < 2s, Average 2-5s, Needs improvement > 5s

### Uptime / זמן פעילות
**Definition:** Percentage of time the chatbot is available and responsive.
**Hebrew:** אחוז הזמן שהצ'אטבוט זמין ומגיב.
**Benchmark:** Target 99.9% or higher.

## Volume Metrics / מדדי נפח

### Conversations Per Day / שיחות ביום
**Definition:** Total number of conversation sessions initiated per day.
**Hebrew:** מספר סשני שיחה שנפתחו ביום.

### Peak Hour / שעת שיא
**Definition:** Hour of day with highest conversation volume.
**Hebrew:** שעה ביום עם נפח השיחות הגבוה ביותר.
**Israeli note:** Typical peaks at 10:00-12:00 and 19:00-22:00 Israel Time.

### Channel Distribution / התפלגות ערוצים
**Definition:** Breakdown of conversations by channel (WhatsApp, Telegram, web, app).
**Hebrew:** פילוח שיחות לפי ערוץ (וואטסאפ, טלגרם, אתר, אפליקציה).
**Israeli note:** WhatsApp dominates in Israel with over 90% smartphone penetration.

## A/B Testing Metrics / מדדי בדיקות A/B

### Statistical Significance / מובהקות סטטיסטית
**Definition:** Confidence level that observed differences between variants are not due to chance.
**Hebrew:** רמת ביטחון שההבדלים שנצפו בין הווריאנטים לא נובעים ממקריות.
**Standard:** p < 0.05 (95% confidence)
**Israeli note:** Hebrew chatbots often have smaller user bases. Plan for longer test durations (2+ weeks) and lower minimum detectable effects.

### Minimum Detectable Effect (MDE) / אפקט מינימלי ניתן לגילוי
**Definition:** Smallest difference between variants that the test can reliably detect.
**Hebrew:** ההבדל הקטן ביותר בין ווריאנטים שהבדיקה יכולה לזהות באופן אמין.
**Guideline:** For 200 impressions per variant, MDE is typically 10-15%.

## Sentiment Metrics / מדדי סנטימנט

### Sentiment Distribution / התפלגות סנטימנט
**Definition:** Breakdown of user messages by detected sentiment (positive, neutral, negative).
**Hebrew:** פילוח הודעות משתמשים לפי סנטימנט שזוהה (חיובי, ניטרלי, שלילי).

### Sentiment Trend / מגמת סנטימנט
**Definition:** Change in average sentiment score over time within a conversation or across conversations.
**Hebrew:** שינוי בציון סנטימנט ממוצע לאורך זמן בתוך שיחה או בין שיחות.
**Usage:** Declining sentiment within a conversation signals user frustration.

### Mixed Language Rate / שיעור שפה מעורבת
**Definition:** Percentage of messages containing both Hebrew and English text.
**Hebrew:** אחוז ההודעות שמכילות טקסט גם בעברית וגם באנגלית.
**Israeli note:** Typically 15-30% in Israeli tech-oriented chatbots.

## Benchmark Summary Table / טבלת סיכום בנצ'מרקים

| Metric / מדד | Good / טוב | Average / ממוצע | Needs Work / לשיפור |
|--------------|-----------|----------------|---------------------|
| Resolution Rate / פתרון | > 70% | 50-70% | < 50% |
| FCR / מגע ראשון | > 65% | 45-65% | < 45% |
| Escalation / הסלמה | < 15% | 15-30% | > 30% |
| Abandonment / נטישה | < 20% | 20-35% | > 35% |
| Fallback Rate | < 10% | 10-20% | > 20% |
| CSAT | > 4.0/5 | 3.0-4.0 | < 3.0 |
| Intent Accuracy / דיוק | > 85% | 70-85% | < 70% |
| Avg Response Time / תגובה | < 1s | 1-3s | > 3s |
| Session Length / אורך | 4-8 msgs | 8-15 msgs | > 15 msgs |
| Loop Rate / לולאות | < 3% | 3-5% | > 5% |
