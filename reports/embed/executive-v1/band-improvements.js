(function () {
  "use strict";
  var evidence = null, latest = null, weeklyEmail = null, nativeCalls = null;
  function esc(value) { var el = document.createElement("span"); el.textContent = String(value == null ? "" : value); return el.innerHTML; }
  function num(value) { return value == null || value === "" || !Number.isFinite(Number(value)) ? "—" : Number(value).toLocaleString("en-US"); }
  function sources(id, rows, valueKey) {
    if (!Array.isArray(rows) || !rows.length) {
      var el = document.querySelector(id);
      if (el) el.innerHTML = '<div class="unavailable">No source events in this period.</div>';
      return;
    }
    var values = rows.map(function (row) { return { label: row.origin_kind || row.source || "Unknown", value: Number(row[valueKey] || 0) }; })
      .filter(function (row) { return row.value > 0; })
      .sort(function (a, b) { return b.value - a.value; });
    var max = Math.max.apply(null, values.map(function (row) { return row.value; }).concat([1]));
    document.querySelector(id).innerHTML = values.map(function (row) {
      var barColor = /unknown|unattributed|no attribution/i.test(row.label) ? '#bc9200' : '#155aa0';
      return '<div class="metric"><span>' + esc(row.label) + '</span><span>' + num(row.value) + '</span></div>' +
        '<div style="height:5px;background:#f5f5f3;margin-bottom:10px"><div style="height:5px;background:' + barColor + ';width:' + (row.value / max * 100) + '%"></div></div>';
    }).join("") || '<div class="unavailable">No source events in this period.</div>';
  }
  function sourceLabel(origin) {
    var labels = { ghl_automation: 'GHL automation (form not verified)', ghl_form: 'GHL form', linkedin_form: 'LinkedIn form', meta_form: 'Meta form', form_fill: 'Legacy source - not verified as form fill', booking_link_click: 'Booking link click' };
    return labels[origin] || origin || 'Unknown';
  }
  function mqlDetailRows(facts) {
    if (Array.isArray(facts.mqlSourcesDetailed) && facts.mqlSourcesDetailed.length) return facts.mqlSourcesDetailed;
    return (facts.mqlSourcesByForm || []).map(function (row) { return { origin_kind: row.source, contacts: row.contacts }; });
  }
  function utmLine(row) {
    return [row.utm_source || 'source not captured', row.utm_medium || 'medium not captured', row.utm_campaign || 'campaign not captured'].join(' / ');
  }
  function renderMqlDetail(id, facts) {
    var el = document.querySelector(id);
    if (!el) return;
    var rows = mqlDetailRows(facts).filter(function (row) { return Number(row.contacts || 0) > 0; });
    if (!rows.length) { el.innerHTML = '<div class="unavailable">No MQL source events in this period.</div>'; return; }
    el.innerHTML = rows.map(function (row) {
      var label = row.link_name || sourceLabel(row.origin_kind);
      var context = (row.vertical ? row.vertical + ' · ' : '') + utmLine(row);
      return '<div class="metric"><span>' + esc(label) + '<br><span class="small-note">' + esc(context) + '</span></span><span>' + num(row.contacts) + '</span></div>';
    }).join('');
  }
  function renderOpportunitySources(summary, facts) {
    var el = document.querySelector('#opp-sources');
    if (!el) return;
    var actionRows = Array.isArray(facts.opportunityActionSources) && facts.opportunityActionSources.length;
    var rows = actionRows ? facts.opportunityActionSources.slice() : (Array.isArray(summary.opportunitySourceBreakdown) ? summary.opportunitySourceBreakdown.slice() : []);
    if (!rows.length) {
      sources('#opp-sources', (facts.opportunityOrigin || []).map(function (r) { return { origin_kind: r.origin_kind, opportunities: r.opportunities }; }), 'opportunities');
      return;
    }
    rows.sort(function (a, b) { return Number(b.opportunities || 0) - Number(a.opportunities || 0); });
    var total = rows.reduce(function (n, r) { return n + Number(r.opportunities || 0); }, 0);
    el.innerHTML = '<div class="table-wrap"><table class="table" style="min-width:0"><thead><tr><th>Campaign</th><th>Medium</th><th>Opps</th></tr></thead><tbody>' +
      rows.map(function (r) { return '<tr><td>' + esc(r.campaign || r.source || 'Campaign not captured') + '</td><td>' + esc(r.medium || 'Not captured') + '</td><td>' + num(r.opportunities) + '</td></tr>'; }).join('') +
      '<tr><td><strong>Total</strong></td><td></td><td><strong>' + num(total) + '</strong></td></tr></tbody></table></div>' +
      (actionRows
        ? '<p class="small-note">Campaign and medium are inferred from the contact\'s current campaign/action tags; import source and csv_import medium are not used. Named-campaign coverage: ' + num((facts.opportunityActionCoverage || {}).with_campaign) + ' / ' + num((facts.opportunityActionCoverage || {}).total) + '. “Campaign not captured” means no matching campaign tag.</p>'
        : '<p class="small-note">GHL source/medium attribution for opportunities created in the window. Source labels are campaign/import names.</p>');
  }
  function renderSqlSourceSummary(facts) {
    var el = document.querySelector('#sql-source-summary');
    if (!el) return;
    var rows = Array.isArray(facts.sqlBooking) ? facts.sqlBooking : [];
    if (!rows.length) { el.innerHTML = '<div class="unavailable">0 verified booking-backed SQLs in this period.</div>'; return; }
    el.innerHTML = rows.map(function (row) {
      var calendar = row.calendar_id === 'WS6lacfQK2XOhqN7mRaF' ? 'Book a demo' : row.calendar_id === 'SrtXcFVyea7pFl3nTiIK' ? 'Regulated Ads On Social/Search' : (row.calendar_id || 'Calendar not recorded');
      return '<div class="metric"><span>' + esc(calendar) + '<br><span class="small-note">' + esc(utmLine(row)) + '</span></span><span>' + num(row.sqls) + '</span></div>';
    }).join('');
  }
  function renderSources(summary, facts) {
    if (facts.metricVersion === 'verified-booking-v2') {
      renderOpportunitySources(summary, facts);
      renderMqlDetail('#mql-sources', facts);
      renderSqlSourceSummary(facts);
      document.querySelector('#coverage-rate').textContent = mqlDetailRows(facts).length ? '100%' : '-';
      document.querySelector('#coverage-detail').textContent = num(facts.funnel?.mqls_entered) + ' MQL ledger contacts with recorded event source · ' + num(facts.funnel?.sqls_entered) + ' verified SQLs. MQL click UTM is shown when captured; opportunity and SQL campaign UTM coverage is separate.';
      document.querySelector('#mql-coverage').textContent = 'MQLs use distinct mql-tag ledger contacts, matching the headline. Booking-link rows are matched to the click ledger by contact and tag time; source / medium / campaign come from that click. GHL automation events are not assumed to be form submissions.';
      return;
    }
    var origin = facts.mqlSqlOrigin || [];
    sources("#opp-sources", facts.opportunityOrigin || [], "opportunities");
    sources("#mql-sources", origin, "mqls");
    sources("#sql-source-summary", origin, "sqls");
    var coverage = document.querySelector("#mql-coverage");
    if (coverage) coverage.textContent = "Opportunity source = how the opportunity was created (GHL attributions array). Every MQL/SQL in this window has a documented origin; no Unknown / Unattributed bucket is shown. - means no rows in that bucket.";
  }
  function renderSqlBooking(facts) {
    var card = document.querySelector("#sql-booking");
    if (!card) return;
    var rows = facts.sqlBooking || [];
    if (!rows.length) { card.innerHTML = '<div class="unavailable">No SQLs in this window with a verified Regulated Ads calendar booking. Trigger-link clicks are not counted as bookings.</div>'; return; }
    card.innerHTML = rows.map(function (row) {
      var calendar = row.calendar_id === 'SrtXcFVyea7pFl3nTiIK' ? 'Regulated Ads On Social/Search' : row.calendar_id === 'WS6lacfQK2XOhqN7mRaF' ? 'Book a demo' : row.calendar_id;
      return '<div class="metric"><span>' + esc(calendar) + ' · ' + esc(row.booked_via) + (row.attributed ? ' (attributed)' : '') + '<br><span class="small-note">' + esc(utmLine(row)) + '</span></span><span>' + num(row.sqls) + '</span></div>';
    }).join('');
  }
  function renderMqlsAdded(facts) {
    var card = document.querySelector("#mqls-added");
    if (!card) return;
    var rows = mqlDetailRows(facts).filter(function (row) { return Number(row.contacts || 0) > 0; }).sort(function (a, b) { return Number(b.contacts || 0) - Number(a.contacts || 0); });
    if (!rows.length) { card.innerHTML = '<div class="unavailable">No MQLs added in this window.</div>'; return; }
    card.innerHTML = rows.map(function (row) {
      var label = row.link_name || sourceLabel(row.origin_kind);
      var context = (row.vertical ? row.vertical + ' · ' : '') + utmLine(row);
      return '<div class="metric"><span>' + esc(label) + '<br><span class="small-note">' + esc(context) + '</span></span><span>' + num(row.contacts) + '</span></div>';
    }).join('');
  }
  function renderBookingsBySource(facts) {
    var rows = Array.isArray(facts.bookingsBySource) ? facts.bookingsBySource : [];
    var card = document.querySelector("#bookings-by-source tbody");
    if (!card) return;
    if (!rows.length) { card.innerHTML = '<tr><td colspan="5" class="unavailable">No verified bookings with source rows in this period.</td></tr>'; return; }
    card.innerHTML = rows.map(function (row) {
      return '<tr><td>' + esc(row.utm_source || 'UTM not captured') + '</td><td>' + esc(row.utm_medium || 'Not captured') + '</td><td>' + esc(row.utm_campaign || 'Not captured') + '</td><td>' + num(row.contacts) + '</td></tr>';
    }).join('');
  }
  function fmtPST(value) {
    if (!value) return "Unavailable";
    var d = new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return new Intl.DateTimeFormat("en-US", { timeZone: "America/Los_Angeles", month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(d) + " PT";
  }
  function calendarName(id) {
    return id === "SrtXcFVyea7pFl3nTiIK" ? "Regulated Ads On Social/Search" : id === "WS6lacfQK2XOhqN7mRaF" ? "Book a demo" : (id || "Calendar not recorded");
  }
  function ownerNames(facts) {
    var map = { unassigned: "Unassigned" };
    (facts.sdrOutputs || []).forEach(function (row) { if (row.owner_id) map[row.owner_id] = row.owner_name || row.owner_id; });
    return map;
  }
  function wow(value, prior) {
    if (value == null || prior == null || !Number.isFinite(Number(value)) || !Number.isFinite(Number(prior)) || Number(prior) === 0) return "";
    var p = (Number(value) - Number(prior)) / Number(prior) * 100;
    return (p > 0 ? "+" : "") + p.toFixed(1) + "% WoW";
  }
  function callCell(value, prior) {
    if (value == null) return "Unavailable";
    var change = wow(value, prior);
    return num(value) + (change ? '<div class="wow">' + esc(change) + '</div>' : "");
  }
  function nativeWindowFor(facts) {
    if (!nativeCalls || !facts.window) return null;
    return (nativeCalls.windows || []).find(function (w) { return w.from === facts.window.from && w.to === facts.window.to; }) || null;
  }
  function priorNativeWindow(window) {
    if (!nativeCalls || !window) return null;
    var from = new Date(window.from + "T00:00:00Z"), to = new Date(window.to + "T00:00:00Z");
    var span = Math.round((to - from) / 86400000) + 1;
    var priorTo = new Date(from.getTime() - 86400000), priorFrom = new Date(priorTo.getTime() - (span - 1) * 86400000);
    var keyTo = priorTo.toISOString().slice(0, 10), keyFrom = priorFrom.toISOString().slice(0, 10);
    return (nativeCalls.windows || []).find(function (w) { return w.from === keyFrom && w.to === keyTo; }) || null;
  }
  function renderSdr(facts) {
    if (!Array.isArray(facts.sdrOutputs) || !facts.sdrOutputs.length) return;
    var native = nativeWindowFor(facts), prior = priorNativeWindow(native || facts.window);
    document.querySelector("#sdr-table thead tr").innerHTML = ["SDR / Owner", "Attempted", "Answered", "Busy", "No answer", "Failed", "Ringing", "Booked", "SQLs", "MQLs"].map(function (x) { return '<th>' + esc(x) + '</th>'; }).join("");
    var rows = facts.sdrOutputs, totals = { booked: 0, sqls: 0, mqls: 0 };
    document.querySelector("#sdr-table tbody").innerHTML = rows.map(function (row) {
      ["booked", "sqls", "mqls"].forEach(function (key) { totals[key] += Number(row[key] || 0); });
      var name = row.owner_name, call;
      if (native) {
        var s = (native.sdr || {})[name], p = (prior && prior.sdr || {})[name] || {};
        call = s ? [callCell(s.attempted, p.attempted), callCell(s.answered, p.answered), callCell(s.busy, p.busy), callCell(s.no_answer, p.no_answer), callCell(s.failed, p.failed), callCell(s.ringing, p.ringing)] : ["Unavailable", "Unavailable", "Unavailable", "Unavailable", "Unavailable", "Unavailable"];
      } else {
        call = ["Unavailable", "Unavailable", "Unavailable", "Unavailable", "Unavailable", "Unavailable"];
      }
      return '<tr><td>' + esc(name) + (row.is_sdr ? "" : row.owner_id === 'unassigned' ? ' <small>(unassigned)</small>' : ' <small>(non-SDR)</small>') + '</td>' + call.map(function (cell) { return '<td>' + cell + '</td>'; }).join("") + ["booked", "sqls", "mqls"].map(function (key) { return '<td>' + num(row[key]) + '</td>'; }).join("") + '</tr>';
    }).join("");
    var strip = document.querySelector("#sdr-totals");
    if (native) {
      var t = native.team || {}, pt = prior && prior.team || {};
      strip.innerHTML = [
        '<div class="kpi"><div class="label">Calls attempted</div><div class="value">' + num(t.attempted) + '</div><div class="wow">' + esc(wow(t.attempted, pt.attempted)) + '</div></div>',
        '<div class="kpi"><div class="label">Answered</div><div class="value">' + num(t.answered) + '</div><div class="wow">' + esc(wow(t.answered, pt.answered)) + '</div></div>',
        '<div class="kpi"><div class="label">Busy</div><div class="value">' + num(t.busy) + '</div><div class="wow">' + esc(wow(t.busy, pt.busy)) + '</div></div>',
        '<div class="kpi"><div class="label">No answer</div><div class="value">' + num(t.no_answer) + '</div><div class="wow">' + esc(wow(t.no_answer, pt.no_answer)) + '</div></div>',
        '<div class="kpi"><div class="label">Failed</div><div class="value">' + num(t.failed) + '</div><div class="wow">' + esc(wow(t.failed, pt.failed)) + '</div></div>',
        '<div class="kpi"><div class="label">Ringing</div><div class="value">' + num(t.ringing) + '</div><div class="wow">' + esc(wow(t.ringing, pt.ringing)) + '</div></div>'
      ].join("");
    } else {
      strip.innerHTML = '<div class="kpi"><div class="label">Call inputs</div><div class="value">Unavailable</div><div class="note">no native GHL snapshot for this window</div></div>';
    }
    strip.querySelectorAll(".output-kpi").forEach(function (el) { el.remove(); });
    ["booked", "sqls", "mqls"].forEach(function (key) {
      var div = document.createElement("div"); div.className = "kpi output-kpi";
      div.innerHTML = '<div class="label">' + esc({ booked: "New booked contacts", sqls: "Verified SQLs", mqls: "MQLs added" }[key]) + '</div><div class="value">' + num(totals[key]) + '</div>';
      strip.appendChild(div);
    });
    document.querySelector("#calls-source-note").textContent = native
      ? "Call inputs are the native GHL 'Outgoing Calls by Status' weekly report for " + native.from + " to " + native.to + " (America/Los_Angeles; captured " + (nativeCalls.captured_at || "reported") + "); values are the report totals, with Busy and Failed kept separate. Outputs: MQLs are distinct tagged contacts by latest recorded owner; SQLs are first non-canceled approved-calendar bookings by creation date; Booked counts distinct new booked contacts. Pre-booking assignee is ownership context, not proof of who booked."
      : "No native GHL call-report snapshot is captured for this window; partial Conversations call facts are not shown as native totals. Outputs remain available: MQLs are distinct tagged contacts by latest recorded owner; SQLs are first non-canceled approved-calendar bookings by creation date; Booked counts distinct new booked contacts.";
  }
  function renderNewBookings(facts) {
    var el = document.querySelector('#new-bookings');
    if (!el) return;
    var rows = Array.isArray(facts.newBookingDetails) ? facts.newBookingDetails : [];
    if (!rows.length) { el.innerHTML = '<div class="unavailable">No new bookings created in this window.</div>'; return; }
    el.innerHTML = '<h4 style="font-size:12px;margin:12px 0 6px">New bookings created in this window (meeting may be later)</h4><div class="table-wrap"><table class="table" style="min-width:0"><thead><tr><th>Contact</th><th>Booked (PT)</th><th>Scheduled (PT)</th><th>Calendar</th></tr></thead><tbody>' +
      rows.map(function (row) {
        return '<tr><td>' + esc(row.contact_name || row.contact_id || 'Unknown') + '</td><td>' + esc(fmtPST(row.booked_at)) + '</td><td>' + esc(fmtPST(row.start_at)) + '</td><td>' + esc(calendarName(row.calendar_id)) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }
  function renderMeetings(facts) {
    var el = document.querySelector("#meetings-detail");
    if (!el) return;
    var rows = Array.isArray(facts.appointmentDetails) ? facts.appointmentDetails : [];
    var owners = ownerNames(facts);
    renderNewBookings(facts);
    if (!rows.length) {
      el.innerHTML = '<div class="unavailable">Meeting detail is not currently returned for this period.</div>';
      var emptyOutcomes = document.querySelector("#meeting-outcomes");
      if (emptyOutcomes) emptyOutcomes.innerHTML = ['confirmed', 'cancelled', 'rescheduled flag', 'showed / no-show'].map(function (label) { return '<div class="right"><strong>Unavailable</strong><div class="sub">' + esc(label) + '</div></div>'; }).join("");
      var emptyNote = document.querySelector("#meeting-note");
      if (emptyNote) emptyNote.textContent = (emptyNote.textContent || "").replace(/\s*Outcomes:.*$/, "").replace(/\s*Appointment detail and outcomes.*$/, "") + " Appointment detail and outcomes are unavailable for this period; no zero substituted. SQL and new-booking counts use the booking creation date; bookings created earlier with meetings in this window appear under new bookings.";
      return;
    } else {
      el.innerHTML = '<div class="table-wrap"><table class="table"><thead><tr><th>Contact</th><th>Scheduled (PT)</th><th>Owner (pre-booking)</th><th>Calendar</th><th>Status</th><th>Booked (PT)</th></tr></thead><tbody>' + rows.map(function (row) {
        var payload = row.payload_json || {};
        var status = row.status || payload.appointmentStatus || payload.appoinmentStatus || "Unknown";
        if (payload.rescheduledAt) status += " (rescheduled)";
        return '<tr><td>' + esc(row.contact_name || row.contact_id || "Unknown") + '</td><td>' + esc(fmtPST(row.start_at)) + '</td><td>' + esc(owners[row.owner_id] || (row.owner_id === "unassigned" ? "Unassigned" : row.owner_id || "Unassigned")) + '</td><td>' + esc(calendarName(row.calendar_id)) + '</td><td>' + esc(status) + '</td><td>' + esc(fmtPST(row.booked_at)) + '</td></tr>';
      }).join("") + '</tbody></table></div>';
    }
    var confirmed = 0, cancelled = 0, rescheduled = 0;
    rows.forEach(function (row) {
      var status = String(row.status || (row.payload_json || {}).appointmentStatus || "").toLowerCase();
      if (/cancel/.test(status)) cancelled++; else if (/confirm|active|booked|showed/.test(status)) confirmed++;
      if ((row.payload_json || {}).rescheduledAt) rescheduled++;
    });
    var outcomes = document.querySelector("#meeting-outcomes");
    if (outcomes) outcomes.innerHTML = [
      '<div class="right"><strong>' + num(confirmed) + '</strong><div class="sub">confirmed</div></div>',
      '<div class="right"><strong>' + num(cancelled) + '</strong><div class="sub">cancelled</div></div>',
      '<div class="right"><strong>' + num(rescheduled) + '</strong><div class="sub">rescheduled flag</div></div>',
      '<div class="right"><strong>Unavailable</strong><div class="sub">showed / no-show</div></div>'
    ].join("");
    var note = document.querySelector("#meeting-note");
    if (note) note.textContent = (note.textContent || "").replace(/\s*Outcomes:.*$/, "") + " Outcomes: confirmed/cancelled use the recorded appointment status; rescheduled counts a reschedule flag and can overlap. Showed and no-show remain unavailable until GHL status is updated after the meeting. SQL and new-booking counts use the booking creation date; a booking created earlier with a meeting in this window appears under new bookings, not scheduled meetings.";
  }
  function renderVerticalAccuracy(facts) {
    var tbody = document.querySelector("#vertical-table tbody");
    if (!tbody || !weeklyEmail || !facts.window) return;
    var weekly = (weeklyEmail.periods || []).find(function (p) { return p.window && p.window.from === facts.window.from && p.window.to === facts.window.to; });
    if (!weekly) return;
    var aliases = { "Cannabis": "Cannabis Brands" };
    var byVertical = {};
    (weekly.rows || []).forEach(function (row) { byVertical[row.vertical] = row; });
    Array.from(tbody.rows).forEach(function (tr) {
      if (!tr.cells || tr.cells.length < 3) return;
      var name = tr.cells[0].textContent.trim();
      var row = byVertical[aliases[name] || name];
      tr.cells[2].textContent = row ? num(row.sent) : "Unavailable";
    });
    var note = document.querySelector("#vertical-note");
    if (note) note.textContent = "Sends are email sends in the native GHL captured cohort for this window, as of " + (weekly.captured_at || weeklyEmail.captured_at) + (weekly.complete === false ? " (in-progress snapshot)." : ".") + " Email only; delivery and engagement are in Band 3. Unverified closure outcomes and revenue remain unavailable.";
  }
  function renderRetargeting(facts) {
    var el = document.querySelector("#retargeting"), r = facts.retargeting;
    if (!el || !r) return;
    var available = r.available === true;
    el.innerHTML = '<div class="grid two">' +
      '<div class="metric"><span>Audience contacts</span><strong>' + (available ? num(r.audience_contacts) : "Unavailable") + '</strong></div>' +
      '<div class="metric"><span>Newsletter clickers</span><strong>' + num(r.clickers) + '</strong></div>' +
      '<div class="metric"><span>Suppressed or replied</span><strong>' + (available ? num(r.suppressed_or_replied) : "Unavailable") + '</strong></div>' +
      '<div class="metric"><span>Next action pending</span><strong>' + (available ? num(r.next_action_pending) : "Unavailable") + '</strong></div>' +
      '</div><p class="small-note">' + (available ? "Audience and suppression coverage reported by the newsletter ledgers." : "Partial source: the clicker count is from the newsletter event ledger; audience and suppression coverage are unavailable and not shown as zero.") + ' Read-only visibility; no automatic send is authorized.</p>';
  }
  function renderActions(summary, facts) {
    var el = document.querySelector("#actions");
    if (!el) return;
    var m = summary.mqlSummary || {};
    var details = Array.isArray(facts.responseSlaDetails) ? facts.responseSlaDetails : [];
    var unmatched = details.filter(function (row) { return row.status === "unmatched" || row.status === "ambiguous"; }).length;
    var clickers = facts.retargeting && facts.retargeting.clickers;
    var rows = [];
    rows.push('<div class="action"><span class="pill">MQL</span><span>' + num(m.currentMqls) + ' MQL-stage contacts awaiting Sales (current snapshot)</span></div>');
    rows.push('<div class="action"><span class="pill">SLA</span><span>' + (details.length ? num(unmatched) + ' inbound events unmatched or ambiguous' : 'Unmatched inbound events unavailable for this period') + '</span></div>');
    rows.push('<div class="action"><span class="pill yellow">Audience</span><span>' + (clickers == null ? 'Newsletter clicker count unavailable' : num(clickers) + ' newsletter clickers visible (read-only; no send)') + '</span></div>');
    rows.push('<div class="action"><span class="pill yellow">Contract</span><span>Unavailable - stale proposal source not captured</span></div>');
    rows.push('<div class="action"><span class="pill yellow">Follow-up</span><span>Unavailable - follow-up SLA source not captured</span></div>');
    el.innerHTML = rows.join("");
  }
  function campaignName(row) {
    var name = String(row.campaign || row.name || "");
    var aliases = { emerald_email_event: "Unmatched email engagement events — campaign not recorded", simpletexting_campaign_v1: "SimpleTexting — campaign not recorded", "LinkedIn - unattributed": "LinkedIn — campaign not recorded", "Email - unattributed": "Email — campaign not recorded" };
    return aliases[name] || name || "Campaign not recorded";
  }
  function table(id, rows, keys) {
    document.querySelector(id + " tbody").innerHTML = rows.length ? rows.map(function (row) {
      return '<tr><td>' + esc(campaignName(row)) + '</td>' + keys.map(function (key) { return '<td>' + num(row[key]) + '</td>'; }).join("") + '</tr>';
    }).join("") : '<tr><td colspan="' + (keys.length + 1) + '" class="unavailable">Campaign facts unavailable.</td></tr>';
  }
  function note(id, text) {
    var el = document.querySelector(id).closest("section").querySelector(".small-note");
    if (!el) { el = document.createElement("p"); el.className = "small-note"; document.querySelector(id).closest("section").appendChild(el); }
    el.textContent = text;
  }
  function renderCampaigns(summary, channels, facts) {
    var rows = channels.campaignChannelBreakdown || [], window = facts.window || {}, exact = evidence && window.from === evidence.window.from && window.to === evidence.window.to;
    var email = rows.filter(function (row) { return row.channel === "email" && ['email_sent','email_delivered','email_opened','email_clicked','email_replies','email_bounced'].some(function(k){return Number(row[k])>0;}); }).map(function(row){var r=Object.assign({},row);if(row.campaign==='emerald_email_event'){r.email_sent=null;r.email_delivered=null;}return r;});
    var verticals = evidence ? evidence.rows : [];
    var weekly=weeklyEmail?.periods?.find(function(p) {return p.window.from===window.from && p.window.to===window.to;});
    verticals.forEach(function (row) {
      var report=weekly?.rows.find(function(r) {return r.vertical===row.vertical;});
      email.push({
        campaign: row.campaign + " · Email",
        email_sent: report ? report.sent : (exact ? row.sent : null),
        email_delivered: report ? report.delivered : null,
        email_opened: report ? report.opened : null,
        email_clicked: report ? report.clicked : null,
        email_replies: report ? report.replied : null,
        email_bounced: report ? report.bounced : null
      });
    });
    email.sort(function (a, b) {
      var au = /Unmatched email engagement events/i.test(String(a.campaign || "")), bu = /Unmatched email engagement events/i.test(String(b.campaign || ""));
      return au === bu ? 0 : au ? 1 : -1;
    });
    table("#email-table", email, ["email_sent", "email_delivered", "email_opened", "email_clicked", "email_replies", "email_bounced"]);
    var emailKpi=document.querySelector('#outbound-totals .kpi');
    if(emailKpi){emailKpi.querySelector('.label').textContent='Vertical emails sent';emailKpi.querySelector('.value').textContent=num(weekly ? weekly.rows.reduce(function(n,r){return n+Number(r.sent||0);},0) : exact ? verticals.reduce(function(n,r){return n+Number(r.sent||0);},0) : null);}
    note("#email-table", weekly
      ? "Vertical campaigns use native GHL data for the selected Pacific sent-message cohort; delivery and engagement reflect their state as of "+(weekly.captured_at || weeklyEmail.captured_at)+". Not lifetime totals. Oct 4–10 sent IDs reconcile to the 1,501-message export. Native hard+soft failure counts are shown as Bounced. Unmatched event-ledger rows are separate event-date metrics."+(weekly.complete===false?" Current week is an in-progress snapshot.":"")
      : "October vertical campaigns: reconciled sent snapshot available only for Oct 4–10, 2026 Pacific. Other windows remain unavailable until reconciled. — means unavailable.");
    var linkedin = rows.filter(function (row) { return row.channel === "linkedin"; });
    verticals.forEach(function (row) { linkedin.push({ campaign: row.campaign + " · LinkedIn — no attributed feed", linkedin_invites: null, linkedin_accepted: null, linkedin_dms: null, linkedin_opened: null, linkedin_replies: null }); });
    table("#linkedin-table", linkedin, ["linkedin_invites", "linkedin_accepted", "linkedin_dms", "linkedin_opened", "linkedin_replies"]);
    document.querySelector("#linkedin-table thead th:nth-child(4)").textContent = "Msgs sent";
    note("#linkedin-table", "Campaign names come from the source ledger. Unattributed events are not assigned to a vertical. October vertical LinkedIn performance has no reconciled feed; invite/DM senders remain paused.");
    var sms = rows.filter(function (row) { return row.channel === "sms"; }).map(function (row) { return { campaign: campaignName(row), sent: row.sms_sent, delivered: null, replies: row.sms_replies, failed: null, attempts: null, unauthorized: null, timeouts: null }; });
    verticals.forEach(function (row) { sms.push({ campaign: row.campaign + " · SMS", sent: null, delivered: null, replies: null, failed: null, attempts: exact ? row.sms_attempts : null, unauthorized: exact ? row.sms_unauthorized : null, timeouts: exact ? row.sms_timeouts : null }); });
    document.querySelector("#sms-table thead tr").innerHTML = ["SMS campaign", "Sent", "Delivered", "Replies", "Failed", "Webhook attempts", "Auth rejected", "Timed out"].map(function (x) { return '<th>' + esc(x) + '</th>'; }).join("");
    table("#sms-table", sms, ["sent", "delivered", "replies", "failed", "attempts", "unauthorized", "timeouts"]);
    note("#sms-table", exact ? "911 vertical webhook attempts: 477 application auth rejections and 434 timeouts. These are not sends or provider delivery failures. Timeouts require provider reconciliation before replay. Legacy SMS counts remain a separate cohort."
      : "Vertical send and delivery counts remain unavailable. Attempt diagnostics are a date-scoped Oct 4–10 snapshot; no timeout is assumed unsent.");
  }
  var previous = window.ltRenderV1Evidence;
  window.ltRenderCanonicalSources = function(summary,facts) {renderSources(summary,facts);};
  window.ltRenderVerticalAccuracy = renderVerticalAccuracy;
  window.ltRenderV1Evidence = function (summary, facts) {
    if (previous) previous(summary, facts);
    renderSources(summary, facts);
    renderSqlBooking(facts);
    renderMqlsAdded(facts);
    renderBookingsBySource(facts);
  };
  window.ltRenderBandImprovements = function (summary, channels, facts) {
    latest = { summary: summary, channels: channels, facts: facts };
    renderSources(summary, facts);
    renderCampaigns(summary, channels, facts);
    renderSdr(facts);
    renderSqlBooking(facts);
    renderMqlsAdded(facts);
    renderBookingsBySource(facts);
     if(facts.metricVersion==='verified-booking-v2'){
       document.querySelectorAll('#headline .kpi').forEach(function(card){if(card.querySelector('.label')?.textContent==='MQL→SQL'){var rate=facts.funnel?.mql_to_sql_rate;card.querySelector('.value').textContent=rate==null?'—':(rate*100).toFixed(2)+'%';}});
       var action=document.querySelector('#actions .action span:last-child');if(action && action.textContent.includes('MQLs awaiting Sales'))action.textContent=action.textContent.replace('MQLs awaiting Sales','MQL-stage contacts awaiting Sales (current snapshot)');
      document.querySelectorAll('#headline .label').forEach(function(el){if(el.textContent==='MQLs entered')el.textContent='MQLs added';if(el.textContent==='SQLs entered')el.textContent='Verified SQLs';if(el.textContent==='Meetings booked')el.textContent='Meetings scheduled';});
      document.querySelectorAll('#band1-wow-table tbody tr').forEach(function(row){if(row.cells[0].textContent==='MQLs entered')row.cells[0].textContent='MQLs added';if(row.cells[0].textContent==='SQLs entered')row.cells[0].textContent='Verified SQLs';if(row.cells[0].textContent==='Meetings booked')row.cells[0].textContent='Meetings scheduled';});
      document.querySelector('#cache-status').textContent='Facts '+(facts.cache?.status || 'loaded')+' · computed '+(facts.cache?.computed_at || 'unavailable')+' · historical Sales Outreach entries: '+num(facts.pipelineEntries)+'; MQL stage entries: '+num(facts.mqlStageEntries)+'. These are not the headline qualification counts.';
       document.querySelector('#meeting-note').textContent='Both approved calendars: '+num(facts.meetingSummary?.unique_contacts)+' contacts scheduled in this Pacific window (canceled appointments retained in scheduled history); '+num(facts.meetingSummary?.new_bookings_created)+' new booked contacts created in this window, including meetings scheduled later. '+num(facts.bookingAttributionPending)+' new booked contacts lack supported pre-booking owner/campaign attribution. Missing historical UTM remains explicit.';
       document.querySelectorAll('#funnel-metrics .kpi').forEach(function(card){var label=card.querySelector('.label');if(!label)return;var sub=card.querySelector('.note');if(label.textContent==='MQLs')label.textContent='MQLs added';if(label.textContent==='SQLs')label.textContent='Verified SQLs';if(label.textContent==='MQLs added' && sub)sub.textContent='distinct mql-tag ledger contacts';if(label.textContent==='Verified SQLs' && sub)sub.textContent='verified booking-backed SQLs';if(label.textContent==='MQL→SQL'){card.querySelector('.value').textContent=num(facts.funnel?.mql_to_sql_converted)+' / '+num(facts.funnel?.mqls_entered);if(sub)sub.textContent='MQL tag precedes first valid booking; both events in selected period';}});
       renderSocialAccuracy(summary,facts);
      document.querySelector('#weekly-table thead th:nth-child(3)').textContent='MQL stage entries';
      document.querySelector('#weekly-table thead th:nth-child(4)').textContent='Sales Outreach entries';
    }
    renderMeetings(facts);
    renderVerticalAccuracy(facts);
    renderRetargeting(facts);
    renderActions(summary,facts);
  };
  fetch("vertical-campaign-evidence.json", { cache: "no-store" }).then(function (response) {
    if (!response.ok) throw new Error("Campaign snapshot unavailable");
    return response.json();
  }).then(function (data) {
    evidence = data;
    var state = latest || window.ltV1Current;
    if (state) window.ltRenderBandImprovements(state.summary, state.channels, state.facts);
  }).catch(function () { note("#email-table", "Vertical campaign evidence unavailable; no counts substituted."); });
  if (window.ltV1Current) window.ltRenderBandImprovements(window.ltV1Current.summary, window.ltV1Current.channels, window.ltV1Current.facts);
   function renderSocialAccuracy(summary,facts){
     var s=summary.socialPosts || {},stats=facts.socialStatistics || [],platforms=['linkedin','instagram','facebook'];
     var counts={linkedin:s.linkedinCount,instagram:s.instagramCount,facebook:s.facebookCount};
     var platformRows=platforms.map(function(p){return stats.find(function(r){return String(r.platform).toLowerCase()===p;}) || {};});
     var cards=document.querySelectorAll('#social-totals .kpi');
     var known=platforms.every(function(p,i){return counts[p]!=null || platformRows[i].posts!=null;});
     var posts=known?platforms.reduce(function(n,p,i){return n+Number(counts[p] ?? platformRows[i].posts);},0):null;
     if(cards[0]){cards[0].querySelector('.value').textContent=num(posts);cards[0].querySelector('.label').textContent='Post records';}
     document.querySelectorAll('#social-table tbody tr').forEach(function(row,i){
       if(row.cells.length<6)return;
       row.cells[1].textContent=num(counts[platforms[i]] ?? platformRows[i].posts);
       var r=platformRows[i];row.cells[4].textContent=r.likes!=null && r.comments!=null?num(Number(r.likes)+Number(r.comments)):'N/A';
     });
     ['impressions','reach','engagement','followers'].forEach(function(key,index){
       var values=platformRows.map(function(r){return key==='engagement'?(r.likes!=null && r.comments!=null?Number(r.likes)+Number(r.comments):null):r[key];});
       var complete=values.every(function(v){return v!=null;});
       if(cards[index+1])cards[index+1].querySelector('.value').textContent=complete?num(values.reduce(function(n,v){return n+Number(v);},0)):'N/A';
     });
     note('#social-table','Post records are platform placements including recorded failures: '+num(s.publishedCount)+' published; '+num(s.failedCount)+' failed. Account-statistics posts are a different coverage basis. Cross-platform statistics are N/A unless every displayed platform has exact-window source coverage. Reach is summed platform reach, not deduplicated people; followers is a snapshot, not followers gained.');
   }
   fetch('weekly-email-evidence.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw Error('Weekly evidence unavailable');return r.json();}).then(function(data){weeklyEmail=data;var s=latest || window.ltV1Current;if(s)window.ltRenderBandImprovements(s.summary,s.channels,s.facts);}).catch(function(){weeklyEmail=null;var s=latest || window.ltV1Current;if(s)renderCampaigns(s.summary,s.channels,s.facts);});
   fetch('native-call-evidence.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw Error('Native call evidence unavailable');return r.json();}).then(function(data){nativeCalls=data;var s=latest || window.ltV1Current;if(s)window.ltRenderBandImprovements(s.summary,s.channels,s.facts);}).catch(function(){nativeCalls=null;var s=latest || window.ltV1Current;if(s)window.ltRenderBandImprovements(s.summary,s.channels,s.facts);});
})();
