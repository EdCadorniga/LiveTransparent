const https = require('https');

const tests = [
  { desc: 'exists operator', body: { locationId: 'Zwz4relUXVPxx8uohnjV', pageLimit: 10, page: 1, filters: [{ field: 'customFields.apollo_person_linkedin_url', operator: 'exists' }] } },
  { desc: 'not_eq empty string', body: { locationId: 'Zwz4relUXVPxx8uohnjV', pageLimit: 10, page: 1, filters: [{ field: 'customFields.apollo_person_linkedin_url', operator: 'not_eq', value: '' }] } },
  { desc: 'contains linkedin.com', body: { locationId: 'Zwz4relUXVPxx8uohnjV', pageLimit: 10, page: 1, filters: [{ field: 'customFields.apollo_person_linkedin_url', operator: 'contains', value: 'linkedin.com' }] } },
  { desc: 'match linkedin', body: { locationId: 'Zwz4relUXVPxx8uohnjV', pageLimit: 10, page: 1, filters: [{ field: 'customFields.apollo_person_linkedin_url', operator: 'match', value: 'linkedin' }] } },
  { desc: 'nested customFields', body: { locationId: 'Zwz4relUXVPxx8uohnjV', pageLimit: 10, page: 1, filters: [{ field: 'customFields', operator: 'contains', value: 'apollo_person_linkedin_url' }] } },
];

let i = 0;
function runNext() {
  if (i >= tests.length) { console.log('Done'); process.exit(0); }
  const t = tests[i];
  console.log('\n--- Test:', t.desc, '---');
  const bodyStr = JSON.stringify(t.body);
  const options = {
    hostname: 'services.leadconnectorhq.com',
    path: '/contacts/search',
    method: 'POST',
    headers: {
      'Authorization': 'Bearer pit-2d2ed8c3-9297-482e-b8f2-3615e7003c86',
      'Version': '2021-07-28',
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(bodyStr),
    },
  };
  const req = https.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
      try {
        const parsed = JSON.parse(data);
        const count = parsed.contacts ? parsed.contacts.length : 'N/A';
        console.log('Status:', res.statusCode, '| Contacts:', count);
        if (res.statusCode !== 200) console.log('Error:', parsed.message || parsed.error);
        else if (parsed.contacts && parsed.contacts.length > 0) {
          console.log('IDs:', parsed.contacts.map(c => c.id).join(', '));
        }
      } catch {
        console.log('Status:', res.statusCode, 'Raw:', data.substring(0, 300));
      }
      i++;
      runNext();
    });
  });
  req.on('error', (e) => { console.error('Error:', e.message); i++; runNext(); });
  req.write(bodyStr);
  req.end();
}
runNext();
