# WhatsApp Business API Setup Guide for Israeli Businesses

## Overview

This guide covers setting up the WhatsApp Business Cloud API for Israeli businesses. The Cloud API is Meta's hosted solution (no need for on-premise servers), and is the recommended approach for new integrations.

## Prerequisites

1. **Meta Business Account** (business.facebook.com)
2. **Israeli phone number** (+972) that can receive SMS or voice calls for verification
3. **Business verification** on Meta Business Suite (requires Israeli business registration documents)
4. **SSL-enabled webhook endpoint** (HTTPS required)

## Step-by-Step Setup

### 1. Create Meta Business Account

1. Go to business.facebook.com
2. Create an account using your Israeli business details
3. Complete business verification:
   - Upload Israeli business registration certificate (תעודת רישום עסק)
   - Provide business address in Israel
   - Submit utility bill or bank statement as address proof
   - Verification typically takes 2-5 business days

### 2. Set Up WhatsApp Business

1. Go to Meta Developers (developers.facebook.com)
2. Create a new app (type: "Business")
3. Add the "WhatsApp" product to your app
4. In WhatsApp settings, link your Meta Business Account

### 3. Phone Number Registration

Register your Israeli phone number:

1. Navigate to WhatsApp > Getting Started in your app dashboard
2. Click "Add phone number"
3. Enter your Israeli number in E.164 format: `+972XXXXXXXXX`
4. Choose verification method (SMS or voice call)
5. Enter the verification code

**Notes for Israeli numbers:**
- Mobile numbers: `+9725XXXXXXXX` (10 digits after country code)
- Landline numbers are supported but mobile is recommended
- The number must not be currently registered on WhatsApp or WhatsApp Business app

### 4. Generate Access Token

For development:
1. Go to WhatsApp > Getting Started
2. Copy the temporary access token (valid 24 hours)

For production:
1. Go to App Settings > Basic
2. Note your App ID and App Secret
3. Create a System User in Business Settings
4. Generate a permanent token for the System User with `whatsapp_business_messaging` permission

### 5. Set Up Webhook

Configure your webhook endpoint to receive incoming messages:

1. Go to WhatsApp > Configuration
2. Enter your webhook URL: `https://your-domain.com/webhook`
3. Enter your verify token (a secret string you choose)
4. Subscribe to these webhook fields:
   - `messages` (incoming messages)
   - `message_status` (delivery/read receipts)

**Webhook requirements:**
- Must be HTTPS (SSL certificate required)
- Must respond to GET verification requests
- Must respond with HTTP 200 within 5 seconds
- Must verify the X-Hub-Signature-256 header

### 6. Create Message Templates (Hebrew)

WhatsApp requires pre-approved templates for initiating conversations. Submit Hebrew templates via Meta Business Suite:

1. Go to WhatsApp > Message Templates
2. Click "Create Template"
3. Select language: Hebrew (he)
4. Choose category: Marketing, Utility, or Authentication

#### Template Examples for Israeli Businesses

**Order Confirmation (Utility):**
```
Template name: order_confirmation_he
Language: he
Category: Utility
Header: None
Body: שלום {{1}}, ההזמנה שלך מספר {{2}} התקבלה בהצלחה. סכום: ₪{{3}}. צפי למשלוח: {{4}}.
Footer: תודה שקנית אצלנו!
Buttons: [Quick Reply: "בדוק סטטוס"]
```

**Appointment Reminder (Utility):**
```
Template name: appointment_reminder_he
Language: he
Category: Utility
Body: שלום {{1}}, תזכורת לתור שלך ב-{{2}} בתאריך {{3}} בשעה {{4}}. לאישור, לחץ/י על הכפתור למטה.
Buttons: [Quick Reply: "מאשר/ת"] [Quick Reply: "רוצה לשנות"]
```

**Shipping Update (Utility):**
```
Template name: shipping_update_he
Language: he
Category: Utility
Body: הזמנה {{1}} נשלחה! מספר מעקב: {{2}}. צפי הגעה: {{3}}. לעקוב אחר המשלוח:
Buttons: [URL: "מעקב משלוח" -> https://tracking.example.com/{{1}}]
```

**Template Review Notes:**
- Hebrew templates typically take 1-3 business days to review
- Templates must not contain promotional content in the Utility category
- Variables ({{1}}, {{2}}) must not be used for the entire message body
- Footer is optional and limited to 60 characters
- Maximum 3 buttons per template

## API Reference

### Sending Messages

**Base URL:** `https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages`

**Authentication:** Bearer token in Authorization header

### Send Text Message

```bash
curl -X POST "https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "972501234567",
    "type": "text",
    "text": {"body": "שלום! איך אפשר לעזור?"}
  }'
```

