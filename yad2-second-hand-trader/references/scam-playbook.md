# Yad2 Scam Playbook (Israel, 2026)

The Israeli second-hand market on Yad2 is targeted by a small set of repeatable scams. Some attack the SELLER (the person who posted an item) and some attack the BUYER. Sources: Israeli Internet Association (block.org.il), Yad2 official safety guidance, payment-app terms.

## Seller-side: the signature "pay the courier first" scam

Step by step:

1. A "buyer" contacts the seller, eager, often willing to pay full price or extra. They often claim to be far away (Eilat, abroad) and offer to pay for shipping. Hebrew is sometimes poor or error-filled.
2. The buyer says they cannot come in person and will arrange a courier (usually GLS) to collect the item.
3. The buyer sends a screenshot of a bank transfer "already done" so the seller relaxes. Dedicated apps generate fake confirmations.
4. The buyer (or a fake courier email) then tells the seller they must pay the shipping company first, via a link, to release the transfer / receive the credit.
5. The link is a phishing page that captures the seller's credit-card details, or the payment goes to the scammer. Sometimes the demand is in Bitcoin.

**Verbatim source descriptions:**
- "שולח 'הרוכש' צילום של העברה בנקאית מזויפת. המוכר חש שהעסקה כשרה"
- "ה'רוכש' מבקש מהמוכר לשלם ישירות לחברת השילוח (GLS, בד\"כ)"
- "הלינק משמש לצורך הכנסת פרטי כרטיס אשראי אליו יתקבל, לכאורה, הזיכוי"
- "בקשת התשלום היא, לרוב, באמצעות ביטקוין"

**The tell:** a courier never needs the SELLER to pay anything in order to send money TO the seller. Any "pay to receive your money" flow is fraud.

**Overpayment variant:** "I paid too much by mistake, refund me the difference." The original payment is fake or will be reversed; only the refund is real money out.

## Buyer-side: the deposit / fake-listing scam

The dominant fraud against buyers:

1. A "seller" posts a fake listing for a sought-after item (PS5, concert tickets, a puppy, even an apartment) at an attractive price.
2. They create urgency ("lots of interest, I can hold it for you").
3. They ask for a deposit / holding fee (מקדמה / דמי רצינות) before the buyer sees the item.
4. Once paid, the seller vanishes; the item never existed.

Other buyer-side flags:
- Price far below market for the model/condition (bait).
- Photos look like stock or stolen images (run a reverse-image search).
- Seller refuses to meet in person or give a real pickup address.
- Suspiciously cheap phone/laptop/e-bike with no proof of origin: possible stolen goods (buying stolen property can mean it is seized and you lose the money). Ask for the box, receipt, or serial.
- For phones: not allowing an on-the-spot check. Before paying, power on, insert a SIM, and confirm it is not iCloud/Google activation-locked or reported lost/stolen.

## Payment rails (why finality matters)

The whole scam economy hinges on payment reversibility.

- **Cash:** instant, final, safest.
- **Bit:** a transfer cannot be cancelled once sent. "לא ניתן לבטל את ההעברה." Good to RECEIVE.
- **PayBox:** a payment can be undone only before the recipient confirms: "אם שילמתם למשתמש, תוכלו לבטל את התשלום רק בתנאי שהצד השני עוד לא אישר את קבלת התשלום." Good to RECEIVE once confirmed.
- **Bank transfer:** a "confirmation" shown at the meeting is NOT cleared money. Wait until it appears in your own balance.
- **Payment request (בקשת תשלום):** approving an incoming request sends YOUR money out. It is the opposite of being paid. Scammers disguise a request as "I'm paying, just approve."

Bit and PayBox now record the sender and recipient names in bank/credit statements, which adds traceability for a legitimate deal.

## Red-flag catalog (combined)

| Flag | Side | Verdict weight |
|------|------|----------------|
| Pay-courier-first + shipping | seller | High |
| Forged transfer screenshot | seller | High |
| Phishing payment/credit link | seller | High |
| Crypto / Bitcoin demand | either | High |
| Overpayment "refund the difference" | seller | High |
| Deposit / holding fee before viewing | buyer | High |
| Price far below market | buyer | Medium |
| Stock/stolen photos | buyer | Medium |
| Refuses to meet / give address | either | Medium |
| Too-cheap electronics, no proof of origin | buyer | Medium (stolen-goods risk) |
| Off-platform urgency, "abroad/soldier" | either | Medium |
| Payment request sent to you | either | High |

## The safe-deal checklist (give this to the user)

1. Meet in person, in a public place, in daylight. Bring someone for large or expensive items. Do not share your home address until committed.
2. Inspect the item against the listing before any money moves. "לוודא שהמוצר הוא אכן כפי שפורסם באתר, ללא שריטות או חבלות."
3. Pay/receive at handover only: cash, or Bit/PayBox you control. "מומלץ שהתשלום יתבצע במזומן, או דרך אפליקציות תשלומים מוכרות."
4. Never transfer money in advance, and never abroad on a future promise. "מומלץ מאוד שלא להעביר כסף מראש, ובטח לא לחו\"ל."
5. A transfer screenshot is not payment. Only your own bank balance proves money arrived.
6. Never click a payment/credit link a counterparty sends, and never enter card details to "receive" money.
7. Keep the conversation in Yad2's in-app chat (preserves evidence), and report a scammer's user/listing to Yad2 itself.

## If already scammed

1. Stop all contact and payment immediately.
2. Keep every screenshot and the listing URL.
3. Report the user/listing to Yad2.
4. If card details were entered anywhere, call your credit-card company / bank now to block the card.
5. File an online complaint with Israel Police.
6. Report phishing links to the National Cyber Directorate (gov.il cyber-event-report).

## Legal reality (state it plainly)

A private Yad2 sale between two individuals is NOT a consumer transaction under the Consumer Protection Law. The law's cancellation/cooling-off right applies to buying from a business (עוסק): "תקנות הגנת הצרכן מאפשרות לצרכן לבטל עסקה צרכנית שנעשתה בבית העסק." So there is no statutory 14-day return on a private deal.

But "no Consumer Protection Law" is not "no recourse." A seller must still disclose known defects ("כל מוכר חייב להודיע לצרכן על פגמים ידועים במוצר"), and a buyer who was deceived or sold an item with an undisclosed hidden defect (מום נסתר) can pursue remedies under general contract law and the Sales Law (חוק המכר), typically in small claims court. Inspect-before-paying is still far easier than suing.
