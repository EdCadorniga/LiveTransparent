const daysBack = 90;
const windowStart = "CURRENT_DATE - INTERVAL ''89 days''";
const windowEnd = "CURRENT_DATE";
const workflowName = ''LT - Report Daily Rollups'';
const sourceSystem = ''rollups'';

const sql = `
DROP TABLE IF EXISTS tmp_report_contacts;
DROP TABLE IF EXISTS tmp_report_opps;
DROP TABLE IF EXISTS tmp_report_forms;
DROP TABLE IF EXISTS tmp_report_dates;
