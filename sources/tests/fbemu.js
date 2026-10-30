// Tiny in-memory stand-in for Firebase Realtime Database, for local tests only.
// Clients (fakefb.js) talk to it over a WebSocket.
const http = require("http");
const { WebSocketServer } = require("ws");
const PORT = +(process.env.FBPORT || 9100);
let root = {};

const parts = p => p.split("/").filter(Boolean);
function get(path) { let n = root; for (const k of parts(path)) { if (n == null || typeof n !== "object") return null; n = n[k]; } return n === undefined ? null : n; }
function clean(v) { // empty objects disappear, like in Firebase
  if (v === null || typeof v !== "object") return v;
  const o = {};
  for (const k of Object.keys(v)) { const c = clean(v[k]); if (c !== null && c !== undefined) o[k] = c; }
  return Object.keys(o).length ? o : null;
}
function stamp(v) {
  if (v && typeof v === "object") {
    if (v[".sv"] === "timestamp") return Date.now();
    const o = Array.isArray(v) ? [] : {};
    for (const k of Object.keys(v)) o[k] = stamp(v[k]);
    return o;
  }
  return v;
}
function set(path, value) {
  const ks = parts(path);
  if (!ks.length) { root = clean(stamp(value)) || {}; return; }
  let n = root;
  for (const k of ks.slice(0, -1)) { if (n[k] == null || typeof n[k] !== "object") n[k] = {}; n = n[k]; }
  const last = ks[ks.length - 1];
  const v = clean(stamp(value));
  if (v === null) delete n[last]; else n[last] = v;
  root = clean(root) || {};
}

const subs = []; // {ws, id, path, ev, prev}
function snapshotOf(sub) {
  const v = get(sub.path);
  return sub.ev === "value" ? JSON.stringify(v) : (v && typeof v === "object" ? Object.keys(v).sort() : []);
}
function fire(sub, initial) {
  const v = get(sub.path);
  if (sub.ev === "value") {
    const s = JSON.stringify(v);
    if (initial || s !== sub.prev) { sub.prev = s; send(sub.ws, { t: "ev", id: sub.id, key: parts(sub.path).pop() || null, val: v }); }
    return;
  }
  const now = v && typeof v === "object" ? Object.keys(v).sort() : [];
  const before = initial ? [] : sub.prev;
  if (sub.ev === "child_added") {
    for (const k of now) if (!before.includes(k)) send(sub.ws, { t: "ev", id: sub.id, key: k, val: v[k] });
  } else if (sub.ev === "child_removed") {
    for (const k of before) if (!now.includes(k)) send(sub.ws, { t: "ev", id: sub.id, key: k, val: sub.prevVals ? sub.prevVals[k] : null });
  }
  sub.prev = now;
  sub.prevVals = v && typeof v === "object" ? JSON.parse(JSON.stringify(v)) : {};
}
function changed() { for (const s of subs.slice()) if (s.ws.readyState === 1) fire(s, false); }
function send(ws, m) { if (ws.readyState === 1) ws.send(JSON.stringify(m)); }

const srv = http.createServer((req, res) => { res.end(JSON.stringify(root)); });
const wss = new WebSocketServer({ server: srv });
wss.on("connection", ws => {
  ws.ondc = [];
  ws.on("message", raw => {
    const m = JSON.parse(raw);
    if (m.op === "set") { set(m.path, m.val); changed(); send(ws, { t: "ok", rid: m.rid }); }
    else if (m.op === "on") { const s = { ws, id: m.id, path: m.path, ev: m.ev }; subs.push(s); fire(s, true); }
    else if (m.op === "off") { for (let i = subs.length - 1; i >= 0; i--) if (subs[i].ws === ws && subs[i].id === m.id) subs.splice(i, 1); }
    else if (m.op === "once") {
      let v = get(m.path);
      if (m.orderBy && v && typeof v === "object") {
        const o = {};
        for (const k of Object.keys(v)) { const c = v[k] && v[k][m.orderBy]; if (c != null && (m.endAt == null || c <= m.endAt)) o[k] = v[k]; }
        v = Object.keys(o).length ? o : null;
      }
      send(ws, { t: "once", rid: m.rid, key: parts(m.path).pop() || null, val: v });
    }
    else if (m.op === "ondc") { ws.ondc.push(m); send(ws, { t: "ok", rid: m.rid }); }
  });
  ws.on("close", () => {
    for (let i = subs.length - 1; i >= 0; i--) if (subs[i].ws === ws) subs.splice(i, 1);
    for (const d of ws.ondc) set(d.path, d.val);
    if (ws.ondc.length) changed();
  });
});
srv.listen(PORT, "127.0.0.1", () => console.log("fbemu on", PORT));
