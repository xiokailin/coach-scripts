import https from 'https';
import fs from 'fs';
import path from 'path';

const SHEET_ID = "1wqdXP0YwnnadeirI-s0ScEj6kBJ8gt-E";
const OUT_DIR = "/Users/linxiaokai/Downloads/forclaude/sheets_csv";

const GIDS = {
  1: "1984060835", 2: "779959662", 3: "1662021019", 4: "17518307",
  5: "659564820", 6: "401552876", 7: "909009745", 8: "618307406",
  9: "2038489536", 10: "752426272", 11: "1003400530", 12: "399754302",
  13: "1107157881", 14: "1339312539", 15: "935923252", 16: "726045306",
  17: "989601606"
};

const COOKIE = "SID=g.a000-AjBCMYRByhNoWgo8FO4HrjTqkzg5TEHcOtkdumPZ_Caxhjqnsfbok_mZgyZQgEVMvxfMgACgYKATISARMSFQHGX2MiQB3kLdHZ-_HS9B3W232nwhoVAUF8yKqhgGM_OXOxLJWkgkBeWicG0076; APISID=oB9dEmClK9EfZl2k/AsRiLR7wfoHfQx2nT; SAPISID=ytiqHwcehKxHYfz0/A1U7Vgxf1qLZ2SPwH; SIDCC=AKEyXzVqaBPPX64ISV-B04hNvTU2czqmuSOg43PPpNCh4kYpEE8SvPOKvKztbvdPQfqxfjyDfg";

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR);

function fetchFollow(url, cookie, redirectCount = 0) {
  return new Promise((resolve, reject) => {
    if (redirectCount > 5) return reject(new Error('Too many redirects'));
    const opts = new URL(url);
    const req = https.get({
      hostname: opts.hostname,
      path: opts.pathname + opts.search,
      headers: { Cookie: cookie, 'User-Agent': 'Mozilla/5.0' }
    }, (res) => {
      if (res.statusCode === 302 || res.statusCode === 301) {
        return resolve(fetchFollow(res.headers.location, cookie, redirectCount + 1));
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
  });
}

for (const [day, gid] of Object.entries(GIDS)) {
  const url = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv&gid=${gid}`;
  try {
    const csv = await fetchFollow(url, COOKIE);
    const outPath = path.join(OUT_DIR, `day${String(day).padStart(2,'0')}.csv`);
    fs.writeFileSync(outPath, csv);
    console.log(`Day ${day}: ${csv.split('\n').length} rows → ${outPath}`);
  } catch(e) {
    console.error(`Day ${day} FAILED: ${e.message}`);
  }
}
console.log('Done!');
