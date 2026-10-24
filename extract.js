const fs = require('fs');
const vm = require('vm');
const path = require('path');
const BASE = __dirname;
const html = fs.readFileSync(path.join(BASE, 'telescope_compare.html'), 'utf8');

// grab the LAST <script> block (the data + render script)
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const code = scripts[scripts.length - 1];

function makeProxy() {
  const fn = function () {};
  return new Proxy(fn, {
    get(t, prop) {
      if (prop === 'matches') return false;
      if (prop === Symbol.toPrimitive) return () => '';
      if (prop === 'value') return '';
      return makeProxy();
    },
    set() { return true; },
    apply() { return makeProxy(); }
  });
}

const ctx = {
  document: makeProxy(),
  window: { matchMedia: () => ({ matches: false }) },
  console,
  __out: null,
};
vm.createContext(ctx);
const wrapped = code + '\n;__out = {DATA, S50_PRO_VALUES, DRACO_VALUES, OFFICIAL_PARAMETER_CORRECTIONS};';
vm.runInContext(wrapped, ctx);

const out = ctx.__out;
fs.writeFileSync(path.join(BASE, 'data.json'), JSON.stringify(out, null, 2));
console.log('headers:', out.DATA.headers);
console.log('row count:', out.DATA.rows.length);
console.log('S50_PRO_LEN:', out.S50_PRO_VALUES.length, 'DRACO_LEN:', out.DRACO_VALUES.length);
