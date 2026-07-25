# Domain Checklist: Telegram Bot Builder

Coverage contract for this skill. Every "Must cover" item is knowledge whose absence
causes an agent to emit broken, insecure, or silently-non-working bot code.
Verified against the live docs on 2026-07-25 (Bot API 10.2, released 2026-07-14).

---

## Must cover (core)

### Platform fundamentals

1. **BotFather is the only way to create a bot; token format `{bot_id}:{secret}`.**
   Cited by: core.telegram.org/bots/api "Authorizing your bot" ("Each bot is given a
   unique authentication token when it is created... `123456:ABC-DEF...`").
   Token must never be committed; `/token` in BotFather rotates it.

2. **Request shape: `https://api.telegram.org/bot<token>/METHOD_NAME`, methods are
   case-insensitive, all queries UTF-8, response is `{ok, result|description, error_code}`.**
   Cited by: bots/api "Making requests". Agents that hand-roll HTTP calls need the
   `ok`/`description`/`error_code` envelope to do error handling at all.

3. **getUpdates and webhooks are mutually exclusive; updates are retained max 24 hours.**
   Cited by: bots/api "Getting updates" ("two mutually exclusive ways... they will not be
   kept longer than 24 hours") and getUpdates Note 1 ("will not work if an outgoing
   webhook is set up"). This is the single most common silent failure.

4. **Webhook constraints: HTTPS only, ports 443/80/88/8443 only, `secret_token` verified
   via the `X-Telegram-Bot-Api-Secret-Token` header, `max_connections` 1-100 (default 40),
   non-2XX responses are retried.**
   Cited by: bots/api setWebhook ("Ports currently supported for webhooks: 443, 80, 88,
   8443"; "the request will contain a header X-Telegram-Bot-Api-Secret-Token").

5. **`allowed_updates` semantics.** An empty/unspecified list delivers everything EXCEPT
   `chat_member`, `message_reaction`, and `message_reaction_count`; those three require
   explicit opt-in. The parameter does not affect updates created before the call.
   Cited by: bots/api getUpdates / setWebhook `allowed_updates` rows.

6. **Group privacy mode.** Enabled by default: in groups a non-admin bot only receives
   commands, replies to its own messages, and @mentions. Bots added as admins always
   receive everything. Toggling requires the bot to be re-added to the group.
   Cited by: bots/features "Privacy mode" ("enabled by default for all bots, except bots
   that were added to a group as admins... the bot will need to be re-added to the group
   for this change to take effect"). Without this, "my group bot gets no messages" is
   unexplainable.

7. **Callback queries must be answered.** `answerCallbackQuery` is required for every
   `callback_query`, `text` is capped at 0-200 characters.
   Cited by: bots/api answerCallbackQuery ("0-200 characters").

8. **Callback data is capped at 64 bytes** (bytes, not characters, Hebrew is 2 bytes/char
   in UTF-8). Cited by: bots/api InlineKeyboardButton `callback_data` ("1-64 bytes").

9. **Rate limits and 429 handling.** ~30 msg/sec broadcast, ~1 msg/sec per chat, 20
   msg/min per group; 429 carries `ResponseParameters.retry_after` which must be honoured.
   Cited by: bots/faq "My bot is hitting limits" and bots/api `ResponseParameters.retry_after`.
   The skill must name a concrete auto-retry/throttle mechanism per framework.

10. **File limits and the local Bot API server.** Cloud server: upload ≤ 50 MB, download
    ≤ 20 MB (`getFile`: "bots can download files of up to 20MB in size"). A self-hosted
    server lifts this to unlimited download / 2000 MB upload and local-path `file_path`.
    **Switching requires calling `logOut` on the cloud server first** ("You must log out
    the bot before running it locally, otherwise there is no guarantee that the bot will
    receive updates"; 10-minute lockout), and `close` when moving between local servers.
    Cited by: bots/api "Using a Local Bot API Server", getFile, logOut, close.
    None of this has anything to do with Telegram Premium.

11. **`file_id` is bound to one bot id**, a test bot cannot reuse the production bot's
    file_ids. Cited by: bots/features "Testing your bot".

12. **Formatting-mode escaping.** HTML mode requires escaping `<`, `>`, `&`; MarkdownV2
    requires escaping 18 reserved characters. Cited by: bots/api "Formatting options".
    For Hebrew-heavy text, HTML is the defensible default.

### Payments (Bot API 10.x)

13. **Telegram Stars invoices.** `currency = "XTR"`, **`provider_token` must be an empty
    string**, and **`prices` must contain exactly one item**; `max_tip_amount` is not
    supported. Cited by: bots/api sendInvoice ("Pass an empty string for payments in
    Telegram Stars"; "Must contain exactly one item for payments in Telegram Stars";
    "Not supported for payments in Telegram Stars"). Passing a provider token or two
    price lines is an immediate API error.

14. **`pre_checkout_query` must be answered with `answerPreCheckoutQuery` within 10
    seconds**, and `successful_payment` is the fulfilment signal. Cited by: bots/api
    answerPreCheckoutQuery ("the Bot API will send an Update... The Bot API must receive
    an answer within 10 seconds").

15. **Stars refunds go through `refundStarPayment(user_id, telegram_payment_charge_id)`.**
    Cited by: bots/api refundStarPayment.

16. **Stars subscriptions: `subscription_period` is required to be exactly 2592000
    (30 days)**, and `editUserStarSubscription` cancels/re-enables renewal.
    Cited by: bots/api createInvoiceLink `subscription_period` (NOT sendInvoice, which has
    no such parameter) ("Currently, it must always be
    2592000 (30 days)") and editUserStarSubscription.

### Mini Apps

17. **`initData` HMAC validation.** secret = `HMAC_SHA256(bot_token, "WebAppData")`;
    data-check-string = all received fields except `hash`, sorted alphabetically, joined
    with `\n`. **`auth_date` must additionally be checked for freshness** and the hash
    comparison should be constant-time.
    Cited by: bots/webapps "Validating data received via the Mini App" ("To prevent the
    use of outdated data, you can additionally check the auth_date field").

18. **`web_app_data` only arrives from a `KeyboardButton` web_app (reply keyboard), never
    from an inline-keyboard web_app button**, inline/menu-button Mini Apps must post to
    your backend and authenticate with `initData`. Cited by: bots/api WebAppData /
    KeyboardButton (`web_app`: "available in private chats only") vs InlineKeyboardButton.

19. **Mini App origin hardening (Bot API 10.2, enforced 2026-07-20):** Mini App methods
    may no longer be invoked from origins other than the original Mini App domain.
    Cited by: bots/api changelog, July 14 2026 ("Hardened the security of Mini Apps by
    disallowing the usage of Mini App methods from origins different from the original
    Mini App domain. The protection will be automatically enabled... on July 20, 2026").

### Telegram Business

20. **Eligibility.** Connecting a bot to a business account does **not** require Telegram
    Premium; the other Business features do.
    Cited by: core.telegram.org/api/business ("All Telegram Business features are
    available for free to Premium subscribers. Additionally, connected bots are also
    available to non-Premium users") and bots/api 10.0 changelog ("Allowed Secretary Bots
    to manage accounts of users without a Telegram Premium subscription").

21. **`BusinessConnection` shape.** Fields are `id`, `user`, `user_chat_id`, `date`,
    `rights` (optional, `BusinessBotRights`), `is_enabled`. There is **no top-level
    `can_reply`**, it lives at `rights.can_reply` and is scoped to "private chats that
    had incoming messages **in the last 24 hours**".
    Cited by: bots/api BusinessConnection and BusinessBotRights.

22. **`business_connection_id` must be echoed on every outgoing call** made on the user's
    behalf, and the real method surface is: `getBusinessConnection`, `readBusinessMessage`,
    `deleteBusinessMessages`, `set/removeBusinessAccountName|Username|Bio|ProfilePhoto|
    GiftSettings`, `getBusinessAccountStarBalance`, `transferBusinessAccountStars`,
    `getBusinessAccountGifts`. **There is no chat-listing method.**
    Cited by: bots/api sendMessage `business_connection_id` row + the method index.

### Framework layer

23. **Current versions and their real Bot API coverage**, grammY 1.45.x (tracks 10.2),
    python-telegram-bot 22.8, Telegraf 4.16.3 (last released 2024-02-29, effectively
    dormant, types stuck around Bot API 7.x). A framework table that presents Telegraf as
    a peer choice without stating its dormancy misdirects the user.
    Cited by: npm/PyPI release metadata; telegraf.js.org.

24. **python-telegram-bot optional extras are not optional in practice.**
    `JobQueue` is `None` unless installed via `python-telegram-bot[job-queue]`;
    `run_webhook` needs `[webhooks]` (tornado); `AIORateLimiter` needs `[rate-limiter]`;
    `CallbackDataCache` needs `[callback-data]`.
    Cited by: docs.python-telegram-bot.org "Installing" / "Optional Dependencies".
    Code that calls `application.job_queue.run_daily(...)` after a bare
    `pip install python-telegram-bot` raises `AttributeError` on `None`.

25. **python-telegram-bot v20+ is fully async and `pytz`-free**, schedule with
    `zoneinfo.ZoneInfo` / `datetime.timezone`, not `pytz` (which is no longer a
    dependency). Cited by: docs.python-telegram-bot.org v20 transition guide.

26. **grammY `session()` ships in the `grammy` core package**, not `@grammyjs/session`;
    only the storage adapters (`@grammyjs/storage-redis`, `-file`, ...) are separate.
    Cited by: grammy.dev/plugins/session.

---

## Should cover (advanced)

1. **`setMyCommands` with `language_code` scoping** so Hebrew and English users see
   different command menus, plus `BotCommandScope*` for per-chat menus.
   Cited by: bots/api setMyCommands (`language_code`, `scope`).

2. **`@grammyjs/auto-retry`** as the primary 429 answer for grammY (the older
   `transformer-throttler` has not been released since 2022). Cited by: grammy.dev/plugins/auto-retry.

3. **grammY conversations v2 API shape**, `conversations()` must be installed before
   `createConversation`; context needs `ConversationFlavor<Context>`; non-deterministic /
   side-effecting code must be wrapped in `conversation.external()` because the engine
   replays the handler; plugins go through `createConversation(fn, { plugins: [...] })`.
   Cited by: grammy.dev/plugins/conversations.

4. **Paid broadcasts**, 1000 msg/sec ceiling at 0.1 Stars per message above the free 30/s,
   gated on ≥100k Stars balance and ≥100k MAU. Cited by: bots/faq "How can I message all
   of my bot's subscribers at once?".

5. **Deep linking** (`t.me/<bot>?start=<payload>`, `A-Z a-z 0-9 _ -`, base64url for binary)
   for attribution and account linking. Cited by: bots/features "Deep Linking".

6. **Dedicated test environment** (separate account, `bot<token>/test/METHOD`) and the
   caveat that flood limits there are stricter, so never hardcode limit values.
   Cited by: bots/features "Dedicated test environment".

7. **Forum topics / `message_thread_id`** and `direct_messages_topic_id` for channel DM
   chats, required to reply in the right thread. Cited by: bots/api sendMessage.

8. **`link_preview_options`** replaced `disable_web_page_preview`; the latter is legacy.
   Cited by: bots/api sendMessage.

9. **Message reactions** (`setMessageReaction`, `message_reaction` update requiring admin
   + explicit `allowed_updates`, and 10.0's `deleteMessageReaction` /
   `deleteAllMessageReactions`). Cited by: bots/api 10.0 changelog.

10. **Bot API 10.x new surfaces the skill claims in its description:** guest mode
    (`supports_guest_queries`, `guest_message`, `answerGuestQuery`), Managed Bots
    (`ManagedBotUpdated`, `getManagedBotAccessSettings`, `setManagedBotAccessSettings`),
    Ephemeral Messages (10.2: `receiver_user_id`, `ephemeral_message_id`,
    `editEphemeralMessage*`, `deleteEphemeralMessage`), Rich Messages
    (`sendRichMessage`, `sendRichMessageDraft` for streaming AI replies), and Communities.
    Cited by: bots/api "Recent changes" 10.0 / 10.1 / 10.2.

11. **Gifts semantics**, `getAvailableGifts` for the catalogue; **a gift sent by a bot via
    `sendGift` cannot be converted to Stars by the receiver**; `convertGiftToStars` applies
    to gifts owned by a managed business account (`can_convert_gifts_to_stars`).
    Cited by: bots/api sendGift ("The gift can't be converted to Telegram Stars by the
    receiver") and BusinessBotRights.

12. **`sendPaidMedia` / `star_count`** for paywalled photos and videos.
    Cited by: bots/api sendPaidMedia.

13. **Third-party Mini App data validation via Ed25519 `signature`** with Telegram's
    published production public key, for when initData must be handed to a partner without
    sharing the bot token. Cited by: bots/webapps "Validating data for Third-Party Use".

14. **Graceful handling of `403 Forbidden: bot was blocked by the user`** and
    `migrate_to_chat_id` on group→supergroup migration.
    Cited by: bots/api ResponseParameters.

15. **Webhook idempotency**, non-2XX triggers redelivery, so update handling should be
    idempotent (dedupe on `update_id`), and heavy work should be queued rather than done
    inline. Cited by: bots/api setWebhook.

16. **Israel-specific**: `Asia/Jerusalem` DST-safe scheduling, `request_contact` +972
    normalisation, and Hebrew bidi handling (LRM/RLM) in buttons and mixed-direction text.
    Cited by: bots/api KeyboardButton `request_contact`; Unicode Bidi Algorithm (UAX #9).

---

## Out of scope (explicit)

- **MTProto / user-account clients** (Telethon, Pyrogram, TDLib as a userbot). Different
  auth model and different ToS surface; bot-token clients cannot do it.
- **Telegram Passport**, deprecated in practice, no Israeli use case.
- **Telegram Games platform** (`sendGame`, `setGameScore`), separate product area.
- **TON / crypto wallet integrations**, regulatory surface out of scope for this skill.
- **Channel/group moderation-bot administration** beyond the API primitives.
- **WhatsApp, voice, and generic chatbot conversation design**, routed to
  `israeli-whatsapp-business`, `hebrew-voice-bot-builder`, `hebrew-chatbot-builder`.
- **Hosting-provider tutorials** beyond the three deployment recipes already bundled.
- **Building the Mini App front-end itself** (React/Vite tooling), only the
  bot-side contract and `initData` validation belong here.

---

## Authoritative sources

| Source | Used for |
|---|---|
| https://core.telegram.org/bots/api | Method/type reference, 10.0-10.2 changelog, webhook + local-server + file limits |
| https://core.telegram.org/bots/api-changelog | Historical version attribution |
| https://core.telegram.org/api/business | Business feature eligibility (Premium vs non-Premium connected bots) |
| https://core.telegram.org/bots/webapps | Mini Apps SDK, initData HMAC + Ed25519 validation, event list |
| https://core.telegram.org/bots/features | Privacy mode, deep linking, inline mode, test environment, file_id scoping |
| https://core.telegram.org/bots/faq | Broadcast rate limits, paid broadcasts |
| https://core.telegram.org/bots/payments | Payment/pre-checkout flow |
| https://github.com/tdlib/telegram-bot-api | Self-hosted Bot API server (currently 10.2) |
| https://grammy.dev/ | grammY 1.45.x core + plugin APIs |
| https://docs.python-telegram-bot.org/ | python-telegram-bot 22.8, optional extras, v20 async transition |
| https://telegraf.js.org/ | Telegraf 4.16.3 API surface and maintenance status |
| https://t.me/botnews | Release announcements |

_Verified 2026-07-25 against Bot API 10.2._
