"""Read-only cohort and provider contract audit; never creates invites or chats."""
import json
import time

import requests
from build_vertical_outreach import ACCOUNT, REGISTRY, V2_ACCOUNT, seed_sql
from vertical_outreach_ops import ENV, Database


def main():
    with Database() as db:
        cte=seed_sql().split('\nINSERT INTO lt_li_vertical_queue')[0]
        print('Snapshot cohort reconciliation:',json.dumps(db.rows(cte+"""
SELECT r.vertical,
 (SELECT count(*) FROM latest l WHERE l.c->'tags' ? r.tag AND EXISTS(SELECT 1 FROM jsonb_array_elements(l.c->'customFields') f WHERE f->>'id'='ODs8fBt5te5HEfSJ91pY' AND f->>'value'=r.vertical)) AS campaign_contacts,
 (SELECT count(DISTINCT contact_id) FROM cohort c WHERE c.vertical=r.vertical) AS with_index,
 (SELECT count(*) FROM eligible e WHERE e.vertical=r.vertical) AS unique_unheld_queue,
 (SELECT count(DISTINCT contact_id) FROM cohort c WHERE c.vertical=r.vertical AND (identities>1 OR contact_rows>1)) AS ambiguous_within_cohort
FROM registry r ORDER BY r.vertical_index
"""),indent=2))
        rows=db.rows("SELECT DISTINCT ON (vertical_index) contact_id,vertical,profile_slug FROM lt_li_vertical_queue ORDER BY vertical_index,contact_id")
        print('Database guards:',json.dumps(db.rows("SELECT tgname,count(*) FROM pg_trigger WHERE tgname IN ('lt_li_shared_pacing','lt_invitation_withdrawal_hold') GROUP BY 1")))
        print('Withdrawals:',json.dumps(db.rows('SELECT withdraw_status,dispatcher_hold,count(*) FROM linkedin_invitation_withdrawals GROUP BY 1,2')))
    gh={'Authorization':'Bearer '+ENV['GHL_PIT'],'Version':'2021-07-28','User-Agent':'Mozilla/5.0'}
    up={'X-API-KEY':ENV['UNIPILE_TOKEN']}
    for row in rows:
        r=requests.get('https://services.leadconnectorhq.com/contacts/'+row['contact_id'],headers=gh,timeout=30)
        r.raise_for_status();contact=r.json()['contact']
        vertical=next((f.get('value') for f in contact.get('customFields',[]) if f['id']=='ODs8fBt5te5HEfSJ91pY'),None)
        tag='lt_campaign_'+REGISTRY['messages'][row['vertical']]['slug']+'_brands_oct_2026_enroll'
        conv=requests.get('https://services.leadconnectorhq.com/conversations/search',headers=gh,
            params={'locationId':contact['locationId'],'contactId':row['contact_id'],'lastMessageDirection':'inbound','status':'all','limit':1},timeout=30)
        p=requests.get(ENV['UNIPILE_API_BASE_URL'].rstrip('/')+'/users/'+requests.utils.quote(row['profile_slug']),
                       params={'account_id':ACCOUNT},headers=up,timeout=30)
        body=p.json() if p.ok else {}
        print(json.dumps({'vertical':row['vertical'],'live_vertical_matches':vertical==row['vertical'],
                          'live_campaign_tag':tag in contact.get('tags',[]),'conversation_http':conv.status_code,
                          'conversation_array':isinstance(conv.json().get('conversations'),list) if conv.ok else False,
                          'classic_profile_http':p.status_code,'provider_id_present':bool(body.get('provider_id')),
                          'provider_first_name_present':bool(body.get('first_name')),
                          'network_distance':body.get('network_distance'),
                          'slug_matches':str(body.get('public_identifier','')).lower()==row['profile_slug']}))
        time.sleep(.5)
    r=requests.get('https://api.unipile.com/v2/accounts/'+V2_ACCOUNT,
                   headers={'X-API-KEY':ENV['UNIPILE_v2_MIGRATION_SERVICE_API_KEY']},timeout=30)
    r.raise_for_status()
    print('Sales Navigator:',json.dumps(r.json().get('metadata',{}).get('products_connection_status',{})))


if __name__=='__main__':main()
