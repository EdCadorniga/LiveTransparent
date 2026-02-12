# Twilio Node Reference

This reference tracks 10 commonly used Twilio automation actions and API calls for n8n workflows.

## Runtime Notes
- n8n built-in app node: `n8n-nodes-base.twilio`
- n8n built-in trigger node: `n8n-nodes-base.twilioTrigger`
- n8n built-in Twilio operations currently cover:
  - `SMS -> Send SMS/MMS/WhatsApp message`
  - `Call -> Make a phone call`
- For other Twilio resources, use `n8n-nodes-base.httpRequest` with Twilio credentials.

## Node Map
1. `Twilio 01 - Send SMS/MMS/WhatsApp`
   - Node: `n8n-nodes-base.twilio`
   - `POST /2010-04-01/Accounts/{AccountSid}/Messages.json`
2. `Twilio 02 - Fetch Message Status`
   - Node: `n8n-nodes-base.httpRequest`
   - `GET /2010-04-01/Accounts/{AccountSid}/Messages/{MessageSid}.json`
3. `Twilio 03 - List Messages`
   - Node: `n8n-nodes-base.httpRequest`
   - `GET /2010-04-01/Accounts/{AccountSid}/Messages.json`
4. `Twilio 04 - Make Outbound Call`
   - Node: `n8n-nodes-base.twilio`
   - `POST /2010-04-01/Accounts/{AccountSid}/Calls.json`
5. `Twilio 05 - Fetch Call Status`
   - Node: `n8n-nodes-base.httpRequest`
   - `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}.json`
6. `Twilio 06 - Redirect or End Active Call`
   - Node: `n8n-nodes-base.httpRequest`
   - `POST /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}.json`
7. `Twilio 07 - List Incoming Phone Numbers`
   - Node: `n8n-nodes-base.httpRequest`
   - `GET /2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers.json`
8. `Twilio 08 - Provision Incoming Phone Number`
   - Node: `n8n-nodes-base.httpRequest`
   - `POST /2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers.json`
9. `Twilio 09 - Start OTP Verification`
   - Node: `n8n-nodes-base.httpRequest`
   - `POST https://verify.twilio.com/v2/Services/{ServiceSid}/Verifications`
10. `Twilio 10 - Check OTP Verification Code`
   - Node: `n8n-nodes-base.httpRequest`
   - `POST https://verify.twilio.com/v2/Services/{ServiceSid}/VerificationCheck`

## Source Docs
- https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.twilio/
- https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.twiliotrigger/
- https://www.twilio.com/docs/messaging/api/message-resource
- https://www.twilio.com/docs/voice/api/call-resource
- https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource
- https://www.twilio.com/docs/verify/api/verification
- https://www.twilio.com/docs/verify/api/verification-check
