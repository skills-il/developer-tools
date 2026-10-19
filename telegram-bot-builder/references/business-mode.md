# Bot Business Mode: connection, rights and methods

Telegram Business lets a user connect a bot to their personal account so it can read and reply to direct messages on their behalf (Bot API 7.2, 2024). Connecting a bot does not require Telegram Premium since Bot API 10.0; see SKILL.md for the exact wording.

## The connection

When the user connects the bot, your bot receives a `business_connection` update with a `business_connection_id`. Every message that arrives in one of the user's connected chats then carries that same `business_connection_id` field, and any outgoing call (`sendMessage`, `editMessageText`, etc.) must echo it back so Telegram routes the reply through the user's account rather than the bot's account.

- `rights.can_reply` (on `BusinessBotRights`) lets the bot "send and edit messages in the private chats that had incoming messages in the last 24 hours". An off-hours auto-reply is fine; a delayed queue drain outside that window fails even when `can_reply` is true.
- Permissions live under `conn.rights`. There is no top-level `conn.can_reply`.
- Fetch the connection with `getBusinessConnection`. There is no method that lists the user's chats; you learn about a chat only when a `business_message` arrives in it.

## Methods, each gated by a `BusinessBotRights` flag

| Area | Methods |
|---|---|
| Messages | `readBusinessMessage`, `deleteBusinessMessages` |
| Profile | `setBusinessAccountName`, `setBusinessAccountUsername`, `setBusinessAccountBio`, `setBusinessAccountProfilePhoto`, `removeBusinessAccountProfilePhoto` |
| Gifts | `setBusinessAccountGiftSettings`, `getBusinessAccountGifts`, `convertGiftToStars`, `upgradeGift`, `transferGift` |
| Stars | `getBusinessAccountStarBalance`, `transferBusinessAccountStars` |
| Stories | `postStory`, `repostStory`, `editStory`, `deleteStory` |

The profile setters are **set-only** except one: `setBusinessAccountName`, `setBusinessAccountUsername`, `setBusinessAccountBio` and `setBusinessAccountGiftSettings` have no `remove*` counterpart. Only `removeBusinessAccountProfilePhoto` exists.

The grammY handlers for capturing `business_connection` and echoing `business_connection_id` on every reply are in [examples.md](examples.md), section "Bot Business: capturing the connection and replying".

Reference: [Telegram Business](https://core.telegram.org/api/business) and [`BusinessConnection`](https://core.telegram.org/bots/api#businessconnection).
