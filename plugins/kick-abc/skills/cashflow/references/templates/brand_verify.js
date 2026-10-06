// Render the page, then confirm the brand pass has something to attach to. The icon script
// runs against the rendered DOM, so a class the renderer never emits means silent no-op.
const fs = require("fs");
const file = process.argv[2];
const html = fs.readFileSync(file, "utf8");

const data = JSON.parse(html.match(/<script[^>]*id="data"[^>]*>([\s\S]*?)<\/script>/)[1]);

const { JSDOM, VirtualConsole } = require("jsdom");
const threw = [];
const vc = new VirtualConsole().on("jsdomError", (e) => threw.push(e.message.split("\n")[0]));
const dom = new JSDOM(html, { runScripts: "dangerously", virtualConsole: vc });
/* The rendered page, minus its own source: script text contains class names as strings and
   would satisfy a hook check that the renderer never actually met. */
const out = dom.window.document.body.innerHTML
  .replace(/<script[\s\S]*?<\/script>/g, "")
  .replace(/<style[\s\S]*?<\/style>/g, "");

const name = file.split("/").pop();
let fail = 0;
for (const e of threw) { console.log("  page threw: " + e); fail++; }

// The four hooks the brand icon pass needs, and where each one lands.
const hooks = [
  ['class="kpi', "KPI tiles"],
  ['class="k-l', "KPI label, where the glyph goes"],
  ['class="callout', "callout, the aha marker"],
  ['class="mark', "entity mark in the header"],
];
for (const [needle, what] of hooks) {
  const n = (out.match(new RegExp(needle.replace(/[[\]"]/g, "\\$&"), "g")) || []).length
          + (html.match(new RegExp(needle.replace(/[[\]"]/g, "\\$&"), "g")) || []).length;
  if (!n) { console.log(`  no ${what} (${needle}), icons would silently no-op`); fail++; }
}
// The theme has to actually be present.
if (!html.includes('id="brand-theme"')) { console.log("  no brand-theme style block"); fail++; }
if (!html.includes('id="brand-icons"')) { console.log("  no brand-icons script block"); fail++; }
// And the file has to still work offline.
const remote = html.match(/(?:src|href)\s*=\s*["']https?:\/\//g) || [];
const imports = html.match(/@import\s+url\(\s*['"]?https?:\/\//g) || [];
if (remote.length + imports.length) {
  console.log(`  ${remote.length + imports.length} remote reference(s), breaks offline`); fail++;
}
// Every tab and toggle must have a handler behind it.
const tabs = (out.match(/class="tab/g) || []).length;
const hasTabHandler = html.includes('tabs.addEventListener');
if (tabs && !hasTabHandler) { console.log("  tabs render but nothing handles the click"); fail++; }

// The brand block existing is not the same as the brand being right. These are the values a
// reader recognizes as Kick, so each one is asserted rather than assumed. A silent fallback to
// the template's neutral palette is the exact regression that ships an unbranded-looking file.
const theme = (html.match(/<style id="brand-theme">([\s\S]*?)<\/style>/) || [])[1] || "";
const brandChecks = [
  [/--accent:\s*#3793da/i, "Kick blue #3793da as the accent"],
  [/--ink:\s*#0f1826/i, "Kick ink #0f1826"],
  [/--line:\s*rgba\(83,\s*100,\s*126/i, "slate-alpha borders rather than flat grey"],
  [/\.mark\{background:#3793da\}/i, "Kick blue on the header mark"],
  [/@font-face\{font-family:Inter/i, "Inter embedded as a font face"],
  [/src:url\(data:font\/woff2;base64,[A-Za-z0-9+/=]{5000,}\)/, "the font payload is actually present"],
  [/font-family:Inter,/i, "Inter first in the body stack"],
  [/box-shadow:0 15px 30px rgba\(83,100,126,0\.06\)/i, "the Kick card shadow"],
  [/@media print\{\.card,\.kpi\{box-shadow:none\}\}/i, "shadow dropped in print"],
];
for (const [re, what] of brandChecks) {
  if (!re.test(theme)) { console.log(`  brand: missing ${what}`); fail++; }
}
// An embedded font is a data URL, which is not a network call, but a real one would be.
if (/@font-face[\s\S]{0,400}?src:\s*url\(\s*['"]?https?:/i.test(html)) {
  console.log("  brand: font loaded over the network, which breaks offline"); fail++;
}

// ---- the categorical ramp ------------------------------------------------
// Three properties of `cats` are rules rather than taste, and all three are the kind of
// thing a later "let's brighten this up" quietly undoes. See skills/brand/SKILL.md.
function hsl(hex) {
  const n = parseInt(hex.slice(1), 16);
  const r = ((n >> 16) & 255) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn, l = (mx + mn) / 2;
  let h = 0;
  if (d) {
    h = mx === r ? ((g - b) / d + (g < b ? 6 : 0)) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    h *= 60;
  }
  // Chroma, not HSL saturation, is what "loud" means here. Kick's own chart blue #a8deff is
  // fully saturated in HSL and reads as a pastel, because at l 0.83 saturation has stopped
  // describing weight. The raw channel spread has not.
  return { h, s: d ? d / (1 - Math.abs(2 * l - 1)) : 0, l, c: d };
}
// theme.py appends its overrides after the template defaults, so the last block wins.
const catBlocks = [...theme.matchAll(/(?:--c\d:#[0-9a-f]{6};?\s*){3,}/gi)].map((m) => m[0]);
const cats = catBlocks.length
  ? [...catBlocks[catBlocks.length - 1].matchAll(/--c(\d):(#[0-9a-f]{6})/gi)]
      .sort((a, b) => a[1] - b[1]).map((m) => m[2])
  : [];
if (!cats.length) { console.log("  brand: no categorical ramp found"); fail++; }
const lights = cats.map((hex) => hsl(hex).l);
cats.forEach((hex, i) => {
  const { h, c, l } = hsl(hex);
  // The Kick product's own chart fills all sit at l 0.82 to 0.84. A band that wide is generous.
  if (l < 0.74 || l > 0.9) {
    console.log(`  brand: c${i + 1} ${hex} is not pastel, lightness ${l.toFixed(2)}`); fail++;
  }
  if (c > 0.42) {
    console.log(`  brand: c${i + 1} ${hex} is too heavy for data, chroma ${c.toFixed(2)}`); fail++;
  }
  // negbar owns red and pink. A categorical bar in that range is indistinguishable from a loss.
  if (h < 25 || h > 320) {
    console.log(`  brand: c${i + 1} ${hex} sits in the red range negbar owns, hue ${Math.round(h)}`);
    fail++;
  }
});
// Adjacent bars are the pair a reader actually compares, so they carry the separation burden.
// One ramp, one weight. A single darker entry reads as the important one, which is a claim
// categorical color is not entitled to make.
if (lights.length && Math.max(...lights) - Math.min(...lights) > 0.12) {
  console.log(`  brand: the ramp is not one lightness, spread ${(Math.max(...lights) - Math.min(...lights)).toFixed(2)}`);
  fail++;
}
for (let i = 1; i < cats.length; i++) {
  const a = hsl(cats[i - 1]).h, b = hsl(cats[i]).h;
  const gap = Math.min(Math.abs(a - b), 360 - Math.abs(a - b));
  if (gap < 25) {
    console.log(`  brand: c${i} and c${i + 1} are ${Math.round(gap)}° apart, too close to tell apart`);
    fail++;
  }
}

const kb = Math.round(Buffer.byteLength(html) / 1024);
console.log(fail
  ? `${name}: ${fail} problem(s), ${kb} KB, FAIL`
  : `${name}: ${tabs} tab(s), Kick theme + Inter + icons, offline, ${kb} KB, clean`);
process.exit(fail ? 1 : 0);
