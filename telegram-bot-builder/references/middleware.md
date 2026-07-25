# Middleware and handler-group patterns

### Middleware Patterns

Middleware runs before handlers and is essential for logging, authentication, rate limiting, and i18n.

**grammY middleware:**

```typescript
// Logging middleware
bot.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`Update ${ctx.update.update_id} processed in ${ms}ms`);
});

// Auth middleware (restrict to specific users)
function adminOnly(ctx: Context, next: () => Promise<void>) {
  const adminIds = [123456789, 987654321]; // Telegram user IDs
  if (ctx.from && adminIds.includes(ctx.from.id)) {
    return next();
  }
  return ctx.reply("אין לך הרשאה לפקודה זו.");
}

bot.command("admin", adminOnly, async (ctx) => {
  await ctx.reply("פאנל ניהול");
});
```

**python-telegram-bot does not use middleware** in the same way. Instead, use handler groups with different priorities:

```python
# Group 0 (default) handlers run first, then group 1, etc.
# Use group -1 for "middleware-like" behavior
async def log_update(update: Update, context) -> None:
    logger.info(f"Update from user {update.effective_user.id}")

application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)
```