### Send Template Message

```bash
curl -X POST "https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "972501234567",
    "type": "template",
    "template": {
      "name": "order_confirmation_he",
      "language": {"code": "he"},
      "components": [{
        "type": "body",
        "parameters": [
          {"type": "text", "text": "ישראל ישראלי"},
          {"type": "text", "text": "12345"},
          {"type": "text", "text": "299.90"},
          {"type": "text", "text": "יום רביעי, 15/03"}
        ]
      }]
    }
  }'
```

### Send Interactive Buttons

```bash
curl -X POST "https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "972501234567",
    "type": "interactive",
    "interactive": {
      "type": "button",
      "body": {"text": "איך אפשר לעזור?"},
      "action": {
        "buttons": [
          {"type": "reply", "reply": {"id": "order", "title": "בדיקת הזמנה"}},
          {"type": "reply", "reply": {"id": "support", "title": "תמיכה"}},
          {"type": "reply", "reply": {"id": "hours", "title": "שעות פעילות"}}
        ]
      }
    }
  }'
```

### Send Interactive List

```bash
curl -X POST "https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "972501234567",
    "type": "interactive",
    "interactive": {
      "type": "list",
      "body": {"text": "בחר/י נושא:"},
      "action": {
        "button": "לרשימת האפשרויות",
        "sections": [{
          "title": "שירותים",
          "rows": [
            {"id": "pricing", "title": "מחירון", "description": "צפייה במחירים"},
            {"id": "branches", "title": "סניפים", "description": "מציאת סניף"}
          ]
        }]
      }
    }
  }'
```

## Rate Limits and Pricing

### Message Limits

New WhatsApp Business accounts start with limited messaging:

| Tier | Messages per 24h | How to Reach |
|------|-------------------|--------------|
| Tier 1 | 1,000 | Verified business |
| Tier 2 | 10,000 | After sending 2x Tier 1 limit |
| Tier 3 | 100,000 | After sending 2x Tier 2 limit |
| Tier 4 | Unlimited | After sending 2x Tier 3 limit |

### Pricing (Israel)

WhatsApp uses conversation-based pricing. Each 24-hour conversation window has a cost:

| Conversation Type | Description | Approximate Cost (USD) |
|-------------------|-------------|----------------------|
| Utility | Transaction updates, confirmations | ~$0.02 |
| Authentication | OTP, login codes | ~$0.02 |
| Marketing | Promotional messages | ~$0.05 |
| Service | User-initiated conversations | Free (first 1000/month) |

Prices vary by region and are subject to change. Check Meta's pricing page for current rates.

## Best Practices for Israeli WhatsApp Bots

1. **Respect Shabbat.** Avoid sending marketing messages from Friday sunset to Saturday nightfall. Utility messages (order updates) are generally acceptable.

2. **Use Hebrew templates wisely.** Hebrew text in templates renders well on all devices. Test on both iOS and Android.

3. **Keep button text short.** WhatsApp button titles are limited to 20 characters. Hebrew can be more compact than English, so plan accordingly.

4. **Handle billing in NIS.** When displaying prices, use the ₪ symbol and Israeli number formatting (1,000.00).

5. **Support both Hebrew and English.** Many Israeli users are bilingual. Offer a language toggle early in the conversation.

6. **Comply with Israeli privacy laws.** The Israeli Privacy Protection Law (1981) and its regulations apply to WhatsApp communications. Ensure proper consent for marketing messages.

7. **Use interactive messages.** Israeli users engage more with buttons and lists than free-text input. Use interactive messages wherever possible.

8. **Business hours awareness.** Israeli business hours are Sunday through Thursday. Configure your bot to acknowledge off-hours messages and set expectations for response times.

## Common Issues and Solutions

### Phone Number Verification Failed
- Ensure the number is not registered on WhatsApp personal or WhatsApp Business app
- Try voice call verification instead of SMS
- Israeli virtual numbers may not work; use a SIM-based number

### Template Rejected
- Ensure Hebrew text is grammatically correct
- Remove any promotional language from Utility templates
- Variables must have sample values during submission
- Resubmit with suggested changes from the rejection reason

### Messages Not Delivering
- Check the recipient's phone number format (must be E.164: 972XXXXXXXXX, no leading + in API)
- Verify the recipient has WhatsApp installed
- Check your messaging tier limits
- Ensure the 24-hour conversation window is active for non-template messages

### Webhook Not Receiving Messages
- Verify SSL certificate is valid and not self-signed
- Ensure webhook responds with HTTP 200 within 5 seconds
- Check that you've subscribed to the correct webhook fields
- Verify the X-Hub-Signature-256 validation is correct
