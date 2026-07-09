"""
One-time import of the 50-county outreach status report into the counties table.
Populates outreach_status and status_notes. Safe to re-run (upserts by name+state).
"""
import sqlite3
from datetime import datetime

DB_PATH = "pre_foreclosure.db"

# (county_name, state, outreach_status, status_notes)
REPORT = [
    ("Cuyahoga", "OH", "data_received", "Sent PDF with 702 Lis Pendens case records (Apr-Jun 2026) - no addresses included, just case #s and names"),
    ("Johnson", "KS", "data_received", "Sent PDF with 1 filing only; said to check District Court site for more"),
    ("Miami-Dade", "FL", "pending", "FOIA #30172 accepted, still waiting to hear on fees/availability"),
    ("Essex", "NJ", "pending", "OPRA #17192 accepted, 7 business days to respond"),
    ("Lake", "IL", "pending", "Had to re-clarify after a duplicate email, still waiting on actual data"),
    ("Pierce", "WA", "fee_required", "Invoice issued (Ref P045160-061526), they want payment first"),
    ("Broward", "FL", "fee_required", "Said bulk data isn't free, told us to email PublicRecords@browardclerk.org"),
    ("Franklin", "OH", "refused", "No bulk requests at all - told to use their website or call 614-525-3621"),
    ("Bergen", "NJ", "refused", "Clerk says they don't keep a list like this"),
    ("Bernalillo", "NM", "refused", "Said no addresses are stored with their Lis Pendens records, no export available"),
    ("Cook", "IL", "refused", "FOIA technically granted but it's DIY only on their portal, no addresses there either"),
    ("Palm Beach", "FL", "refused", "Portal only - Landmark Web Official Records Search"),
    ("King", "WA", "refused", "Not covered under WA's public records law, pointed to Recorder's portal instead"),
    ("Fairfax", "VA", "refused", "FOIA doesn't apply to land records here, told to research it ourselves"),
    ("Philadelphia", "PA", "redirected", "Told to call Records Management directly: 215-686-7008"),
    ("Denver", "CO", "redirected", "Need to resubmit as a CORA request to Clerk & Recorder"),
    ("Oakland", "MI", "redirected", "Pointed to their FOIA portal"),
    ("Fulton", "GA", "redirected", "Auto-reply says to use the Open Records Center portal"),
    ("Marion", "IN", "wrong_county", "Accidentally reached Marion County FL instead of Indiana, need to redo"),
    ("Maricopa", "AZ", "no_reply", "mcrecorder@risc.maricopa.gov"),
    ("Wake", "NC", "no_reply", "rodinfo@wake.gov"),
    ("Mecklenburg", "NC", "no_reply", "rod@mecklenburgcountync.gov"),
    ("Clark", "NV", "no_reply", "RecWeb@ClarkCountyNV.gov (resent after first one bounced)"),
    ("Wayne", "MI", "no_reply", "Rodhelp@waynecountymi.gov (resent after first one bounced)"),
    ("Tarrant", "TX", "no_reply", "wm-countyclerk@tarrantcountytx.gov (resent after first one bounced)"),
    ("Dallas", "TX", "no_reply", "DCRecords@dallascounty.org"),
    ("Gwinnett", "GA", "no_reply", "Tysh.Coleman@GwinnettCounty.com"),
    ("Harris", "TX", "bounced", "Blocked by their mail server - won't accept mail from Gmail"),
    ("Hamilton", "IN", "bounced", "Same issue - Gmail blocked"),
    ("Allen", "IN", "bounced", "Same issue - Gmail blocked"),
    ("St. Joseph", "IN", "bounced", "Same issue - Gmail blocked"),
    ("Elkhart", "IN", "bounced", "Same issue - Gmail blocked"),
    ("Kings", "NY", "bounced", "Same issue - Gmail blocked"),
    ("Queens", "NY", "bounced", "Same issue - Gmail blocked"),
    ("Milwaukee", "WI", "bounced", "Same issue - Gmail blocked"),
    ("Tulsa", "OK", "bounced", "Gmail isn't on their allowed senders list"),
    ("Montgomery MD", "MD", "bounced", "Same issue - Gmail blocked"),
    ("Prince Georges", "MD", "bounced", "Same issue - Gmail blocked"),
    ("Middlesex", "NJ", "bounced", "Wrong address - mxclerk@co.middlesex.nj.us, user unknown"),
    ("Collin", "TX", "bounced", "Wrong address - countyclerk@collincountytx.gov rejected"),
    ("Bexar", "TX", "bounced", "Wrong address - countyclerk@bexar.org not found"),
    ("Shelby", "TN", "bounced", "Their server timed out - info@register.shelby.tn.us"),
    ("Cook Court", "IL", "bounced", "Their server timed out - foi@cookcountyclerkofcourt.org"),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

updated, inserted = 0, 0
for name, state, outreach_status, notes in REPORT:
    cur.execute("SELECT id FROM counties WHERE county_name = ? AND state = ?", (name, state))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE counties SET outreach_status = ?, status_notes = ? WHERE id = ?",
            (outreach_status, notes, row[0]),
        )
        updated += 1
    else:
        now = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO counties (county_name, state, status, outreach_status, status_notes, created_at, updated_at) "
            "VALUES (?, ?, 'active', ?, ?, ?, ?)",
            (name, state, outreach_status, notes, now, now),
        )
        inserted += 1

conn.commit()
print(f"Updated {updated} counties, inserted {inserted} new counties.")
conn.close()
