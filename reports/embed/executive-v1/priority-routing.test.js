/* Pure acceptance checks for the Priority upsert decision. No CRM or network calls. */
"use strict";
const decide = ({ existing, status = "open", duplicate = false }) => {
  if (duplicate) return { disposition: "duplicate", mutate: false };
  if (existing && status !== "open") return { disposition: "closed_protected", mutate: false };
  if (existing && existing.stageId === "be636da7-3c15-48ab-b589-c75bcd6f9955") return { disposition: "already_priority", mutate: false };
  if (existing) return { disposition: "routed", mutate: true, opportunityId: existing.id };
  return { disposition: "created", mutate: true };
};

const cases = [
  ["new contact", {}, "created", true],
  ["open existing", { id: "opp-1", stageId: "3529dd3d-cab0-4279-967c-1aea203de4fb" }, "routed", true],
  ["already priority", { id: "opp-1", stageId: "be636da7-3c15-48ab-b589-c75bcd6f9955" }, "already_priority", false],
  ["closed protection", { id: "opp-1" }, "closed_protected", false, "won"],
  ["duplicate retry", { id: "opp-1" }, "duplicate", false, "open", true]
];
for (const [name, existing, disposition, mutate, status, duplicate] of cases) {
  const actual = decide({ existing: Object.keys(existing).length ? existing : null, status, duplicate });
  if (actual.disposition !== disposition || actual.mutate !== mutate) throw new Error(`${name}: ${JSON.stringify(actual)}`);
}
console.log(`priority routing cases passed: ${cases.length}`);
