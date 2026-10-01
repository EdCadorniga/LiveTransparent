"""Wire the legacy LinkedIn inbound workflow to the shared indexed contact claim.

The n8n-lt workflow checks the normalized profile index, serializes contact
creation by profile, and persists a newly created contact before sending its
inbound message to GHL.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV: dict[str, str] = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        ENV[key.strip()] = value.strip().strip('"').strip("'")

BASE = ENV.get("N8N_EDITOR_BASE_URL") or f"{ENV.get('N8N_PROTOCOL', 'https')}://{ENV['N8N_HOST']}"
API_KEY = ENV["N8N_LT_API_KEY"]
WORKFLOW_ID = "7o5EBdvwAuIaWW7k"


def api(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    req = urllib.request.Request(
        BASE.rstrip("/") + "/api/v1" + path,
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        method=method,
        headers={
            "X-N8N-API-KEY": API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"n8n-lt returned HTTP {exc.code}; response body withheld") from None


PROFILE_MATCH_CTES = r"""), profile_field_candidates AS (
  SELECT DISTINCT idx.ghl_contact_id
  FROM incoming i
  JOIN linkedin_contact_profile_index idx
    ON idx.normalized_profile_slug = regexp_replace(
      regexp_replace(regexp_replace(lower(i.linkedin_profile_url), '^.*linkedin\\.com/in/', ''), '[?#].*$', ''), '/+$', ''
    )
  WHERE i.valid AND NOT i.ignored AND i.linkedin_profile_url IS NOT NULL
), profile_field_match_summary AS (
  SELECT COUNT(*)::integer AS profile_field_match_count,
    CASE WHEN COUNT(*) = 1 THEN MIN(ghl_contact_id) END AS profile_field_match_contact_id
  FROM profile_field_candidates
), profile_claim AS (
  SELECT pc.claim_action, pc.ghl_contact_id, pc.claim_token,
    COALESCE(NULLIF(regexp_replace(regexp_replace(regexp_replace(lower(i.linkedin_profile_url), '^.*linkedin\\.com/in/', ''), '[?#].*$', ''), '/+$', ''), ''),
      'provider:' || lower(i.linkedin_provider_id)) AS normalized_identity_key
  FROM incoming i
  CROSS JOIN LATERAL linkedin_claim_contact_profile(
    NULLIF(regexp_replace(regexp_replace(regexp_replace(lower(i.linkedin_profile_url), '^.*linkedin\\.com/in/', ''), '[?#].*$', ''), '/+$', ''), ''),
    i.linkedin_provider_id, COALESCE(i.message_id, i.linkedin_chat_id), 'classic_unipile'
  ) pc
  WHERE i.valid AND NOT i.ignored
"""

PROFILE_INDEX_SQL_CODE = r'''const row=$input.first()?.json||{};
const url=String(row.sender_profile_url||'').trim(),m=url.match(/linkedin\.com\/in\/([^/?#]+)/i);
let slug=m?String(m[1]).toLowerCase().replace(/\/+$/,''):'';try{slug=decodeURIComponent(slug)}catch{}
const provider=String(row.sender_provider_id||'').trim(),contact=String(row.ghl_contact_id||'').trim(),action=String(row.profile_claim_action||'');
const key=String(row.profile_claim_identity_key||(slug|| (provider?'provider:'+provider.toLowerCase():'')));
const token=String(row.profile_claim_token||''),name=String(row.sender_name||'');
const query=`WITH resolved AS (
 SELECT linkedin_resolve_contact_profile_claim($1,NULLIF($2,'')::uuid,$3,$4,$5,$6,$7) AS ok
 WHERE $8='owner' AND $9::boolean AND $3<>''
), indexed AS (
 INSERT INTO linkedin_contact_profile_index(ghl_contact_id,normalized_profile_slug,profile_url,contact_name,linkedin_provider_ids,refreshed_at)
 SELECT $3,COALESCE(NULLIF($4,''),NULLIF('provider:'||lower($7),'provider:')),NULLIF($5,''),NULLIF($6,''),
  CASE WHEN $7='' THEN '{}'::text[] ELSE ARRAY[$7]::text[] END,NOW()
 WHERE $9::boolean AND $3<>'' AND $8<>'owner'
  AND ($4<>'' OR $7<>'')
 ON CONFLICT(ghl_contact_id,normalized_profile_slug) DO UPDATE SET
  profile_url=COALESCE(EXCLUDED.profile_url,linkedin_contact_profile_index.profile_url),
  contact_name=COALESCE(EXCLUDED.contact_name,linkedin_contact_profile_index.contact_name),
  linkedin_provider_ids=ARRAY(SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids||EXCLUDED.linkedin_provider_ids)),refreshed_at=NOW()
 RETURNING ghl_contact_id
)
SELECT COALESCE((SELECT ok FROM resolved),EXISTS(SELECT 1 FROM indexed)) AS index_saved;`;
 return [{json:{query,values:[key,token,contact,slug,url,name,provider,action,row.should_upsert===true],should_upsert:row.should_upsert===true,contactId:contact,status:row.status||'',reason:row.reason||''}}];'''

SEND_INBOUND_CODE = r'''const base=$('Create LinkedIn Contact and Add Inbound Message').first().json||{};
const event=$('Normalize Unipile Message Event').first().json||{};
if(!base.should_upsert||!base.ghl_contact_id)return [{json:{...base,should_upsert:false}}];
const GHL_BASE='https://services.leadconnectorhq.com',VERSION='2021-07-28',COMPANY_ID='7vMmm4at5OrjQplRN3EO',LOCATION_ID='Zwz4relUXVPxx8uohnjV';
function str(v){return v===null||v===undefined?'':String(v).trim();}
function describeError(e){const b=e&&(e.error||e.response?.body||e.response?.data||e.body||e.data);if(b){try{return typeof b==='string'?b:JSON.stringify(b)}catch{}}return str(e&&e.message?e.message:e).slice(0,500)}
async function main(){
 const idx=$('Confirm LinkedIn Profile Index').first()?.json||{};if(idx.index_saved!==true)return {...base,should_upsert:false,status:'error',reason:'linkedin_profile_index_write_failed'};
 const agencyToken=str(base._oauth_access_token);if(!agencyToken)return {...base,status:'error',reason:'missing_oauth_token'};
 let locToken='';try{const r=await this.helpers.httpRequest({method:'POST',url:GHL_BASE+'/oauth/locationToken',json:true,headers:{Authorization:'Bearer '+agencyToken,Version,Accept:'application/json','Content-Type':'application/json'},body:{companyId:COMPANY_ID,locationId:LOCATION_ID}});locToken=str(r.access_token);if(!locToken)return {...base,status:'error',reason:'loc_tok_empty'};}catch(e){return {...base,status:'error',reason:'loc_tok_err: '+describeError(e)}}
 const sentBody={type:'Custom',contactId:base.ghl_contact_id,message:event.message_text,conversationProviderId:'6a58a14ff3023bea3783c152',altId:event.chat_id,date:event.timestamp||new Date().toISOString()};
 try{const resp=await this.helpers.httpRequest({method:'POST',url:GHL_BASE+'/conversations/messages/inbound',headers:{Authorization:'Bearer '+locToken,Version,Accept:'application/json','Content-Type':'application/json'},body:sentBody,json:true,returnFullResponse:true});if(resp.statusCode>=200&&resp.statusCode<300){const b=resp.body||{};return {...base,status:'processed',ghl_conversation_id:str(b.conversationId||b.conversation?.id),ghl_message_id:str(b.messageId||b.id),sentBody:JSON.stringify(sentBody),_oauth_access_token:undefined};}return {...base,status:'error',reason:'inbound_failed: status='+resp.statusCode,sentBody:JSON.stringify(sentBody),_oauth_access_token:undefined};}catch(e){return {...base,status:'error',reason:'inbound_failed: '+describeError(e),sentBody:JSON.stringify(sentBody),_oauth_access_token:undefined}}
}
try{return [{json:await main.call(this)}]}catch(e){return [{json:{...base,status:'error',reason:'inbound_failed: '+describeError(e),_oauth_access_token:undefined}}]}'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} anchor; found {count}")
    return source.replace(old, new, 1)


def patch_workflow(workflow: dict) -> tuple[dict, bool]:
    if workflow.get("name") != "LT - LinkedIn Unipile New Messages" or not workflow.get("active"):
        raise RuntimeError("Unexpected or inactive n8n-lt workflow; refusing update")
    nodes = workflow.get("nodes", [])
    lookup_node = next((n for n in nodes if n.get("name") == "Build Lookup Map SQL"), None)
    handler_node = next((n for n in nodes if n.get("name") == "Create LinkedIn Contact and Add Inbound Message"), None)
    map_node = next((n for n in nodes if n.get("name") == "Build Upsert Map SQL"), None)
    if not lookup_node or not handler_node or not map_node:
        raise RuntimeError("Expected inbound resolver nodes were not found")

    lookup_code = lookup_node["parameters"]["jsCode"]
    handler_code = handler_node["parameters"]["jsCode"]
    map_code = map_node["parameters"]["jsCode"]
    marker = "profile_field_candidates AS ("
    changed = False
    if marker not in lookup_code:
        lookup_code = replace_once(
            lookup_code,
            "), claim_state AS (",
            PROFILE_MATCH_CTES + "), claim_state AS (",
            "profile-field CTE insertion",
        )
        lookup_code = replace_once(
            lookup_code,
            "COALESCE(s.ghl_contact_id, m.ghl_contact_id, c.ghl_contact_id) AS mapped_ghl_contact_id,",
            "COALESCE(s.ghl_contact_id, m.ghl_contact_id, c.ghl_contact_id, CASE WHEN pf.profile_field_match_count = 1 THEN pf.profile_field_match_contact_id END) AS mapped_ghl_contact_id,\n  pf.profile_field_match_count, pf.profile_field_match_contact_id,",
            "mapped contact projection",
        )
        lookup_code = replace_once(
            lookup_code,
            "LEFT JOIN claim_state c ON TRUE;`",
            "LEFT JOIN claim_state c ON TRUE LEFT JOIN profile_field_match_summary pf ON TRUE;`",
            "profile-match summary join",
        )
        changed = True
    else:
        start = lookup_code.find("), profile_field_candidates AS (")
        end_anchor = "), claim_state AS ("
        end = lookup_code.find(end_anchor, start)
        if start < 0 or end < 0:
            raise RuntimeError("Could not identify existing profile lookup CTE boundaries")
        current_profile_cte = lookup_code[start:end]
        if "linkedin_claim_contact_profile" not in current_profile_cte:
            lookup_code = lookup_code[:start] + PROFILE_MATCH_CTES + end_anchor + lookup_code[end + len(end_anchor):]
            changed = True

    if "pc.claim_token AS profile_claim_token" not in lookup_code:
        old_projection = "pf.profile_field_match_count, pf.profile_field_match_contact_id,"
        lookup_code = replace_once(
            lookup_code,
            old_projection,
            old_projection + " pc.claim_action AS profile_claim_action, pc.claim_token AS profile_claim_token, pc.normalized_identity_key AS profile_claim_identity_key,",
            "shared profile claim projection",
        )
        old_join = "LEFT JOIN profile_field_match_summary pf ON TRUE;`"
        if old_join in lookup_code:
            lookup_code = replace_once(lookup_code, old_join, "LEFT JOIN profile_field_match_summary pf ON TRUE LEFT JOIN profile_claim pc ON TRUE;`", "shared profile claim join")
        else:
            lookup_code = replace_once(lookup_code, "LEFT JOIN claim_state c ON TRUE LEFT JOIN profile_field_match_summary pf ON TRUE;`", "LEFT JOIN claim_state c ON TRUE LEFT JOIN profile_field_match_summary pf ON TRUE LEFT JOIN profile_claim pc ON TRUE;`", "shared profile claim join")
        lookup_code = replace_once(
            lookup_code,
            "COALESCE(s.ghl_contact_id, m.ghl_contact_id, c.ghl_contact_id, CASE WHEN pf.profile_field_match_count = 1 THEN pf.profile_field_match_contact_id END) AS mapped_ghl_contact_id,",
            "COALESCE(s.ghl_contact_id, m.ghl_contact_id, c.ghl_contact_id, CASE WHEN pf.profile_field_match_count = 1 THEN pf.profile_field_match_contact_id END, pc.ghl_contact_id) AS mapped_ghl_contact_id,",
            "shared profile match projection",
        )
        changed = True

    ambiguity_guard = """  var profileFieldMatchCount = Number(row.profile_field_match_count || 0);
  if (profileFieldMatchCount > 1) {
    return { ...payload, should_upsert: false, status: 'error', reason: 'ambiguous_linkedin_profile_field_match', identity_key: str(row.identity_key || ''), identity_claim_status: claimStatus, identity_claim_owner_message_id: str(row.identity_claim_owner_message_id || '') };
  }
"""
    if "var profileFieldMatchCount = Number(row.profile_field_match_count || 0);" not in handler_code:
        handler_code = replace_once(
            handler_code,
            "  if (contactId) {\n    match = { id: contactId, reason: row.identity_claim_contact_id ? 'identity_claim_reuse' : 'mapped_contact' };",
            ambiguity_guard + "  if (contactId) {\n    match = { id: contactId, reason: row.identity_claim_contact_id ? 'identity_claim_reuse' : (row.profile_field_match_contact_id && String(row.profile_field_match_contact_id) === contactId ? 'exact_linkedin_profile_field_match' : 'mapped_contact') };",
            "ambiguous-match guard and resolution reason",
        )
        changed = True
    elif "if (!contactId && profileFieldMatchCount > 1)" in handler_code:
        handler_code = handler_code.replace("if (!contactId && profileFieldMatchCount > 1)", "if (profileFieldMatchCount > 1)", 1)
        changed = True
    if "var profileClaimAction = str(row.profile_claim_action || '');" not in handler_code:
        handler_code = replace_once(
            handler_code,
            "  var profileFieldMatchCount = Number(row.profile_field_match_count || 0);\n  if (profileFieldMatchCount > 1) {",
            "  var profileFieldMatchCount = Number(row.profile_field_match_count || 0);\n  var profileClaimAction = str(row.profile_claim_action || '');\n  if (profileFieldMatchCount > 1 || profileClaimAction === 'ambiguous') {",
            "shared profile-claim action guard",
        )
        handler_code = replace_once(
            handler_code,
            "  } else if (claimStatus === 'wait') {",
            "  } else if ((!contactId && profileClaimAction === 'busy') || claimStatus === 'wait') {",
            "shared profile-claim waiter branch",
        )
        handler_code = replace_once(
            handler_code,
            "reason: 'identity_claim_wait_timeout', identity_key: str(row.identity_key || ''), identity_claim_status: claimStatus, identity_claim_owner_message_id:",
            "reason: profileClaimAction === 'busy' ? 'linkedin_profile_create_in_progress' : 'identity_claim_wait_timeout', identity_key: str(row.identity_key || ''), identity_claim_status: claimStatus, profile_claim_action: profileClaimAction, identity_claim_owner_message_id:",
            "shared profile-claim waiter error",
        )
        handler_code = replace_once(
            handler_code,
            "identity_claim_owner_message_id: str(row.identity_claim_owner_message_id || ''), ghl_conversation_id: '', ghl_message_id: '' };",
            "identity_claim_owner_message_id: str(row.identity_claim_owner_message_id || ''), profile_claim_action: profileClaimAction, profile_claim_token: str(row.profile_claim_token || ''), profile_claim_identity_key: str(row.profile_claim_identity_key || ''), ghl_conversation_id: '', ghl_message_id: '' };",
            "shared profile-claim result projection",
        )
        changed = True

    if "function extractLinkedInProfiles(contact)" not in handler_code:
        old_helper = """function extractLinkedInUrl(contact) {
  var website = lower(str(contact.website));
  if (website && website.includes('linkedin.com/in/')) return website;
  if (contact.customFields) {
    for (var i = 0; i < contact.customFields.length; i++) {
      var cf = contact.customFields[i];
      var v = lower(str(cf && cf.value));
      if (v && v.includes('linkedin.com/in/')) return v;
    }
  }
  return '';
}
"""
        new_helper = """function normalizeLinkedInProfile(value) {
  var text = lower(str(value));
  var match = text.match(/(?:https?:\\/\\/)?(?:[a-z0-9-]+\\.)?linkedin\\.com\\/in\\/([^/?#\\s,;<>]+)/i);
  if (!match) return '';
  var slug = String(match[1] || '').replace(/[.,;:!?]+$/, '').replace(/\\/+$/, '');
  try { slug = decodeURIComponent(slug); } catch (e) {}
  return slug ? 'linkedin.com/in/' + slug : '';
}

function extractLinkedInProfiles(contact) {
  var values = [contact && contact.website];
  var fields = Array.isArray(contact && contact.customFields) ? contact.customFields
    : Array.isArray(contact && contact.customFields && contact.customFields.fields) ? contact.customFields.fields
    : Array.isArray(contact && contact.customFields && contact.customFields.data) ? contact.customFields.data : [];
  for (var i = 0; i < fields.length; i++) values.push(fields[i] && (fields[i].value ?? fields[i].fieldValue ?? fields[i].field_value));
  var profiles = [];
  for (var j = 0; j < values.length; j++) {
    var text = str(values[j]);
    var matches = text.match(/(?:https?:\\/\\/)?(?:[a-z0-9-]+\\.)?linkedin\\.com\\/in\\/[^/?#\\s,;<>]+/ig) || [];
    for (var k = 0; k < matches.length; k++) {
      var normalized = normalizeLinkedInProfile(matches[k]);
      if (normalized && profiles.indexOf(normalized) < 0) profiles.push(normalized);
    }
  }
  return profiles;
}
"""
        handler_code = replace_once(handler_code, old_helper, new_helper, "all-profile-field extractor")
        changed = True

    if "var exactProfileMatches = candidates.filter" not in handler_code:
        handler_code = replace_once(
            handler_code,
            """  var expected = {
    profileUrl: lower(payload.sender_profile_url),
    providerId: lower(payload.sender_provider_id),
    displayName: lower(displayName),
  };

  var scored = candidates.map(function(contact) {""",
            """  var expected = {
    profileUrl: lower(payload.sender_profile_url),
    providerId: lower(payload.sender_provider_id),
    displayName: lower(displayName),
  };
  var expectedProfile = normalizeLinkedInProfile(expected.profileUrl);
  if (expectedProfile) {
    var exactProfileMatches = candidates.filter(function(contact) {
      return extractLinkedInProfiles(contact).indexOf(expectedProfile) >= 0;
    });
    if (exactProfileMatches.length === 1) return { id: exactProfileMatches[0].id, reason: 'exact_linkedin_profile_field_match' };
    if (exactProfileMatches.length > 1) return { id: '', reason: 'ambiguous_linkedin_profile_field_match' };
    return { id: '', reason: 'linkedin_profile_field_not_found' };
  }

  var scored = candidates.map(function(contact) {""",
            "unique exact profile resolution",
        )
        handler_code = replace_once(
            handler_code,
            "    var website = lower(str(contact.website));\n    var cfLinkedInUrl = extractLinkedInUrl(contact);\n",
            "",
            "legacy first-profile scoring removal",
        )
        handler_code = replace_once(
            handler_code,
            "    if (expected.profileUrl && (website === expected.profileUrl || cfLinkedInUrl === expected.profileUrl)) score += 100;\n    if (expected.profileUrl && (website.includes(expected.profileUrl.replace('https://www.', '').replace('https://', '')) || cfLinkedInUrl.includes(expected.profileUrl.replace('https://www.', '').replace('https://', '')))) score += 95;\n",
            "",
            "non-exact profile scoring removal",
        )
        changed = True

    if "linkedin_resolve_contact_profile_claim(" not in map_code:
        map_code = replace_once(
            map_code,
            "const retrySql = `CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue (",
            """const providerIdValue = String(providerId || '').trim();
const profileUrlValue = String(profileUrl || '').trim();
const profileMatch = profileUrlValue.match(/linkedin\\.com\\/in\\/([^/?#]+)/i);
var normalizedProfileSlug = profileMatch ? String(profileMatch[1]).toLowerCase().replace(/\\/+$/, '') : '';
try { normalizedProfileSlug = decodeURIComponent(normalizedProfileSlug); } catch (e) {}
const profileClaimAction = String(row.profile_claim_action || '');
const profileClaimToken = String(row.profile_claim_token || '');
const profileClaimIdentityKey = String(row.profile_claim_identity_key || '');
const profileContactName = String(row.sender_name || '');
const profileIndexSql = `
SELECT linkedin_resolve_contact_profile_claim(${esc(profileClaimIdentityKey)}, NULLIF(${esc(profileClaimToken)},'')::uuid, ${esc(contactId)}, ${esc(normalizedProfileSlug)}, ${esc(profileUrlValue)}, ${esc(profileContactName)}, ${esc(providerIdValue)})
WHERE ${shouldUpsert}::boolean AND ${hasContactId}::boolean AND ${esc(profileClaimAction)} = 'owner';
INSERT INTO linkedin_contact_profile_index(ghl_contact_id,normalized_profile_slug,profile_url,contact_name,linkedin_provider_ids,refreshed_at)
SELECT ${esc(contactId)}, COALESCE(NULLIF(${esc(normalizedProfileSlug)},''), NULLIF('provider:'||lower(${esc(providerIdValue)}),'provider:')),
  NULLIF(${esc(profileUrlValue)},''), NULLIF(${esc(profileContactName)},''),
  CASE WHEN NULLIF(${esc(providerIdValue)},'') IS NULL THEN '{}'::text[] ELSE ARRAY[${esc(providerIdValue)}]::text[] END, NOW()
WHERE ${shouldUpsert}::boolean AND ${hasContactId}::boolean AND ${esc(profileClaimAction)} <> 'owner'
  AND (NULLIF(${esc(normalizedProfileSlug)},'') IS NOT NULL OR NULLIF(${esc(providerIdValue)},'') IS NOT NULL)
ON CONFLICT(ghl_contact_id,normalized_profile_slug) DO UPDATE SET
  profile_url=COALESCE(EXCLUDED.profile_url,linkedin_contact_profile_index.profile_url),
  contact_name=COALESCE(EXCLUDED.contact_name,linkedin_contact_profile_index.contact_name),
  linkedin_provider_ids=ARRAY(SELECT DISTINCT unnest(linkedin_contact_profile_index.linkedin_provider_ids||EXCLUDED.linkedin_provider_ids)),
  refreshed_at=NOW();
`;

const retrySql = `CREATE TABLE IF NOT EXISTS linkedin_inbound_retry_queue (""",
            "shared profile index upsert",
        )
        map_code = replace_once(
            map_code,
            "const sqlQuery = identityClaimSql + '\\n' + retrySql + '\\n' + mapSql;",
            "const sqlQuery = identityClaimSql + '\\n' + retrySql + '\\n' + profileIndexSql + '\\n' + mapSql;",
            "profile index execution ordering",
        )
        changed = True

    if "status: 'contact_resolved'" not in handler_code:
        prefix, separator, tail = handler_code.partition("  var agencyToken = str(row.ghl_oauth_access_token);")
        if not separator:
            raise RuntimeError("Could not split contact creation from inbound GHL message posting")
        tail_start = tail.find("\ntry {")
        if tail_start < 0:
            raise RuntimeError("Could not locate handler error boundary after message posting")
        handler_code = prefix + """  var agencyToken = str(row.ghl_oauth_access_token);
  if (!agencyToken) return { ...base, status: 'error', reason: 'missing_oauth_token', _oauth_access_token: '' };
  return { ...base, status: 'contact_resolved', _oauth_access_token: agencyToken };
}
""" + tail[tail_start:]
        changed = True

    by_name = {n.get("name"): n for n in nodes}
    index_builder = by_name.get("Build LinkedIn Profile Index SQL") or {
        "id": "linkedin-profile-index-builder", "name": "Build LinkedIn Profile Index SQL", "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [200, 0], "parameters": {"mode": "runOnceForAllItems", "jsCode": PROFILE_INDEX_SQL_CODE},
    }
    index_builder["parameters"]["jsCode"] = PROFILE_INDEX_SQL_CODE
    index_persist = by_name.get("Persist LinkedIn Profile Index") or {
        "id": "linkedin-profile-index-persist", "name": "Persist LinkedIn Profile Index", "type": "n8n-nodes-base.postgres", "typeVersion": 2.6,
        "position": [450, 0], "parameters": {"operation": "executeQuery", "query": "={{ $json.query }}", "options": {"queryBatching": "independently", "queryReplacement": "={{ $json.values }}"}},
        "credentials": {"postgres": {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}}, "alwaysOutputData": True,
    }
    confirm_index = by_name.get("Confirm LinkedIn Profile Index") or {
        "id": "linkedin-profile-index-confirm", "name": "Confirm LinkedIn Profile Index", "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [700, 0], "parameters": {"mode": "runOnceForAllItems", "jsCode": ""},
    }
    confirm_index["parameters"]["jsCode"] = r'''const result=$input.first()?.json||{},base=$('Create LinkedIn Contact and Add Inbound Message').first()?.json||{};
if(!base.should_upsert||!base.ghl_contact_id)return [{json:{...base,index_saved:false}}];
if(result.index_saved!==true)return [{json:{...base,should_upsert:false,index_saved:false,status:'error',reason:'linkedin_profile_index_write_failed',_oauth_access_token:undefined}}];
return [{json:{...base,index_saved:true}}];'''
    send_inbound = by_name.get("Send LinkedIn Inbound Message") or {
        "id": "linkedin-send-inbound", "name": "Send LinkedIn Inbound Message", "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [950, 0], "parameters": {"mode": "runOnceForAllItems", "jsCode": SEND_INBOUND_CODE},
    }
    send_inbound["parameters"]["jsCode"] = SEND_INBOUND_CODE
    additions = [index_builder, index_persist, confirm_index, send_inbound]
    for node in additions:
        if not any(n.get("name") == node["name"] for n in nodes):
            nodes.append(node)
            changed = True
    if nodes != workflow.get("nodes", []):
        changed = True
    workflow["nodes"] = nodes
    connections = workflow.get("connections", {})
    original_connections = json.loads(json.dumps(connections))
    connections["Create LinkedIn Contact and Add Inbound Message"] = {"main": [[{"node": "Build LinkedIn Profile Index SQL", "type": "main", "index": 0}]]}
    connections["Build LinkedIn Profile Index SQL"] = {"main": [[{"node": "Persist LinkedIn Profile Index", "type": "main", "index": 0}]]}
    connections["Persist LinkedIn Profile Index"] = {"main": [[{"node": "Confirm LinkedIn Profile Index", "type": "main", "index": 0}]]}
    connections["Confirm LinkedIn Profile Index"] = {"main": [[{"node": "Send LinkedIn Inbound Message", "type": "main", "index": 0}]]}
    connections["Send LinkedIn Inbound Message"] = {"main": [[{"node": "Build Upsert Map SQL", "type": "main", "index": 0}]]}
    if connections != original_connections:
        changed = True
    workflow["connections"] = connections

    if changed:
        lookup_node["parameters"]["jsCode"] = lookup_code
        handler_node["parameters"]["jsCode"] = handler_code
        map_node["parameters"]["jsCode"] = map_code
    settings = workflow.setdefault("settings", {})
    safe_execution_settings = {
        "saveDataErrorExecution": "none",
        "saveDataSuccessExecution": "none",
        "saveManualExecutions": False,
        "saveExecutionProgress": False,
    }
    if any(settings.get(key) != value for key, value in safe_execution_settings.items()):
        settings.update(safe_execution_settings)
        changed = True
    return workflow, changed


workflow = api(f"/workflows/{WORKFLOW_ID}")
workflow, changed = patch_workflow(workflow)
if changed:
    payload = {key: workflow[key] for key in ("name", "nodes", "connections", "settings") if key in workflow}
    if "staticData" in workflow:
        payload["staticData"] = workflow["staticData"]
    api(f"/workflows/{WORKFLOW_ID}", "PUT", payload)

readback = api(f"/workflows/{WORKFLOW_ID}")
lookup = next(n for n in readback["nodes"] if n.get("name") == "Build Lookup Map SQL")
handler = next(n for n in readback["nodes"] if n.get("name") == "Create LinkedIn Contact and Add Inbound Message")
index_sql = next(n for n in readback["nodes"] if n.get("name") == "Build LinkedIn Profile Index SQL")
send_node = next(n for n in readback["nodes"] if n.get("name") == "Send LinkedIn Inbound Message")
lookup_code = lookup["parameters"]["jsCode"]
handler_code = handler["parameters"]["jsCode"]
index_code = index_sql["parameters"]["jsCode"]
send_code = send_node["parameters"]["jsCode"]
print(json.dumps({
    "id": readback.get("id"),
    "versionId": readback.get("versionId"),
    "active": readback.get("active"),
    "versionMatches": readback.get("versionId") == readback.get("activeVersionId"),
    "profileFieldLookupPresent": "profile_field_candidates AS (" in lookup_code,
    "sharedRaceClaimPresent": "linkedin_claim_contact_profile" in lookup_code,
    "ambiguityFailsClosed": "ambiguous_linkedin_profile_field_match" in handler_code,
    "createContactFallbackPreserved": "POST', url: GHL_BASE + '/contacts/'" in handler_code,
    "strictProfileMatchBeforeFallback": "var exactProfileMatches = candidates.filter" in handler_code,
    "contactIndexedBeforeGhlMessage": "linkedin_resolve_contact_profile_claim" in index_code and "Confirm LinkedIn Profile Index" in send_code,
    "changedNow": changed,
}))
