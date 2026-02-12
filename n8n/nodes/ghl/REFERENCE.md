# GHL Node Reference

This reference tracks 10 commonly used GHL (HighLevel/LeadConnector) automation nodes and API actions for n8n workflows.

## Runtime Notes
- n8n built-in app node: `n8n-nodes-base.highLevel` (HighLevel)
- n8n built-in operations currently cover: Contact, Opportunity, Task, Calendar
- For messaging and tag endpoints not exposed by the built-in node, use `n8n-nodes-base.httpRequest`

## Node Map
1. `GHL 01 - Upsert Contact`
   - `POST /contacts/upsert`
2. `GHL 02 - Search Contacts`
   - `POST /contacts/search`
3. `GHL 03 - Add Contact Tags`
   - `POST /contacts/:contactId/tags`
4. `GHL 04 - Create Opportunity`
   - `POST /opportunities/`
5. `GHL 05 - Update Opportunity Status`
   - `PUT /opportunities/:id/status`
6. `GHL 06 - Create Task`
   - `POST /contacts/:contactId/tasks`
7. `GHL 07 - Create Note`
   - `POST /contacts/:contactId/notes`
8. `GHL 08 - Get Free Calendar Slots`
   - `GET /calendars/:calendarId/free-slots`
9. `GHL 09 - Create Appointment`
   - `POST /calendars/events/appointments`
10. `GHL 10 - Send Conversation Message`
   - `POST /conversations/messages`

## Source Docs
- https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.highlevel/
- https://marketplace.gohighlevel.com/docs/
- https://marketplace.gohighlevel.com/docs/ghl/contacts/upsert-contact
- https://marketplace.gohighlevel.com/docs/ghl/contacts/search-contacts-advanced
- https://marketplace.gohighlevel.com/docs/ghl/contacts/add-tags
- https://marketplace.gohighlevel.com/docs/ghl/opportunities/create-opportunity/index.html
- https://marketplace.gohighlevel.com/docs/ghl/opportunities/update-opportunity-status/index.html
- https://marketplace.gohighlevel.com/docs/ghl/contacts/create-task/index.html
- https://marketplace.gohighlevel.com/docs/ghl/contacts/create-note
- https://marketplace.gohighlevel.com/docs/ghl/calendars/get-slots/index.html
- https://marketplace.gohighlevel.com/docs/ghl/calendars/create-appointment
- https://marketplace.gohighlevel.com/docs/ghl/conversations/send-a-new-message/index.html
