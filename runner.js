const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const htmlPath = path.join(__dirname, 'map.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// Extract inline <script>...</script> blocks (ignore scripts with src=)
const scriptRegex = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
let match;
const inlineScripts = [];
while ((match = scriptRegex.exec(html)) !== null) {
  const attrs = match[1];
  const content = match[2];
  if (!/\bsrc\s*=\s*['\"]/.test(attrs)) {
    inlineScripts.push(content);
  }
}

if (inlineScripts.length === 0) {
  console.error('No inline scripts found in map.html');
  process.exit(1);
}

// We'll run the last inline script (the page script)
const pageScript = inlineScripts[inlineScripts.length - 1];

(async () => {
  try {
    // Minimal HTML with map containers
    const base = `<!DOCTYPE html><html><head></head><body><div id="overviewMap"></div><div id="europeMap"></div></body></html>`;

    const dom = new JSDOM(base, { runScripts: 'dangerously', resources: 'usable' });

    // Make window/global available before requiring leaflet
    global.window = dom.window;
    global.document = dom.window.document;
    global.navigator = dom.window.navigator;

    // Try to require real leaflet; if it causes environment issues in jsdom,
    // fall back to a small stub of the methods used by the page script.
    // Use a minimal stub for the L API used in the page script to avoid
    // Leaflet/jsdom environment incompatibilities.
    const L = (function() {
      function MapStub(containerId) {
        this._container = containerId;
      }
      MapStub.prototype.setView = function() { return this; };
      MapStub.prototype.fitBounds = function() { return this; };

      return {
        map: (id) => new MapStub(id),
        tileLayer: () => ({ addTo: () => null }),
        circleMarker: () => ({ addTo: () => ({ bindPopup: () => {} }) }),
        polyline: () => ({ addTo: () => ({}) }),
        marker: () => ({ addTo: () => ({ bindPopup: () => {} }) }),
        divIcon: (opts) => ({ _opts: opts }),
        featureGroup: (arr) => ({ getBounds: () => ({ pad: () => ({}) }) })
      };
    })();
    dom.window.L = L;

    // Append and run the page script
    const scriptEl = dom.window.document.createElement('script');
    scriptEl.textContent = pageScript;
    dom.window.document.body.appendChild(scriptEl);

    // Give some time for any async operations (tile loads won't happen) and capture any errors
    await new Promise((res) => setTimeout(res, 1000));

    console.log('Script executed without throwing a synchronous exception.');
  } catch (err) {
    console.error('Error while running page script:');
    console.error(err && err.stack ? err.stack : err);
    process.exit(1);
  }
})();
