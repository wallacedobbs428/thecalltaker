# Call Setup Contract

The client onboarding flow stores call setup locally in the browser only. It does not configure CTOS, Supabase, GHL, Voice AI, SMS, email, webhooks, phone forwarding, or any live provider.

## Local Storage

- Key: `tct_call_setup_v1`
- Schema version: `2`
- Writer: `client/onboarding.html` through `TCTCallFlow.createLocalSetupStore(localStorage)`
- Reader: `client/dashboard.html` through the same local store wrapper

## Contract Shape

```json
{
  "schemaVersion": 2,
  "setupCompletion": "complete",
  "business": {
    "name": "Thompson Plumbing",
    "industry": "Plumbing",
    "location": "Nashville, TN"
  },
  "hours": {
    "weekday": "8 AM - 6 PM",
    "saturday": "Closed",
    "sunday": "Closed"
  },
  "services": {
    "offered": ["Drain cleaning", "Emergency plumbing"],
    "serviceArea": "Nashville metro"
  },
  "callHandling": {
    "greeting": "Thank you for calling Thompson Plumbing. How can I help?",
    "emergencyForwardNumber": "+16155550199"
  },
  "activation": {
    "liveProviderConfigured": false,
    "providerStatus": "not-configured"
  },
  "meta": {
    "savedAt": "ISO-8601 timestamp",
    "updatedAt": "ISO-8601 timestamp",
    "storage": "local-only"
  }
}
```

## Future Backend Boundary

`client/call-flow.js` exposes `createBackendPersistenceAdapter()` as an explicit placeholder. It intentionally returns a skipped result and makes no network calls.

A future real persistence implementation must:

- live behind an authenticated server endpoint
- revalidate the schema v2 payload server-side
- associate setup with a verified client/account identity
- persist the contract before provider setup begins
- update `activation.providerStatus` only after real provider work is complete
- require explicit operator approval before CTOS, Supabase, GHL, Voice AI, SMS, email, webhooks, or phone routing changes

Local setup completion means the client has supplied required configuration fields. It does not mean the business line is live, provider routing is configured, backend sync exists, or any SMS/email/call/webhook automation is active.
