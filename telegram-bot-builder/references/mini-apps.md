# Mini Apps: 2.0 feature surface and initData validation

### Mini Apps 2.0 Features

Bot API 7.x and 8.x added a set of "Mini Apps 2.0" capabilities exposed through `window.Telegram.WebApp`. All of them require the latest Telegram clients and are no-ops on older ones, so feature-detect before calling.

**Cloud storage** (`window.Telegram.WebApp.CloudStorage`) - per-user key-value storage that survives between sessions and devices. Up to 1024 keys per user, 4096 characters per value. No backend needed for lightweight preferences:

```javascript
const tg = window.Telegram.WebApp;
tg.CloudStorage.setItem("last_order_id", "12345");
tg.CloudStorage.getItem("last_order_id", (err, value) => {
  console.log("Restored:", value);
});
```

**Biometric authentication** (`window.Telegram.WebApp.BiometricManager`) - prompt the user for Face ID / Touch ID / fingerprint to gate sensitive actions inside the Mini App. Useful for confirming high-value Stars purchases or releasing saved payment tokens:

```javascript
// Call from a click handler (for example the "confirm payment" button).
function confirmWithBiometrics() {
  const bm = tg.BiometricManager;
  // BiometricManager needs Bot API 7.2+. On older clients init() returns without
  // ever calling its callback, so check the version first.
  if (!tg.isVersionAtLeast("7.2")) return fallbackConfirm();

  const run = () => {
    if (!bm.isBiometricAvailable) return fallbackConfirm();
    if (bm.isAccessGranted) {
      return bm.authenticate({ reason: "אישור תשלום" }, (ok) => (ok ? submitOrder() : fallbackConfirm()));
    }
    // Asked before and refused: offer the bot's biometric settings instead.
    // openSettings() is meant for users "who haven't granted it yet" and, per the
    // docs, "can be called only in response to user interaction".
    if (bm.isAccessRequested) return offerSettingsOrFallback(() => bm.openSettings());
    bm.requestAccess({ reason: "אישור תשלומים בטביעת אצבע או בזיהוי פנים" }, (granted) =>
      granted ? run() : fallbackConfirm(),
    );
  };

  // init() is a no-op once initialised and then never calls the callback again,
  // so a second tap would do nothing without this check.
  bm.isInited ? run() : bm.init(run);
}
```

`authenticate()` **throws** (`WebAppBiometricManagerBiometricAccessNotGranted`) when access was never granted, so the order above is not optional. Always keep a non-biometric path (`fallbackConfirm`): a user who declines, or a device without biometrics, must still be able to pay. Both `reason` strings are capped at 128 characters. **Biometrics is client-side UX only and proves nothing to your server**: it never replaces `initData` validation or Stars payment checks.

**Location service** (`window.Telegram.WebApp.LocationManager`) - request the user's GPS coordinates with explicit permission. Good for "find my nearest branch" flows in Israeli retail bots.

**Fullscreen mode** - `tg.requestFullscreen()` expands the Mini App to fill the device screen on mobile. Pair with `tg.exitFullscreen()` when you're done.

**Home-screen install** - `tg.addToHomeScreen()` lets the user add the Mini App as a launcher icon on Android (currently iOS shows a manual instructions sheet). Works once `tg.checkHomeScreenStatus()` reports the app is eligible.

**Reference:** [Telegram Mini Apps](https://core.telegram.org/bots/webapps)

### Mini App Validation

Always validate the `initData` on your server to ensure the request is genuinely from Telegram:

```typescript
import crypto from "crypto";

const MAX_AGE_SECONDS = 300;

function validateInitData(initData: string, botToken: string): boolean {
  const params = new URLSearchParams(initData);
  const hash = params.get("hash");
  if (!hash) return false;
  params.delete("hash");

  // Without this check a captured initData string authenticates forever.
  // The docs: "To prevent the use of outdated data, you can additionally
  // check the auth_date field".
  const authDate = Number(params.get("auth_date"));
  if (!authDate || Date.now() / 1000 - authDate > MAX_AGE_SECONDS) return false;

  // Sort params alphabetically
  const dataCheckString = Array.from(params.entries())
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)) // code-point order, not locale
    .map(([key, value]) => `${key}=${value}`)
    .join("\n");

  const secretKey = crypto
    .createHmac("sha256", "WebAppData")
    .update(botToken)
    .digest();

  const calculatedHash = crypto
    .createHmac("sha256", secretKey)
    .update(dataCheckString)
    .digest("hex");

  // Constant-time compare, a plain === leaks timing information.
  const a = Buffer.from(calculatedHash, "hex");
  const b = Buffer.from(hash, "hex");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
```



## Persistent menu button (setChatMenuButton)

**Using MenuButton (persistent button next to text input):**

```typescript
await bot.api.setChatMenuButton({
  chat_id: ctx.chat.id,
  menu_button: {
    type: "web_app",
    text: "פתח",
    web_app: { url: "https://your-app.com/mini-app" },
  },
});
```



## The sendData path in full

| Launch path | How data comes back |
|---|---|
| Reply-keyboard `web_app` button | `sendData()` -> `message:web_app_data` service message (no server needed) |
| Inline-keyboard button, menu button, direct link, inline mode | POST to your own backend with `initData`, validated server-side (below) |

For the `sendData` path the button must be a reply keyboard, not an inline one:

```typescript
import { Keyboard } from "grammy";

const kb = new Keyboard()
  .webApp("פתח אפליקציה", "https://your-app.com/mini-app")
  .resized();
await ctx.reply("לחצו לפתיחה:", { reply_markup: kb });
```

**In the Mini App (browser-side JavaScript):**

```javascript
// Telegram WebApp SDK is injected by Telegram
const tg = window.Telegram.WebApp;

// Send data back to the bot (closes the Mini App)
tg.sendData(JSON.stringify({
  action: "order",
  items: ["item1", "item2"],
  total: 150,
}));

// Or use MainButton for a cleaner UX
tg.MainButton.setText("אישור הזמנה"); // setText(), not MainButton.text =, which never reaches the client
tg.MainButton.show();
tg.MainButton.onClick(() => {
  tg.sendData(JSON.stringify({ confirmed: true }));
});
```

**In the bot (receiving the data):**

```typescript
bot.on("message:web_app_data", async (ctx) => {
  const data = JSON.parse(ctx.message.web_app_data.data);
  console.log("Received from Mini App:", data);

  // data comes from the user's client: recompute the price from item ids on the
  // server, never charge or confirm the client-sent total
  await ctx.reply(`הזמנה התקבלה! סה"כ: ₪${priceFromItems(data.items)}`);
});
```
