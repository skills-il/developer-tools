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
tg.BiometricManager.init(() => {
  if (tg.BiometricManager.isBiometricAvailable) {
    tg.BiometricManager.authenticate({ reason: "אישור תשלום" }, (success) => {
      if (success) submitOrder();
    });
  }
});
```

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
    .sort(([a], [b]) => a.localeCompare(b))
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

