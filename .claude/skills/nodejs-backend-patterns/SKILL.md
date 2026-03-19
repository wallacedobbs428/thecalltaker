---
name: nodejs-backend-patterns
description: "Build Node.js backend services with best practices. Use when creating Express/Fastify APIs, webhook handlers, background workers, or server-side JavaScript. Covers project structure, middleware, error handling, database patterns, and deployment."
category: backend
---

# Node.js Backend Patterns

Build reliable Node.js services with clean architecture.

---

## Project Structure

```
src/
├── index.js            # Entry point — starts server
├── routes/             # Route handlers
│   ├── contacts.js
│   ├── webhooks.js
│   └── health.js
├── middleware/          # Express middleware
│   ├── auth.js
│   ├── rateLimit.js
│   └── errorHandler.js
├── services/           # Business logic
│   ├── ghl.js          # GHL API wrapper
│   ├── notifications.js
│   └── scoring.js
├── utils/              # Pure utility functions
│   ├── validators.js
│   └── formatters.js
└── config/
    └── index.js        # Environment config
```

---

## Express API Setup

```javascript
const express = require('express');
const app = express();

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// CORS (if needed)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'https://thecalltaker.com');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  next();
});

// Routes
app.use('/api/contacts', require('./routes/contacts'));
app.use('/api/webhooks', require('./routes/webhooks'));
app.get('/health', (req, res) => res.json({ status: 'ok', timestamp: new Date().toISOString() }));

// Error handler (must be last)
app.use(require('./middleware/errorHandler'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

---

## Route Handler Pattern

```javascript
// routes/contacts.js
const express = require('express');
const router = express.Router();
const { getContact, createContact } = require('../services/ghl');

// GET /api/contacts/:id
router.get('/:id', async (req, res, next) => {
  try {
    const contact = await getContact(req.params.id);
    if (!contact) {
      return res.status(404).json({ error: { code: 'NOT_FOUND', message: 'Contact not found' } });
    }
    res.json({ data: contact });
  } catch (err) {
    next(err); // Pass to error handler
  }
});

// POST /api/contacts
router.post('/', async (req, res, next) => {
  try {
    const { firstName, email, phone } = req.body;
    if (!firstName) {
      return res.status(400).json({ error: { code: 'MISSING_FIELD', message: 'firstName is required' } });
    }
    const contact = await createContact({ firstName, email, phone });
    res.status(201).json({ data: contact });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
```

---

## Error Handling Middleware

```javascript
// middleware/errorHandler.js
module.exports = (err, req, res, next) => {
  console.error(`[${new Date().toISOString()}] ${err.message}`, {
    path: req.path,
    method: req.method,
    stack: err.stack,
  });

  // Known error types
  if (err.name === 'ValidationError') {
    return res.status(400).json({ error: { code: 'VALIDATION', message: err.message } });
  }

  if (err.status === 429) {
    return res.status(429).json({ error: { code: 'RATE_LIMITED', message: 'Too many requests' } });
  }

  // Default 500
  res.status(500).json({
    error: { code: 'INTERNAL', message: 'Something went wrong' }
  });
};
```

---

## Webhook Handler Pattern

```javascript
// routes/webhooks.js
const crypto = require('crypto');

router.post('/stripe', express.raw({ type: 'application/json' }), (req, res) => {
  // 1. Verify signature
  const sig = req.headers['stripe-signature'];
  const payload = req.body;
  const expected = crypto
    .createHmac('sha256', process.env.STRIPE_WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');

  if (sig !== `sha256=${expected}`) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // 2. Parse event
  const event = JSON.parse(payload);

  // 3. Acknowledge immediately
  res.status(200).json({ received: true });

  // 4. Process async (don't block the response)
  processWebhookEvent(event).catch(err => {
    console.error('Webhook processing failed:', err);
  });
});

async function processWebhookEvent(event) {
  switch (event.type) {
    case 'checkout.session.completed':
      await handlePayment(event.data.object);
      break;
    case 'customer.subscription.deleted':
      await handleChurn(event.data.object);
      break;
  }
}
```

---

## Environment Configuration

```javascript
// config/index.js
const config = {
  port: parseInt(process.env.PORT || '3000'),
  ghl: {
    apiKey: process.env.GHL_API_KEY,
    locationId: process.env.GHL_LOCATION_ID || 'tQb9YmrGDrdVUJYPKrsY',
    baseUrl: 'https://services.leadconnectorhq.com',
  },
  ntfy: {
    urgentTopic: process.env.NTFY_URGENT || 'tct-urgent-Hk9UOEZR',
    salesTopic: process.env.NTFY_SALES || 'tct-sales-63uYsIT9',
  },
  isProduction: process.env.NODE_ENV === 'production',
};

// Validate required config
const required = ['ghl.apiKey'];
for (const key of required) {
  const value = key.split('.').reduce((obj, k) => obj?.[k], config);
  if (!value) {
    throw new Error(`Missing required config: ${key}`);
  }
}

module.exports = config;
```

---

## Rate Limiting

```javascript
// middleware/rateLimit.js
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 100,              // 100 requests per minute
  message: { error: { code: 'RATE_LIMITED', message: 'Too many requests, try again later' } },
  standardHeaders: true,
  legacyHeaders: false,
});

module.exports = { apiLimiter };
```

---

## Async Patterns

### Promise with Timeout
```javascript
function withTimeout(promise, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
  );
  return Promise.race([promise, timeout]);
}

// Usage
const contact = await withTimeout(getContact(id), 5000);
```

### Retry with Backoff
```javascript
async function retry(fn, maxRetries = 3) {
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === maxRetries) throw err;
      await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000));
    }
  }
}
```
