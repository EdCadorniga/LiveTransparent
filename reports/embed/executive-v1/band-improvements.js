(function () {
  "use strict";
  var evidence = null, latest = null;
  function esc(value) { var el = document.createElement("span"); el.textContent = String(value == null ? "" : value); return el.innerHTML; }
  function num(value) { return value == null || value === "" || !Number.isFinite(Number(value)) ? "—" : Number(value).toLocaleString("en-US"); }
  function sourceLabel(row) {
    var source = String(row.source || "").trim(), medium = String(row.medium || "").trim(), text = (source + " " + medium).toLowerCase();
    if (!source || /^(unknown|unattributed|unclassified|none|null)(\b|$)/i.test(source)) return "Unknown / Unattributed";
    if (/linkedin|unipile/i.test(source)) return "LinkedIn";
    if (/apollo/i.test(source)) return "Apollo upload";
    if (/multi.channel|multichannel/.test(text)) return "Outbound campaign";
    if (/calendar|regulated ads|book.*demo/.test(text)) return "Calendar / Booking page";
    if (/newsletter/.test(text)) return "Newsletter";
    if (/email|emerald|dan campaign|followup|outreach/.test(text)) return "Email campaign";
    if (/sms|simpletext/.test(text)) return "SMS campaign";
    if (/referr/.test(text)) return "Referral";
    if (/partner|interview/.test(text)) return "Partner / Interview";
    if (/call|sdr|vapi/.test(text)) return "Calls";
    if (/facebook|instagram|meta/.test(text)) return "Social media";
    if (/google|search|organic/.test(text)) return "Search";
    if (/website|form|direct|livetransparent|leadconnector|msgsndr|https?:/.test(text)) return "Website / Form";
    return source.replace(/[_-]+/g, " ").replace(/\s+/g, " ");
  }
  function sources(id, rows, keys) {
    var buckets = {}, found = false;
    rows.forEach(function (row) {
      var value; keys.some(function (key) { if (row[key] != null) { value = row[key]; return true; } return false; });
      if (value == null || !Number.isFinite(Number(value))) return;
      found = true; var label = sourceLabel(row); buckets[label] = (buckets[label] || 0) + Number(value);
    });
    var values = Object.keys(buckets).map(function (label) { return { label: label, value: buckets[label] }; }).filter(function (row) { return row.value > 0; }).sort(function (a,b) { return b.value-a.value; });
    var max = Math.max.apply(null, values.map(function (row) { return row.value; }).concat([1]));
    document.querySelector(id).innerHTML = values.length ? values.map(function (row) { return '<div class="metric"><span>'+esc(row.label)+'</span><span>'+num(row.value)+'</span></div><div style="height:5px;background:#f5f5f3;margin-bottom:10px"><div style="height:5px;background:'+(row.label === "Unknown / Unattributed" ? '#bc9200' : '#155aa0')+';width:'+row.value/max*100+'%"></div></div>'; }).join("") : '<div class="unavailable">'+(found ? 'No source events in this period.' : 'Source facts unavailable.')+'</div>';
  }
  function renderSources(summary, facts) {
    var rows = facts.sourceBreakdown || [];
    sources("#opp-sources", rows, ["opportunities"]);
    sources("#mql-sources", rows, ["mqls"]);
    sources("#sql-source-summary", rows, ["sqls"]);
    var coverage=document.querySelector("#mql-coverage");
    if (coverage) coverage.textContent = "Same period-entry cohort as Band 1; latest recorded contact acquisition source. Unknown remains visible.";
  }
  function renderSdr(facts) {
    if (!Array.isArray(facts.sdrOutputs) || !facts.sdrOutputs.length) return;
    var calls={};
    Array.from(document.querySelectorAll("#sdr-table tbody tr")).forEach(function(row) {
      var cells=Array.from(row.cells); if (cells.length>=7) calls[cells[0].textContent.trim()]=cells.slice(1,7).map(function(cell){return cell.innerHTML;});
    });
    document.querySelector("#sdr-table thead tr").innerHTML=["SDR / Owner","Attempted","Answered","Busy","No answer","Failed","Ringing","Booked","SQLs","MQLs"].map(function(x){return '<th>'+esc(x)+'</th>';}).join("");
    var rows=facts.sdrOutputs,totals={booked:0,sqls:0,mqls:0};
    document.querySelector("#sdr-table tbody").innerHTML=rows.map(function(row) {
      ["booked","sqls","mqls"].forEach(function(key){totals[key]+=Number(row[key]||0);});
      var name=row.owner_name,call=calls[name]||["—","—","—","—","—","—"];
      return '<tr><td>'+esc(name)+(row.is_sdr?"":' <small>(non-SDR / unattributed)</small>')+'</td>'+call.map(function(cell){return '<td>'+cell+'</td>';}).join("")+["booked","sqls","mqls"].map(function(key){return '<td>'+num(row[key])+'</td>';}).join("")+'</tr>';
    }).join("");
    var strip=document.querySelector("#sdr-totals");
    strip.querySelectorAll(".output-kpi").forEach(function(el){el.remove();});
    ["booked","sqls","mqls"].forEach(function(key){
      var div=document.createElement("div"); div.className="kpi output-kpi";
      div.innerHTML='<div class="label">'+esc({booked:"Booked",sqls:"SQLs entered",mqls:"MQLs entered"}[key])+'</div><div class="value">'+num(totals[key])+'</div>';
      strip.appendChild(div);
    });
    document.querySelector("#calls-source-note").textContent="Calls retain their native GHL date-scoped basis. MQLs/SQLs use the same first-entry cohorts as Band 1, attributed to the latest recorded opportunity owner (not necessarily the creator). Booked: distinct Regulated Ads contacts by scheduled Pacific date, credited only to recorded Originating SDR or SDR appointment creator; otherwise unattributed. Non-SDR/unassigned rows reconcile totals; they are not SDR rankings.";
  }
  function campaignName(row) {
    var name = String(row.campaign || row.name || "");
    var aliases = { emerald_email_event:"Emerald email campaigns — sequence not recorded", simpletexting_campaign_v1:"SimpleTexting — campaign not recorded", "LinkedIn - unattributed":"LinkedIn — campaign not recorded", "Email - unattributed":"Email — campaign not recorded" };
    return aliases[name] || name || "Campaign not recorded";
  }
  function table(id, rows, keys) {
    document.querySelector(id+" tbody").innerHTML = rows.length ? rows.map(function(row) { return '<tr><td>'+esc(campaignName(row))+'</td>'+keys.map(function(key) { return '<td>'+num(row[key])+'</td>'; }).join("")+'</tr>'; }).join("") : '<tr><td colspan="'+(keys.length+1)+'" class="unavailable">Campaign facts unavailable.</td></tr>';
  }
  function note(id,text) { var el=document.querySelector(id).closest("section").querySelector(".small-note"); if (!el) { el=document.createElement("p");el.className="small-note";document.querySelector(id).closest("section").appendChild(el); } el.textContent=text; }
  function renderCampaigns(summary, channels, facts) {
    var rows=channels.campaignChannelBreakdown || [], window=facts.window || {}, exact=evidence && window.from===evidence.window.from && window.to===evidence.window.to;
    var email=rows.filter(function(row) { return row.channel==="email"; }).map(function(row) {
      var copy=Object.assign({},row); if (row.campaign==="emerald_email_event" && !row.email_sent) copy.email_delivered=null; return copy;
    });
    var verticals=evidence ? evidence.rows : [];
    verticals.forEach(function(row) {
      email.push({campaign:row.campaign+" · Email",email_sent:exact?row.sent:null,email_delivered:null,email_opened:null,email_clicked:null,email_replies:null,email_bounced:null});
    });
    table("#email-table",email,["email_sent","email_delivered","email_opened","email_clicked","email_replies","email_bounced"]);
    note("#email-table",exact ? "October vertical campaigns: 1,501 sent, verified by exact queue-message/export IDs. 21 action errors and 2 skips are separate. Delivery and engagement unavailable. Legacy event-ledger rows are separate; no overlapping sends added to the total." : "October vertical campaigns: reconciled sent snapshot available only for Oct 4–10, 2026 Pacific. Other windows remain unavailable until reconciled. — means unavailable.");
    var linkedin=rows.filter(function(row) { return row.channel==="linkedin"; });
    verticals.forEach(function(row) { linkedin.push({campaign:row.campaign+" · LinkedIn — no attributed feed",linkedin_invites:null,linkedin_accepted:null,linkedin_dms:null,linkedin_opened:null,linkedin_replies:null}); });
    table("#linkedin-table",linkedin,["linkedin_invites","linkedin_accepted","linkedin_dms","linkedin_opened","linkedin_replies"]);
    document.querySelector("#linkedin-table thead th:nth-child(4)").textContent="Msgs sent";
    note("#linkedin-table","Campaign names come from the source ledger. Unattributed events are not assigned to a vertical. October vertical LinkedIn performance has no reconciled feed; invite/DM senders remain paused.");
    var sms=rows.filter(function(row) { return row.channel==="sms"; }).map(function(row) { return {campaign:campaignName(row),sent:row.sms_sent,delivered:null,replies:row.sms_replies,failed:null,attempts:null,unauthorized:null,timeouts:null}; });
    verticals.forEach(function(row) { sms.push({campaign:row.campaign+" · SMS",sent:null,delivered:null,replies:null,failed:null,attempts:exact?row.sms_attempts:null,unauthorized:exact?row.sms_unauthorized:null,timeouts:exact?row.sms_timeouts:null}); });
    document.querySelector("#sms-table thead tr").innerHTML=["SMS campaign","Sent","Delivered","Replies","Failed","Webhook attempts","Auth rejected","Timed out"].map(function(x) {return '<th>'+esc(x)+'</th>';}).join("");
    table("#sms-table",sms,["sent","delivered","replies","failed","attempts","unauthorized","timeouts"]);
    note("#sms-table",exact ? "911 vertical webhook attempts: 477 application auth rejections and 434 timeouts. These are not sends or provider delivery failures. Timeouts require provider reconciliation before replay. Legacy SMS counts remain a separate cohort." : "Vertical send and delivery counts remain unavailable. Attempt diagnostics are a date-scoped Oct 4–10 snapshot; no timeout is assumed unsent.");
    // Replace only the email KPI: avoid adding an unreconciled all-channel legacy total.
    var strip=document.querySelector("#outbound-totals");
    if (strip) { var card=strip.querySelector(".kpi"); if(card && exact) { card.querySelector(".label").textContent="Vertical emails sent"; card.querySelector(".value").textContent=num(evidence.matched_sent); var small=card.querySelector(".small-note") || card.querySelector(".hint"); if(small) small.textContent="exact-ID Oct 4–10 snapshot"; } }
  }
  function renderSdr(facts) {
    if (!Array.isArray(facts.sdrOutputs) || !facts.sdrOutputs.length) return;
    var calls={};
    Array.from(document.querySelectorAll("#sdr-table tbody tr")).forEach(function(row) {
      var cells=Array.from(row.cells); if (cells.length>=7) calls[cells[0].textContent.trim()]=cells.slice(1,7).map(function(cell){return cell.innerHTML;});
    });
    document.querySelector("#sdr-table thead tr").innerHTML=["SDR / Owner","Attempted","Answered","Busy","No answer","Failed","Ringing","Booked","SQLs","MQLs"].map(function(x){return '<th>'+esc(x)+'</th>';}).join("");
    var rows=facts.sdrOutputs,totals={booked:0,sqls:0,mqls:0};
    document.querySelector("#sdr-table tbody").innerHTML=rows.map(function(row) {
      ["booked","sqls","mqls"].forEach(function(key){totals[key]+=Number(row[key]||0);});
      var name=row.owner_name,call=calls[name]||["—","—","—","—","—","—"];
      return '<tr><td>'+esc(name)+(row.is_sdr?"":' <small>(non-SDR / unattributed)</small>')+'</td>'+call.map(function(cell){return '<td>'+cell+'</td>';}).join("")+["booked","sqls","mqls"].map(function(key){return '<td>'+num(row[key])+'</td>';}).join("")+'</tr>';
    }).join("");
    var strip=document.querySelector("#sdr-totals");
    strip.querySelectorAll(".output-kpi").forEach(function(el){el.remove();});
    ["booked","sqls","mqls"].forEach(function(key){
      var div=document.createElement("div"); div.className="kpi output-kpi";
      div.innerHTML='<div class="label">'+esc({booked:"Booked",sqls:"SQLs entered",mqls:"MQLs entered"}[key])+'</div><div class="value">'+num(totals[key])+'</div>';
      strip.appendChild(div);
    });
    document.querySelector("#calls-source-note").textContent="Calls retain their native GHL date-scoped basis. MQLs/SQLs use the same first-entry cohorts as Band 1, attributed to the latest recorded opportunity owner (not necessarily the creator). Booked: distinct Regulated Ads contacts by scheduled Pacific date, credited only to recorded Originating SDR or SDR appointment creator; otherwise unattributed. Non-SDR/unassigned rows reconcile totals; they are not SDR rankings.";
  }
  var previous = window.ltRenderV1Evidence;
  window.ltRenderV1Evidence = function(summary, facts) {
    if (previous) previous(summary, facts);
    renderSources(summary, facts);
  };
  window.ltRenderBandImprovements=function(summary,channels,facts) {latest={summary:summary,channels:channels,facts:facts};renderSources(summary,facts);renderCampaigns(summary,channels,facts);renderSdr(facts);};
  fetch("vertical-campaign-evidence.json",{cache:"no-store"}).then(function(response) {if(!response.ok) throw new Error("Campaign snapshot unavailable");return response.json();}).then(function(data) {evidence=data;var state=latest || window.ltV1Current;if(state) window.ltRenderBandImprovements(state.summary,state.channels,state.facts);}).catch(function() {note("#email-table","Vertical campaign evidence unavailable; no counts substituted.");});
  if(window.ltV1Current) window.ltRenderBandImprovements(window.ltV1Current.summary,window.ltV1Current.channels,window.ltV1Current.facts);
})();
