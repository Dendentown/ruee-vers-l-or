// Test double of the Firebase "compat" SDK (app + database) talking to fbemu.js.
(function () {
  const URL_ = "ws://127.0.0.1:" + (window.__FBPORT || 9100);
  let ws, ready, queue = [], rid = 0, subId = 0;
  const waits = {}, handlers = {}, connCbs = [];
  let connected = false;
  function connect() {
    ws = new WebSocket(URL_);
    ws.onopen = () => { connected = true; queue.forEach(m => ws.send(m)); queue = []; connCbs.forEach(cb => cb(snap(".info/connected", true))); };
    ws.onclose = () => { connected = false; connCbs.forEach(cb => cb(snap(".info/connected", false))); };
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.t === "ok" || m.t === "once") { const w = waits[m.rid]; delete waits[m.rid]; if (w) w(m); }
      else if (m.t === "ev") { const h = handlers[m.id]; if (h) h(snap(h.path + (h.ev === "value" ? "" : "/" + m.key), m.val, m.key)); }
    };
  }
  function sendRaw(o) { const s = JSON.stringify(o); if (ws && ws.readyState === 1) ws.send(s); else queue.push(s); }
  function req(o) { return new Promise(res => { o.rid = ++rid; waits[o.rid] = res; sendRaw(o); }); }
  const norm = p => p.split("/").filter(Boolean).join("/");
  let pushN = 0;
  function pushKey() { return "-" + Date.now().toString(36).padStart(10, "0") + (++pushN).toString(36).padStart(5, "0") + Math.random().toString(36).slice(2, 6); }
  function snap(path, val, key) {
    return {
      key: key !== undefined ? key : norm(path).split("/").pop(),
      val: () => (val === undefined ? null : JSON.parse(JSON.stringify(val))),
      exists: () => val !== null && val !== undefined,
      ref: ref(path),
      forEach(cb) { if (val && typeof val === "object") Object.keys(val).sort().forEach(k => cb(snap(path + "/" + k, val[k], k))); },
    };
  }
  function query(path, orderBy, endAt) {
    return {
      endAt: x => query(path, orderBy, x),
      once: () => req({ op: "once", path, orderBy, endAt }).then(m => snap(path, m.val, m.key)),
    };
  }
  function ref(path) {
    path = norm(path || "");
    const r = {
      key: path.split("/").pop() || null,
      child: p => ref(path + "/" + p),
      set: v => req({ op: "set", path, val: v === undefined ? null : v }),
      remove: () => req({ op: "set", path, val: null }),
      push(v) {
        const c = ref(path + "/" + pushKey());
        const p = v === undefined ? Promise.resolve() : c.set(v);
        c.then = (a, b) => p.then(() => c).then(a, b);
        c.catch = b => p.catch(b);
        return c;
      },
      on(ev, cb) {
        if (path === ".info/connected") { connCbs.push(cb); cb(snap(path, connected)); return cb; }
        const id = ++subId; cb.__id = (cb.__id || []).concat(id); handlers[id] = Object.assign(cb2 => cb(cb2), { path, ev }); handlers[id] = Object.assign(s => cb(s), { path, ev });
        sendRaw({ op: "on", id, path, ev }); return cb;
      },
      off(ev, cb) { (cb && cb.__id || []).forEach(id => { delete handlers[id]; sendRaw({ op: "off", id }); }); },
      once: () => req({ op: "once", path }).then(m => snap(path, m.val, m.key)),
      onDisconnect: () => ({ set: v => req({ op: "ondc", path, val: v }), remove: () => req({ op: "ondc", path, val: null }) }),
      orderByChild: k => query(path, k, null),
    };
    return r;
  }
  const database = () => ({ ref });
  database.ServerValue = { TIMESTAMP: { ".sv": "timestamp" } };
  window.firebase = { initializeApp: () => ({}), apps: [], database };
  connect();
})();
