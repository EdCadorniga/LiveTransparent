// Shared source assembled into the two n8n-lt Code nodes by build_vertical_outreach.py.
// Provider mutations are single-attempt. A durable intent always precedes a send.
function asciiField(value, fallback = '') {
  let s = String(value || '').trim();
  if (!s) return fallback;
  if (/[\uFFFD\u00C2\u00C3\u0393\u20AC]/.test(s)) throw new Error('suspect_personalization_encoding');
  s = s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[\u2018\u2019']/g, '').replace(/[\u2013\u2014]/g, '-')
    .replace(/\u00A0/g, ' ').replace(/\s+/g, ' ');
  if (/[^\x20-\x7E]/.test(s) || /[{}<>\\]/.test(s)) throw new Error('unsafe_personalization');
  return s;
}
function renderMessage(template, firstName, company, bookingUrl) {
  const first = asciiField(firstName);
  if (!first || first.length > 50) throw new Error('provider_first_name_required');
  const text = template.split('{first_name}').join(first)
    .split('{company}').join(asciiField(company, 'your team'))
    .split('{booking_url}').join(bookingUrl).trim();
  if (!text || /[^\x20-\x7E\n]/.test(text) || /['{}<>\\]/.test(text))
    throw new Error('outbound_text_rejected');
  if (text.includes('  ') || /\n{3}/.test(text)) throw new Error('outbound_spacing_rejected');
  return text;
}
function field(contact, id) {
  return (contact.customFields || []).find(f => f.id === id)?.value || '';
}
function profileSlug(value) {
  const v = String(value || '').trim();
  const match = v.match(/^(?:https?:[/][/])?(?:www[.])?linkedin[.]com[/]in[/]([^/?#]+)[/]?(?:[?#].*)?$/i);
  return match ? decodeURIComponent(match[1]).toLowerCase() : '';
}
function relationship(profile) {
  return profile.is_relationship === true || ['FIRST_DEGREE', 'DISTANCE_1'].includes(profile.network_distance || profile.specifics?.network_distance);
}
function pacificOpen(now = new Date()) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles',
    weekday: 'short', hour: '2-digit', hourCycle: 'h23' }).formatToParts(now).map(p => [p.type, p.value]));
  return !['Sat','Sun'].includes(parts.weekday) && Number(parts.hour) >= 9 && Number(parts.hour) < 17;
}
function dueStep(q, now = new Date()) {
  const accepted = Date.parse(q.accepted_at);
  if (!Number.isFinite(accepted) || q.status !== 'connected') return 0;
  if (q.dm_step === 0 && now.getTime() >= accepted + 9 * 86400000) return 1;
  if (q.dm_step === 1 && q.dm1_sent_at && now.getTime() >= Math.max(accepted + 17 * 86400000,
      Date.parse(q.dm1_sent_at) + 8 * 86400000)) return 2;
  return 0;
}
function contactBlock(contact, vertical, slug, invite = false) {
  if (!contact || contact.locationId !== 'Zwz4relUXVPxx8uohnjV') return 'contact_location_mismatch';
  if (field(contact, 'ODs8fBt5te5HEfSJ91pY') !== vertical) return 'vertical_changed';
  const tags = (contact.tags || []).map(t => String(t).toLowerCase());
  const required = 'lt_campaign_' + slug + '_brands_oct_2026_enroll';
  if (!tags.includes(required)) return 'not_in_october_cohort';
  const blocked = ['do not contact','do not nurture','stop_linkedin_dms','linkedin_dm_sequence_completed',
    'partner_do_not_contact','partner_replied','simpletext_stop','simpletext_replied','dan_seq_replied_or_booked'];
  if (contact.dnd === true || blocked.some(t => tags.includes(t)) ||
      tags.some(t => /^lt_campaign_.+_(replied|suppressed)$/.test(t))) return 'suppressed';
  return '';
}

// RUNTIME_START -- tests load only the pure helpers above this marker.
const cfg = $('Config').first().json;
const {Client} = require('pg');
const db = new Client({host:'postgres',port:5432,database:'postgres',user:'postgres',
  password:cfg.pgPassword,connectionTimeoutMillis:10000,statement_timeout:90000});
const out = {mode:MODE, sent:0,accepted:0,checked:0,skipped:0,held:0,results:[]};
let locked = false, pendingAttempt = null;
let inboxChats = null;
const gha = {Authorization:'Bearer '+cfg.ghlApiKey,Version:'2021-07-28',Accept:'application/json','Content-Type':'application/json'};
const classic = {'X-API-KEY':cfg.unipileApiKey,Accept:'application/json','Content-Type':'application/json'};
const v2 = {'X-API-KEY':cfg.unipileV2ApiKey,Accept:'application/json','Content-Type':'application/json'};
try {
  await db.connect();
  locked = (await db.query("SELECT pg_try_advisory_lock(hashtextextended($1,0)) AS ok",['lt_li_worker:'+cfg.accountId])).rows[0].ok;
  if (!locked) return [{json:{...out,reason:'another_worker_running'}}];
  const control = (await db.query('SELECT * FROM lt_li_vertical_control WHERE account_id=$1',[cfg.accountId])).rows[0];
  if (cfg.verifyOnly === true) {
    if ($('Webhook').first().json.headers?.['x-lt-verify'] !== cfg.verifySecret)
      return [{json:{ok:false,reason:'unauthorized'}}];
    const account = await this.helpers.httpRequest({method:'GET',url:cfg.v2Base+'/accounts/'+cfg.v2AccountId,headers:v2,json:true,timeout:15000});
    const counts=(await db.query('SELECT vertical,status,count(*)::int AS n FROM lt_li_vertical_queue GROUP BY 1,2 ORDER BY 1,2')).rows;
    return [{json:{ok:true,verify_only:true,provider_writes:0,products:account.metadata?.products_connection_status,counts}}];
  }
  if (!control || !(MODE === 'invite' ? control.enabled : control.dm_enabled))
    return [{json:{...out,reason:'disabled_by_control'}}];
  // Readiness is checked even outside the sending window; disconnected products never trigger a send.
  const account = await this.helpers.httpRequest({method:'GET',url:cfg.v2Base+'/accounts/'+cfg.v2AccountId,headers:v2,json:true,timeout:15000});
  const products = account.metadata?.products_connection_status || {};
  if (products.classic !== 'running' || products.sales_navigator !== 'running')
    return [{json:{...out,reason:'account_not_ready',products}}];
  if (!pacificOpen()) return [{json:{...out,reason:'outside_pacific_business_hours'}}];
  if (MODE === 'invite') {
    // Refresh from the latest report snapshot only. Every individual contact is re-read from GHL before use.
    await db.query(SEED_SQL);
  }
  // Never clear a stale intent or blindly retry a request after a crash/timeout.
  if ((await db.query("SELECT 1 FROM lt_li_outbound_attempts WHERE account_id=$1 AND status IN ('intent','uncertain') LIMIT 1",[cfg.accountId])).rowCount)
    return [{json:{...out,reason:'unresolved_provider_write_requires_review'}}];
  let candidates;
  if (MODE === 'invite') {
    candidates = (await db.query(`SELECT q.* FROM lt_li_vertical_queue q
      WHERE q.account_id=$1 AND q.status='ready'
      ORDER BY ((q.vertical_index-$2+8)%8),q.enrolled_at,q.contact_id LIMIT 24`,[cfg.accountId,control.next_vertical])).rows;
  } else {
    candidates = (await db.query(`SELECT * FROM lt_li_vertical_queue WHERE account_id=$1
      AND status IN ('requested','connected') AND (last_checked_at IS NULL OR last_checked_at<now()-interval '6 hours'
        OR (status='connected' AND dm_step=0 AND accepted_at<=now()-interval '9 days')
        OR (status='connected' AND dm_step=1 AND accepted_at<=now()-interval '17 days' AND dm1_sent_at<=now()-interval '8 days'))
      ORDER BY last_checked_at NULLS FIRST,contact_id LIMIT 20`,[cfg.accountId])).rows;
  }
  for (const q of candidates) {
    let shouldSend = false;
    try {
      out.checked++;
      const registry = MESSAGES.messages[q.vertical];
      if (!registry) throw new Error('vertical_copy_missing');
      const raw = await this.helpers.httpRequest({method:'GET',url:cfg.ghlBase+'/contacts/'+encodeURIComponent(q.contact_id),headers:gha,json:true,timeout:15000});
      const c = raw.contact;
      let block = contactBlock(c,q.vertical,registry.slug,MODE==='invite');
      const index = (await db.query(`SELECT normalized_profile_slug,linkedin_provider_ids FROM linkedin_contact_profile_index WHERE ghl_contact_id=$1`,[q.contact_id])).rows;
      if (index.length !== 1 || index[0].normalized_profile_slug !== q.profile_slug) block='identity_changed';
      if ((await db.query(`SELECT 1 FROM linkedin_contact_profile_index WHERE normalized_profile_slug=$1 AND ghl_contact_id<>$2 LIMIT 1`,[q.profile_slug,q.contact_id])).rowCount)
        block='duplicate_profile';
      if ((await db.query(`SELECT 1 FROM linkedin_invitation_withdrawals WHERE dispatcher_hold AND
        (ghl_contact_id=$1 OR candidate_contact_ids ? $1 OR lower(invited_user_public_id)=$2) LIMIT 1`,[q.contact_id,q.profile_slug])).rowCount)
        block='withdrawal_hold';
      const states = (await db.query(`SELECT * FROM linkedin_connection_state WHERE unipile_account_id=$1 AND
        (ghl_contact_id=$2 OR lower(linkedin_public_identifier)=$3 OR (NULLIF($4,'') IS NOT NULL AND linkedin_provider_id=$4))`,
        [cfg.accountId,q.contact_id,q.profile_slug,q.provider_id||''])).rows;
      if (states.some(s=>s.connection_status==='completed'||s.payload_json?.dm_conversation_status==='active'||s.payload_json?.reply_detected===true)) block='shared_reply_or_terminal';
      if ((await db.query(`SELECT 1 FROM linkedin_activity_events WHERE (ghl_contact_id=$1 OR linkedin_public_identifier=$2)
        AND event_type IN ('reply_received','dm_sent') AND coalesce(source_workflow_name,'') NOT LIKE 'LT - Vertical LinkedIn%' LIMIT 1`,[q.contact_id,q.profile_slug])).rowCount)
        block='prior_conversation_or_sequence';
      if ((await db.query(`SELECT 1 FROM sales_navigator_v2_message_events WHERE ghl_contact_id=$1
        AND direction='inbound' LIMIT 1`,[q.contact_id])).rowCount) block='salesnav_reply';
      if (block) {
        await db.query("UPDATE lt_li_vertical_queue SET status='suppressed',reason=$2,updated_at=now() WHERE contact_id=$1",[q.contact_id,block]);
        out.skipped++;out.results.push({contact_id:q.contact_id,status:block});continue;
      }
      // An empty, well-formed response is required; lookup failures never mean no reply.
      const conversations = await this.helpers.httpRequest({method:'GET',url:cfg.ghlBase+'/conversations/search',
        qs:{locationId:cfg.locationId,contactId:q.contact_id,lastMessageDirection:'inbound',status:'all',limit:1},headers:gha,json:true,timeout:15000});
      if (!Array.isArray(conversations.conversations)) throw new Error('ghl_reply_shape_unverified');
      if (conversations.conversations.length) {
        await db.query("UPDATE lt_li_vertical_queue SET status='suppressed',reason='inbound_reply',updated_at=now() WHERE contact_id=$1",[q.contact_id]);
        out.skipped++;continue;
      }
      const p = await this.helpers.httpRequest({method:'GET',url:cfg.classicBase+'/users/'+encodeURIComponent(q.profile_slug),
        qs:{account_id:cfg.accountId},headers:classic,json:true,timeout:20000});
      const pid = String(p.provider_id || '');
      if (!pid || (p.public_identifier && p.public_identifier.toLowerCase()!==q.profile_slug)) throw new Error('provider_identity_mismatch');
      if (q.provider_id && pid!==q.provider_id) throw new Error('provider_identity_changed');
      if (index[0].linkedin_provider_ids?.length && !index[0].linkedin_provider_ids.includes(pid)) throw new Error('provider_not_in_contact_index');
      if ((await db.query(`SELECT 1 FROM linkedin_contact_profile_index WHERE ghl_contact_id<>$1 AND $2=ANY(linkedin_provider_ids) LIMIT 1`,[q.contact_id,pid])).rowCount)
        throw new Error('duplicate_provider_identity');
      await db.query('UPDATE lt_li_vertical_queue SET provider_id=$2,last_checked_at=now(),updated_at=now() WHERE contact_id=$1',[q.contact_id,pid]);
      if (relationship(p)) {
        if (!q.accepted_at) {
          // Existing connections begin a fresh nine-day wait. New accepts use their verified observation time.
          const anchor = states.filter(s=>s.connected_at && Date.parse(s.connected_at)>=Date.parse(q.enrolled_at))
            .map(s=>new Date(s.connected_at)).sort((a,b)=>a-b)[0] || new Date();
          await db.query(`UPDATE lt_li_vertical_queue SET status='connected',accepted_at=$2,acceptance_basis='provider_first_degree',updated_at=now() WHERE contact_id=$1 AND accepted_at IS NULL`,[q.contact_id,anchor]);
          await db.query(`INSERT INTO linkedin_activity_events(event_key,event_type,event_at,ghl_contact_id,location_id,unipile_account_id,linkedin_provider_id,linkedin_public_identifier,campaign_key,channel,source_workflow_name,status)
            VALUES($1,'connection_accepted',$2,$3,$4,$5,$6,$7,$8,'linkedin',$9,'accepted') ON CONFLICT(event_key) DO NOTHING`,
            ['connection_accepted:'+q.contact_id+':'+pid,anchor,q.contact_id,cfg.locationId,cfg.accountId,pid,q.profile_slug,registry.slug+'_oct_2026',cfg.workflowName]);
          out.accepted++;q.accepted_at=anchor;q.status='connected';
        }
        if (MODE==='invite') {out.skipped++;continue;}
      } else if (MODE==='dm') {out.skipped++;continue;}
      const booking = cfg.bookingBase+'?utm_source='+registry.slug+'sequence&utm_medium=linkedin&utm_campaign=vertical_oct_2026&utm_content=dm2';
      if (MODE==='invite') {
        if ((c.tags||[]).includes('linkedin_connection_requested')||p.invitation?.status==='SENT'||p.invitation?.status==='PENDING'||p.has_pending_invitation===true||
            states.some(s=>s.request_sent_at||['requested','requested_pending'].includes(s.connection_status))) {
          await db.query("UPDATE lt_li_vertical_queue SET status='requested',reason='existing_request',updated_at=now() WHERE contact_id=$1",[q.contact_id]);
          out.skipped++;continue;
        }
        const text=renderMessage(registry.invite,p.first_name,c.companyName,booking);
        if(text.length>300) throw new Error('invite_note_too_long');
        // Check the complete provider pending list so out-of-band/manual invitations are also excluded.
        let cursor='',seen=new Set(),pending=false,finished=false;
        for(let page=0;page<40;page++) {
          const list=await this.helpers.httpRequest({method:'GET',url:cfg.classicBase+'/users/invite/sent',
            qs:{account_id:cfg.accountId,limit:100,...(cursor?{cursor}:{})},headers:classic,json:true,timeout:15000});
          if(!Array.isArray(list.items)) throw new Error('pending_invites_shape_unverified');
          for(const i of list.items) {
            if(i.invited_user_id===pid||String(i.invited_user_public_id||'').toLowerCase()===q.profile_slug) pending=true;
            // External invitations today/hour consume slots too; duplicate provider IDs do not inflate the cap.
            const dt=new Date(i.parsed_datetime||i.date);
            if(Number.isFinite(dt.getTime())&&Date.now()-dt.getTime()<48*3600000) {
              await db.query(`INSERT INTO lt_li_outbound_attempts(account_id,identity_key,contact_id,kind,source,status,reserved_at,sent_at,provider_result_id)
                VALUES($1,$2,'external','invite','provider_readback','sent',$3,$3,$4) ON CONFLICT DO NOTHING`,
                [cfg.accountId,i.invited_user_id||String(i.invited_user_public_id).toLowerCase(),dt,String(i.id)]);
            }
          }
          if(!list.cursor){finished=true;break;}
          if(seen.has(list.cursor))throw new Error('pending_invites_cursor_stalled');
          seen.add(list.cursor);cursor=list.cursor;
        }
        if(!finished)throw new Error('pending_invites_incomplete');
        if(pending){await db.query("UPDATE lt_li_vertical_queue SET status='requested',reason='provider_pending',updated_at=now() WHERE contact_id=$1",[q.contact_id]);out.skipped++;continue;}
        const reservation=(await db.query('SELECT lt_li_reserve_invite($1,$2,$3,$4) AS id',[cfg.accountId,pid,q.contact_id,cfg.workflowName])).rows[0].id;
        if(!reservation){out.results.push({status:'account_limit_or_prior_attempt'});break;}
        pendingAttempt=reservation;shouldSend=true;
        await db.query('UPDATE lt_li_outbound_attempts SET message_text=$2,message_sha256=$3,provider_id=$4 WHERE id=$1',
          [reservation,text,require('crypto').createHash('sha256').update(text,'utf8').digest('hex'),pid]);
        // Exactly one POST: no transport or application retry is permitted.
        const sent=await this.helpers.httpRequest({method:'POST',url:cfg.classicBase+'/users/invite',headers:classic,
          body:{account_id:cfg.accountId,provider_id:pid,message:text},json:true,timeout:20000});
        const iid=sent.invitation_id||sent.id;
        if(typeof iid!=='string'||!iid)throw new Error('invite_result_id_missing');
        await db.query('BEGIN');
        await db.query("UPDATE lt_li_outbound_attempts SET status='sent',sent_at=now(),provider_result_id=$2 WHERE id=$1",[reservation,iid]);
        await db.query("UPDATE lt_li_vertical_queue SET status='requested',invite_sent_at=now(),reason=NULL,updated_at=now() WHERE contact_id=$1",[q.contact_id]);
        await db.query('UPDATE lt_li_vertical_control SET next_vertical=$2,updated_at=now() WHERE account_id=$1',[cfg.accountId,(q.vertical_index+1)%8]);
        await db.query(`INSERT INTO linkedin_connection_state(ghl_contact_id,location_id,unipile_account_id,linkedin_profile_url,linkedin_public_identifier,linkedin_provider_id,connection_status,request_sent_at,request_message,payload_json,metadata_json)
          VALUES($1,$2,$3,$4,$5,$6,'requested',now(),$7,'{}'::jsonb,jsonb_build_object('source','vertical_oct_2026'))
          ON CONFLICT(ghl_contact_id) DO UPDATE SET request_sent_at=now(),connection_status=CASE WHEN linkedin_connection_state.connection_status IN ('connected','completed') THEN linkedin_connection_state.connection_status ELSE 'requested' END,
          linkedin_provider_id=excluded.linkedin_provider_id,request_message=excluded.request_message,updated_at=now()`,
          [q.contact_id,cfg.locationId,cfg.accountId,'https://www.linkedin.com/in/'+q.profile_slug,q.profile_slug,pid,text]);
        await db.query(`INSERT INTO linkedin_activity_events(event_key,event_type,event_at,ghl_contact_id,location_id,unipile_account_id,linkedin_provider_id,linkedin_public_identifier,campaign_key,channel,source_workflow_name,provider_event_id,status)
          VALUES($1,'connection_request_sent',now(),$2,$3,$4,$5,$6,$7,'linkedin',$8,$9,'sent') ON CONFLICT(event_key) DO NOTHING`,
          ['vertical:invite:'+iid,q.contact_id,cfg.locationId,cfg.accountId,pid,q.profile_slug,registry.slug+'_oct_2026',cfg.workflowName,iid]);
        await db.query('COMMIT');pendingAttempt=null;out.sent++;
        out.results.push({contact_id:q.contact_id,vertical:q.vertical,status:'invite_sent',provider_result_id:iid});
        // One invitation per execution makes the persisted round-robin cursor authoritative.
        break;
      } else {
        const step=dueStep(q);
        if(!step){out.skipped++;continue;}
        // Validate the Sales Navigator identity independently of the Classic provider ID.
        const sp=await this.helpers.httpRequest({method:'GET',url:cfg.v2Base+'/'+cfg.v2AccountId+'/users/'+encodeURIComponent(q.profile_slug),
          qs:{variant:'linkedin_sales_navigator'},headers:v2,json:true,timeout:20000});
        const s=sp.data||sp;
        const sid=String(s.id||s.provider_id||'');
        if(!sid||!relationship(s)||String(s.public_identifier||'').toLowerCase()!==q.profile_slug)
          throw new Error('salesnav_first_degree_unverified');
        const text=renderMessage(registry['dm'+step],p.first_name,c.companyName,booking);
        const maps=(await db.query('SELECT * FROM sales_navigator_v2_conversation_map WHERE unipile_account_id=$1 AND ghl_contact_id=$2',[cfg.v2AccountId,q.contact_id])).rows;
        if(maps.length>1)throw new Error('ambiguous_salesnav_chat');
        let chat=q.chat_id||maps[0]?.unipile_chat_id||'';
        // List the recipient chats directly; do not infer no prior conversation from a missing local map.
        if(inboxChats===null) {
          inboxChats=[];let cursor='',seen=new Set(),complete=false;
          for(let page=0;page<40;page++) {
            const chats=await this.helpers.httpRequest({method:'GET',url:cfg.v2Base+'/'+cfg.v2AccountId+'/inboxes/SALES_NAVIGATOR_PRIMARY/chats',
              qs:{limit:100,...(cursor?{cursor}:{})},headers:v2,json:true,timeout:15000});
            if(!Array.isArray(chats.data))throw new Error('salesnav_chat_list_shape_unverified');
            inboxChats.push(...chats.data);
            if(!chats.next_cursor){complete=true;break;}
            if(seen.has(chats.next_cursor))throw new Error('salesnav_chat_cursor_stalled');
            seen.add(chats.next_cursor);cursor=chats.next_cursor;
          }
          if(!complete)throw new Error('salesnav_chat_list_incomplete');
        }
        const sn=inboxChats.filter(x=>x.user_id===sid&&x.is_1to1===true);
        if(sn.length>1)throw new Error('multiple_salesnav_threads');
        if(sn.length)chat=sn[0].id;
        if(chat) {
          const history=await this.helpers.httpRequest({method:'GET',url:cfg.v2Base+'/'+cfg.v2AccountId+'/chats/'+encodeURIComponent(chat)+'/messages',
            qs:{limit:100},headers:v2,json:true,timeout:15000});
          if(!Array.isArray(history.data)||history.next_cursor)throw new Error('salesnav_history_incomplete');
          if(history.data.some(m=>m.is_sender===false)) {
            await db.query("UPDATE lt_li_vertical_queue SET status='suppressed',reason='salesnav_inbound',updated_at=now() WHERE contact_id=$1",[q.contact_id]);out.skipped++;continue;
          }
          if(step===1&&history.data.some(m=>m.is_sender===true))throw new Error('existing_outbound_conversation');
        }
        const attempt=(await db.query(`INSERT INTO lt_li_outbound_attempts(account_id,identity_key,contact_id,kind,source,message_text,message_sha256,provider_id)
          VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT DO NOTHING RETURNING id`,
          [cfg.accountId,pid,q.contact_id,'dm'+step,cfg.workflowName,text,require('crypto').createHash('sha256').update(text).digest('hex'),sid])).rows[0];
        if(!attempt){out.skipped++;continue;}
        pendingAttempt=attempt.id;shouldSend=true;
        const sendPath=chat?'/'+cfg.v2AccountId+'/chats/'+encodeURIComponent(chat)+'/messages/send':
          '/'+cfg.v2AccountId+'/inboxes/SALES_NAVIGATOR_PRIMARY/chats/send';
        const sent=await this.helpers.httpRequest({method:'POST',url:cfg.v2Base+sendPath,headers:v2,
          body:chat?{text}:{text,users_ids:sid},json:true,timeout:20000});
        const mid=sent.message_id||sent.message?.id;chat=String(sent.chat_id||sent.chat?.id||chat);
        if(typeof mid!=='string'||!mid||!chat)throw new Error('dm_result_identity_missing');
        await db.query('BEGIN');
        await db.query("UPDATE lt_li_outbound_attempts SET status='sent',sent_at=now(),provider_result_id=$2 WHERE id=$1",[attempt.id,mid]);
        await db.query(`UPDATE lt_li_vertical_queue SET dm_step=$2,status=CASE WHEN $2=2 THEN 'completed' ELSE 'connected' END,
          dm1_sent_at=CASE WHEN $2=1 THEN now() ELSE dm1_sent_at END,dm2_sent_at=CASE WHEN $2=2 THEN now() ELSE dm2_sent_at END,
          chat_id=$3,salesnav_provider_id=$4,updated_at=now() WHERE contact_id=$1`,[q.contact_id,step,chat,sid]);
        await db.query(`INSERT INTO sales_navigator_v2_conversation_map(unipile_account_id,provider_profile_id,unipile_chat_id,ghl_contact_id)
          VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING`,[cfg.v2AccountId,sid,chat,q.contact_id]);
        await db.query(`INSERT INTO linkedin_activity_events(event_key,event_type,event_at,ghl_contact_id,location_id,unipile_account_id,linkedin_provider_id,linkedin_public_identifier,campaign_key,channel,source_workflow_name,message_id,chat_id,sequence_step,status)
          VALUES($1,'dm_sent',now(),$2,$3,$4,$5,$6,$7,'linkedin',$8,$9,$10,$11,'sent') ON CONFLICT(event_key) DO NOTHING`,
          ['vertical:dm:'+mid,q.contact_id,cfg.locationId,cfg.v2AccountId,sid,q.profile_slug,registry.slug+'_oct_2026',cfg.workflowName,mid,chat,step]);
        await db.query('COMMIT');pendingAttempt=null;out.sent++;
        out.results.push({contact_id:q.contact_id,vertical:q.vertical,status:'dm'+step+'_sent',provider_result_id:mid});
        if(out.sent>=5)break;
      }
    } catch(error) {
      await db.query('ROLLBACK').catch(()=>{});
      const safe=/^[a-z0-9_]+$/.test(error.message||'')?error.message:'external_lookup_or_write_failed';
      if(pendingAttempt) {
        await db.query("UPDATE lt_li_outbound_attempts SET status='uncertain',error_code=$2 WHERE id=$1",[pendingAttempt,safe]);
        await db.query("UPDATE lt_li_vertical_control SET enabled=false,dm_enabled=false,stopped_reason='uncertain_provider_write',updated_at=now() WHERE account_id=$1",[cfg.accountId]);
      }
      // Transient read failures postpone one contact; malformed identity/copy is held for review.
      await db.query("UPDATE lt_li_vertical_queue SET status=CASE WHEN $2 THEN 'held' ELSE status END,reason=$3,last_checked_at=now(),updated_at=now() WHERE contact_id=$1",[q.contact_id,shouldSend||safe!=='external_lookup_or_write_failed',safe]);
      out.held++;out.results.push({contact_id:q.contact_id,status:safe});
      if(pendingAttempt)break;
    }
  }
  return [{json:out}];
} catch(error) {
  // Driver errors can include secrets; expose only an operational code.
  throw new Error('vertical_linkedin_runtime_failed');
} finally {
  if(locked)await db.query('SELECT pg_advisory_unlock(hashtextextended($1,0))',['lt_li_worker:'+cfg.accountId]).catch(()=>{});
  await db.end().catch(()=>{});
}
