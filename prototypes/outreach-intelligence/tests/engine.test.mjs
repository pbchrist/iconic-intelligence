// Tests the exact self-contained artifact published in the feature branch.
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import assert from 'node:assert/strict';

const html = readFileSync(process.env.WORKBENCH_HTML || new URL('../index.html',import.meta.url), 'utf8');
assert.match(html, /<script type="module">/);
const wholeScript = html.split('<script type="module">',2)[1].split('</script>',1)[0];
const engineSource = wholeScript.split('const $ = id =>',1)[0];
const {parseCSV, analyze, styleFromSamples, draft, toCSV} = await import(`data:text/javascript;base64,${Buffer.from(engineSource).toString('base64')}`);

const sample=`company,contact_name,title,email,industry,event_name,evidence_url,evidence_date,do_not_contact,prior_contact
"Acme Foundation","Jane Doe","Development Director",jane@example.org,arts,"Annual Gala",https://example.org/gala,2026-11-10,no,no
"Opted Out","Alex Smith","Producer",alex@example.org,arts,,,,yes,no`;

test('parses quoted CSV',()=>{const rs=parseCSV(sample);assert.equal(rs.length,2);assert.equal(rs[0].event_name,'Annual Gala')});
test('blocks opt-out',()=>{const rs=analyze(parseCSV(sample),{today:'2026-11-16'});assert.equal(rs.find(r=>r.company==='Opted Out').status,'blocked')});
test('blocked record cannot receive draft',()=>{const rs=analyze(parseCSV(sample));assert.throws(()=>draft(rs.find(r=>r.status==='blocked')))});
test('never calls an email verified merely from syntax',()=>{const rs=analyze(parseCSV(sample));assert.match(rs[0].email_check,/unverified/)});
test('deduplicates case-insensitively',()=>{const rs=analyze([...parseCSV(sample),{company:'Duplicate',contact_name:'X Y',title:'Director',email:'JANE@example.org'}]);assert.equal(rs.filter(r=>r.status==='blocked').length,2)});
test('does not invent event-specific claims without a valid evidence URL',()=>{const p=analyze([{company:'A',contact_name:'X Y',title:'Director',email:'xy@example.org',event_name:'Claimed billion dollar win'}])[0];assert.doesNotMatch(draft(p).body,/billion/)});
test('rejects potentially executable source URL',()=>{const p=analyze([{company:'A',contact_name:'X Y',title:'Director',email:'xy@example.org',evidence_url:'javascript:alert(1)'}])[0];assert.equal(p.evidence_url,'')});
test('prevents spreadsheet formula injection in exports',()=>{assert.match(toCSV([{x:'=DANGEROUS()'}],['x']),/\x27=DANGEROUS/)});
test('does not train LLM or claim to',()=>{assert.equal(styleFromSamples('Hi\nBest').training,false)});
