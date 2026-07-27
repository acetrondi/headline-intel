/* Functional smoke test for the browser app — runs in Node, no browser needed.
 *
 *     node tests/smoke.cjs
 *
 * Boots assets/app.js against a minimal DOM stub and asserts that the UI wires up
 * and that the measured platform inversions actually show through in the scores.
 * pipeline/verify.py covers Python<->JS parity; this covers "does the app work".
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

// ------------------------------------------------------------ DOM stub
const els = {};
const mk = id => (els[id] = {
  id, value: '', innerHTML: '', textContent: '', dataset: {},
  addEventListener() {}, querySelectorAll() { return []; }, setAttribute() {}
});
['plat', 'title', 'sub', 'topic', 'go', 'demo', 'copy', 'score', 'scorenote',
 'axes', 'flags', 'ctabs', 'cands', 'subs', 'tags', 'rules', 'prompt'].forEach(mk);

globalThis.window = globalThis;
globalThis.document = {
  addEventListener(_, fn) { globalThis.__boot = fn; },
  getElementById: id => els[id] || mk(id),
  querySelectorAll: () => []
};

// ------------------------------------------------------------ load app
eval(fs.readFileSync(path.join(ROOT, 'assets/data.js'), 'utf8'));
const src = fs.readFileSync(path.join(ROOT, 'assets/app.js'), 'utf8')
  .replace("(() => {\n  'use strict';", "globalThis.__t = (() => {\n  'use strict';")
  .replace(/\}\)\(\);\s*$/, 'return { titleFeatures, scoreTitle };\n})();');
eval(src);
globalThis.__boot();                     // simulate DOMContentLoaded

const { scoreTitle } = globalThis.__t;

// ------------------------------------------------------------ assertions
const checks = [];
const ok = (name, cond, detail = '') => checks.push([Boolean(cond), name, detail]);

ok('platform select is populated', els.plat.innerHTML.includes('Hacker News'));
ok('platform rules render on load', els.rules.innerHTML.includes('<table'));
ok('all six platforms have rules', Object.keys(window.HI.RULES).length === 6);
ok('lexicons loaded', window.HI.LEX.POWER.length > 50);
ok('corpus metadata present', /^\d/.test(window.HI.META.n_posts), window.HI.META.n_posts + ' posts');

const s = scoreTitle('10 Postgres indexing mistakes I made in production', 'devto');
ok('score is within 0-100', s.pct >= 0 && s.pct <= 100, `pct=${s.pct.toFixed(1)}`);
ok('Dev.to uses its own fitted model', s.model === 'platform', s.model);
ok('feature vector is complete', Object.keys(s.f).length >= 45, Object.keys(s.f).length + ' features');

// The headline finding must survive into the shipped app: rules invert by platform.
const listicle = scoreTitle('10 Postgres indexing mistakes I made', 'devto').pct;
const question = scoreTitle('Are your Postgres indexes wrong?', 'devto').pct;
ok('Dev.to: listicle beats question', listicle > question,
   `${listicle.toFixed(1)} vs ${question.toFixed(1)}`);

const plain = scoreTitle('Show HN: a 2 kB state manager with zero dependencies', 'hackernews').pct;
const hyped = scoreTitle('The Ultimate Guide To State Management: Everything You Need', 'hackernews').pct;
ok('Hacker News: plain beats ultimate-guide', plain > hyped,
   `${plain.toFixed(1)} vs ${hyped.toFixed(1)}`);

// typography must not change the score (emoji/apostrophe handling)
const straight = scoreTitle("I'll know when I see this", 'medium').pct;
const curly = scoreTitle('I’ll know when I see this', 'medium').pct;
ok('curly and straight apostrophes score the same', Math.abs(straight - curly) < 0.5,
   `${straight.toFixed(2)} vs ${curly.toFixed(2)}`);

// ------------------------------------------------------------ report
let failed = 0;
for (const [pass, name, detail] of checks) {
  console.log(`  ${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
  if (!pass) failed++;
}
console.log(failed ? `\nFAILED ${failed} check(s)` : '\nsmoke test: all passed');
process.exit(failed ? 1 : 0);
