#!/usr/bin/env python3
"""
FOLLOW-UP BLITZ — Send personalized messages to warm leads.
Wallace approves each one before it sends. Run: python3 send-followups.py
"""
import json, urllib.request, sys, time

API_KEY = "pit-771d5b3f-847e-4cbe-8707-77ddc0f24b35"
LOCATION_ID = "tQb9YmrGDrdVUJYPKrsY"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Version": "2021-04-15",
    "Content-Type": "application/json",
    "User-Agent": "TheCallTaker/1.0"
}

# ============================================================
# FOLLOW-UP QUEUE — Each message waiting for Wallace's approval
# ============================================================
FOLLOWUPS = [
    {
        "name": "Chris @ Dust Digital",
        "contactId": "aXPT0A5MvemG7XlE2BoX",
        "type": "SMS",
        "phone": "+16616079873",
        "message": "Hey Chris, Wallace here from The Call Taker. Saw you checked out our med spa answering service info. Want me to set up a free 14-day trial for Dust Digital? Takes 5 min."
    },
    {
        "name": "Chris @ Dust Digital",
        "contactId": "aXPT0A5MvemG7XlE2BoX",
        "type": "Email",
        "email": "chris@dustdigital.io",
        "subject": "Your missed call report — Dust Digital",
        "message": "Hey Chris,\n\nYou grabbed our missed call report yesterday. If you want to test an AI receptionist on your med spa phones this week, I can have it live in 24 hours. No charge for 14 days, no credit card.\n\nWant me to set it up?\n\n— Wallace\nThe Call Taker | (615) 784-5747"
    },
    {
        "name": "Burton Verner",
        "contactId": "evxURE3ENgyoGdhtH8Ja",
        "type": "SMS",
        "phone": "+16155547355",
        "message": "Hey Burton, this is Wallace from The Call Taker. Saw you called our demo line last night \u2014 what'd you think? What kind of business do you run? I'm doing free 14-day pilots this week if you want to try it on your phones."
    },
    {
        "name": "James",
        "contactId": "LdLCi490GhW6K6qDw0XN",
        "type": "SMS",
        "phone": "+16158409013",
        "message": "Hey James, Wallace from The Call Taker again. We talked a few weeks back about AI answering for your business. Still interested? I have 3 free pilot slots left this week."
    },
    {
        "name": "Unknown (Waco KY)",
        "contactId": "jiy8tTGCkBBAPkQHNq7q",
        "type": "SMS",
        "phone": "+18593764092",
        "message": "Hey, this is Wallace from The Call Taker. Looks like you called us yesterday \u2014 were you checking out the AI receptionist demo? Happy to answer any questions."
    },
    {
        "name": "Air Solutions HVAC",
        "contactId": None,  # Will search by phone
        "type": "SMS",
        "phone": "+14233045898",
        "message": "Hey Phillip, Wallace from The Call Taker. We called and emailed about our AI receptionist for HVAC companies. Spring's coming \u2014 want to catch those after-hours AC calls? Free 14-day trial, I'll set it up today."
    },
    {
        "name": "Reliable Heating & AC",
        "contactId": None,
        "type": "SMS",
        "phone": "+14232662424",
        "message": "Hey David, Wallace from The Call Taker. Quick question \u2014 what happens when someone calls Reliable Heating after hours? We've got an AI that catches those calls and books the job. Free to try for 14 days. Interested?"
    },
    {
        "name": "Berry Good Heating & Air",
        "contactId": None,
        "type": "SMS",
        "phone": "+17709906809",
        "message": "Hey, Wallace from The Call Taker. We reached out about an AI receptionist for Berry Good Heating & Air. Spring AC season is starting \u2014 want to make sure you catch every call. Free 14-day pilot, no card needed. Want to try it?"
    },
    {
        "name": "All About Heating & Air",
        "contactId": None,
        "type": "SMS",
        "phone": "+14047376915",
        "message": "Hey, Wallace from The Call Taker. Following up on the AI receptionist for All About Heating & Air. Catches every after-hours call, books the job, texts you instantly. Free 14-day trial \u2014 want me to set it up?"
    },
]

def send_sms(contact_id, phone, message):
    """Send SMS via GHL conversations API."""
    data = json.dumps({
        "type": "SMS",
        "contactId": contact_id,
        "message": message
    }).encode()
    req = urllib.request.Request(
        f"https://services.leadconnectorhq.com/conversations/messages",
        data=data,
        headers=HEADERS,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def send_email(contact_id, subject, body):
    """Send Email via GHL conversations API."""
    data = json.dumps({
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": body.replace("\n", "<br>"),
        "emailFrom": "wallace@mail.thecalltaker.com"
    }).encode()
    req = urllib.request.Request(
        f"https://services.leadconnectorhq.com/conversations/messages",
        data=data,
        headers=HEADERS,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def find_contact_by_phone(phone):
    """Look up contact ID by phone number."""
    url = f"https://services.leadconnectorhq.com/contacts/?locationId={LOCATION_ID}&limit=1&query={phone}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Version": "2021-07-28",
        "User-Agent": "TheCallTaker/1.0"
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        contacts = data.get("contacts", [])
        return contacts[0]["id"] if contacts else None

def main():
    print("=" * 60)
    print("  FOLLOW-UP BLITZ — Wallace approves each message")
    print("  Type 'y' to send, 'n' to skip, 'q' to quit")
    print("=" * 60)
    print()

    sent = 0
    skipped = 0

    for i, fu in enumerate(FOLLOWUPS, 1):
        name = fu["name"]
        msg_type = fu["type"]
        message = fu["message"]
        contact_id = fu.get("contactId")

        print(f"--- [{i}/{len(FOLLOWUPS)}] {name} ({msg_type}) ---")
        print(f"To: {fu.get('phone', fu.get('email', ''))}")
        if msg_type == "Email":
            print(f"Subject: {fu.get('subject', '')}")
        print(f"Message: {message}")
        print()

        choice = input("Send? (y/n/q): ").strip().lower()

        if choice == "q":
            print(f"\nStopped. Sent: {sent}, Skipped: {skipped}")
            return

        if choice != "y":
            skipped += 1
            print("  Skipped.\n")
            continue

        try:
            # Find contact ID if not provided
            if not contact_id:
                contact_id = find_contact_by_phone(fu.get("phone", ""))
                if not contact_id:
                    print(f"  ERROR: Contact not found for {fu.get('phone', '')}. Skipping.")
                    skipped += 1
                    continue

            if msg_type == "SMS":
                result = send_sms(contact_id, fu["phone"], message)
                print(f"  SENT SMS to {name}")
            elif msg_type == "Email":
                result = send_email(contact_id, fu.get("subject", ""), message)
                print(f"  SENT EMAIL to {name}")

            sent += 1
            time.sleep(1)  # Rate limit
        except Exception as e:
            print(f"  ERROR: {e}")
            skipped += 1

        print()

    print(f"\nDone! Sent: {sent}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
