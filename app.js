/* La Ruée vers l'Or — partie en réseau.
   The teacher's page is the host: it holds the whole game and decides every score.
   Each phone connects to it through PeerJS (WebRTC), with a 5-letter game code. */
(function () {
  "use strict";
  const D = window.RUEE_DATA;
  const $ = s => document.querySelector(s);
  const app = $("#app");
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const NUG = '<svg class="nug" aria-hidden="true"><use href="#nugget"/></svg>';
  const nugs = k => Array.from({ length: Math.max(0, Math.min(k, 6)) }, () => NUG).join("");
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const PCOL = ["#ff5a5a", "#4da3ff", "#4fd27b", "#c084ff", "#ff9f43", "#3fe0d6", "#ff7ad9", "#c9e265", "#ffd166", "#8fa8ff", "#f78c6b", "#7ee8c7"];
  const PREFIX = "ruee-or-dvm-";
  const QTIME = 30, ETIME = 20, DTIME = 10, RTIME = 30, FTIME = 40;
  const F_CHOOSE = 15000, F_LOAD = 20000; // filon: time to sign up, then the longest wait for everybody's question to load
  const KIND = { normal: "", filon: "Filon", raid: "Chapardage", duel: "Castagne", rescue: "Sauvetage" };
  const params = new URLSearchParams(location.search);
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    del(k) { try { localStorage.removeItem(k); } catch (e) {} },
  };
  // PeerJS options; ?peerhost=… lets a test use its own signalling server
  function peerOpts() {
    const o = { debug: 0, config: { iceServers: [{ urls: "stun:stun.l.google.com:19302" }, { urls: "stun:stun1.l.google.com:19302" }] } };
    if (params.get("peerhost")) {
      o.host = params.get("peerhost"); o.port = +(params.get("peerport") || 9000);
      o.path = params.get("peerpath") || "/"; o.secure = params.get("peersecure") === "1";
    }
    return o;
  }
  const extraQS = () => ["peerhost", "peerport", "peerpath", "peersecure"].filter(k => params.get(k)).map(k => `&${k}=${encodeURIComponent(params.get(k))}`).join("");

  function level(key) {
    const L = D.LEVELS[key] || D.LEVELS["5e"];
    const ANSWER = {}, THEME_OF = {};
    L.qs.forEach(([n, th, l]) => { ANSWER[n] = l; THEME_OF[n] = th; });
    return Object.assign({}, L, { key, ANSWER, THEME_OF, twin: n => n > L.half ? n - L.half : n + L.half });
  }

  const credit = `<div class="credit"><span class="cl">©</span> Copyleft Denis Vanmai, avec l'aide de mon ami Claude</div>`;
  function header(sub, extra) {
    return `<header class="top"><div><h1>La Ruée vers l'Or</h1><div class="sub">${sub}</div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">${extra || ""}</div></header>`;
  }
  const segs = (id, vals, cur, lab) => `<div class="seg" id="${id}" role="group">${vals.map(v => `<button type="button" data-v="${v}" aria-pressed="${String(v) === String(cur)}">${lab ? lab(v) : v}</button>`).join("")}</div>`;
  const bindSeg = (id, fn) => document.querySelectorAll(`#${id} button`).forEach(b => { b.onclick = () => fn(b.dataset.v); });
  function rulesHTML() {
    return `<div class="rules">
      <div class="rule"><span class="big">0</span><span>Mauvaise réponse ou temps écoulé : aucune pépite.</span></div>
      <div class="rule"><span class="big">1 ${NUG}</span><span>Bonne réponse à une question normale.</span></div>
      <div class="rule rescue"><span class="big">2 ${NUG}</span><span>Sauvetage : deux joueurs refont chacun une question ratée, jusqu'à 2 pépites chacun. Entraidez-vous !</span></div>
      <div class="rule duel"><span class="big">2 ${NUG}</span><span>Castagne : deux joueurs s'affrontent pour 2 pépites, chacun sur son téléphone.</span></div>
      <div class="rule raid"><span class="big">3 ${NUG}</span><span>Chapardage : tu prends 3 pépites au joueur le plus riche.</span></div>
      <div class="rule ch"><span class="big">4 ${NUG}</span><span>Filon : le joueur gagne 4 pépites s'il répond juste. Les autres peuvent tenter la même question : 1 pépite pour ceux qui trouvent, si le joueur du filon trouve aussi.</span></div>
    </div>`;
  }

  /* ---------- question images (packs of 10, loaded on demand) ---------- */
  const packWait = {};
  function loadPack(key) {
    if ((window.IMGPACK || {})[key]) return Promise.resolve();
    if (!packWait[key]) packWait[key] = new Promise((ok, ko) => {
      const sc = document.createElement("script");
      sc.src = "packs/" + key + ".js"; sc.onload = ok;
      sc.onerror = () => { delete packWait[key]; ko(new Error("pack")); };
      document.head.appendChild(sc);
    });
    return packWait[key];
  }
  function setImg(im, img, n) {
    const key = img + "_" + Math.floor((n - 1) / 10);
    return loadPack(key).then(() => {
      im.src = window.IMGPACK[key][n];
      return im.decode ? im.decode().catch(() => {}) : null;
    });
  }

  /* ---------- menu ---------- */
  function renderMenu() {
    app.innerHTML = header("Chercheurs d'or · partie en réseau") + `
      <div class="setup">
        <section class="panel"><h2>Le principe</h2>
          <p>Chaque chercheur d'or répond à ses questions sur son téléphone, à son rythme. Une bonne réponse rapporte des pépites. De temps en temps, les joueurs peuvent tomber sur des événements spéciaux.</p>
          ${rulesHTML()}
        </section>
        <section class="panel menu"><h2>Jouer</h2>
          <button class="primary" id="mHost">Créer une partie (professeur)</button>
          <p>À ouvrir sur l'ordinateur relié au tableau : un code et un QR code s'affichent, puis le classement en direct.</p>
          <button class="primary" id="mJoin">Rejoindre une partie (élève)</button>
          <p>Sur le téléphone : scanne le QR code ou tape le code affiché au tableau.</p>
          <a class="primary" href="tableau.html" style="text-align:center;text-decoration:none">Jouer en ligne au tableau (un seul écran)</a>
          <p>Le même jeu que la version hors ligne, directement en ligne : les joueurs répondent chacun leur tour au tableau, sans téléphone.</p>
          <button class="primary" id="mOff">Télécharger la version hors ligne</button>
          <p>Le jeu au tableau (5ème, Terminale, CAPES) dans un fichier zip : on le décompresse, puis on ouvre <strong>jouer.html</strong>, même sans internet.</p>
          <div id="offst" aria-live="polite"></div>
        </section>
      </div>` + credit;
    $("#mHost").onclick = () => Host.init();
    $("#mJoin").onclick = () => Student.init("");
    $("#mOff").onclick = downloadOffline;
  }

  /* ---------- offline version: zip built in the browser from the site's own files ---------- */
  function loadScript(src) {
    return new Promise((ok, ko) => { const sc = document.createElement("script"); sc.src = src; sc.onload = ok; sc.onerror = ko; document.head.appendChild(sc); });
  }
  async function downloadOffline() {
    const btn = $("#mOff"), st = $("#offst");
    const show = (pct, txt) => { st.innerHTML = `<div class="bar" style="margin-top:4px"><i style="width:${pct}%"></i></div><p style="margin-top:6px">${txt}</p>`; };
    btn.disabled = true;
    try {
      if (!window.JSZip) await loadScript("lib/jszip.min.js");
      const files = [];
      Object.values(D.LEVELS).forEach(L => { for (let k = 0; k * 10 < L.qs.length; k++) files.push(`packs/${L.img}_${k}.js`); });
      const zip = new JSZip(), dir = zip.folder("La_Ruee_vers_l_Or_hors_ligne");
      const site = location.origin + location.pathname.replace(/[^/]*$/, "");
      const get = async f => { const r = await fetch(f, { cache: "no-cache" }); if (!r.ok) throw new Error(f); return r.text(); };
      show(0, "Préparation…");
      // the board game; its link to the network game points to this site
      let html = await get("tableau.html");
      html = html.replace(/href="index\.html"/g, `href="${site}"`);
      dir.file("jouer.html", html);
      let done = 0;
      for (let i = 0; i < files.length; i += 6) {
        await Promise.all(files.slice(i, i + 6).map(async f => { dir.file(f, await get(f)); done++; }));
        show(Math.round(done / files.length * 90), `Téléchargement des questions… ${done} / ${files.length}`);
      }
      dir.file("LISEZMOI.txt", "La Ruée vers l'Or - version hors ligne\r\n\r\n" +
        "1. Décompresser ce dossier (clic droit > Extraire tout).\r\n" +
        "2. Ouvrir jouer.html avec un navigateur (Chrome, Firefox, Edge, Safari).\r\n" +
        "3. Choisir le niveau (5ème, Terminale, CAPES) et jouer au tableau, même sans internet.\r\n\r\n" +
        "La partie en réseau sur téléphones demande internet : " + site + "\r\n\r\n" +
        "Copyleft Denis Vanmai, avec l'aide de mon ami Claude\r\n");
      show(92, "Création du fichier zip…");
      const blob = await zip.generateAsync({ type: "blob", compression: "DEFLATE", compressionOptions: { level: 6 } }, m => show(92 + Math.round(m.percent * 0.08), "Création du fichier zip…"));
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = "La_Ruee_vers_l_Or_hors_ligne.zip";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 60000);
      show(100, `C'est prêt : le fichier <strong>La_Ruee_vers_l_Or_hors_ligne.zip</strong> (${Math.round(blob.size / 1e6)} Mo) est dans vos téléchargements.`);
    } catch (e) {
      st.innerHTML = '<div class="feedback ko">Le téléchargement a échoué. Vérifiez la connexion internet et réessayez.</div>';
    }
    btn.disabled = false;
  }

  /* =====================================================================
     HOST (teacher)
     ===================================================================== */
  const Host = (() => {
    const KEY = "ruee-host";
    let H = null, L = null, peer = null, conns = {}, tries = 0, statusText = "", showQR = false, renderT = null;
    const save = () => store.set(KEY, H);
    const players = () => Object.values(H.players);
    const sorted = () => players().sort((a, b) => b.score - a.score || a.join - b.join);
    const rankOf = p => 1 + players().filter(o => o.score > p.score).length;
    const newId = () => Math.random().toString(36).slice(2, 10);
    const joinURL = () => location.origin + location.pathname + "?p=" + H.code + extraQS();
    const nOf = p => p.deck.length || H.nQ;

    function init() {
      try { history.replaceState(null, "", location.pathname + "?prof" + extraQS()); } catch (e) {}
      const old = store.get(KEY);
      if (old && old.phase !== "end" && old.code && Object.keys(old.players || {}).length) {
        app.innerHTML = header("Professeur") + `<section class="panel joinbox"><h2>Partie en cours</h2>
          <p>Une partie (code <strong>${esc(old.code)}</strong>, ${Object.keys(old.players).length} joueur${Object.keys(old.players).length > 1 ? "s" : ""}) n'est pas terminée.</p>
          <button class="primary" id="resume">Reprendre cette partie</button>
          <button class="ghost" id="fresh">Nouvelle partie</button></section>` + credit;
        $("#resume").onclick = () => { H = old; L = level(H.level); players().forEach(p => { p.online = false; }); connect(); };
        $("#fresh").onclick = () => { store.del(KEY); newGame(); };
        return;
      }
      newGame();
    }
    function newCode() { const A = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"; return Array.from({ length: 5 }, () => A[Math.floor(Math.random() * A.length)]).join(""); }
    function newGame() {
      if (peer) { try { peer.destroy(); } catch (e) {} peer = null; }
      conns = {};
      H = { code: newCode(), level: (H && H.level) || "5e", nQ: (H && H.nQ) || 20, series: (H && H.series) || "A", themes: null, phase: "lobby", players: {}, links: {}, feed: [], seq: 0 };
      L = level(H.level);
      H.themes = Object.fromEntries(L.themes.map(t => [t.id, true]));
      save(); connect();
    }

    function setStatus(t) { statusText = t; const el = $("#hstatus"); if (el) { el.textContent = t; el.hidden = !t; } }
    function connect() {
      if (peer) { try { peer.destroy(); } catch (e) {} }
      if (!window.Peer) { statusText = "La bibliothèque de connexion n'a pas pu se charger."; render(); return; }
      statusText = "Connexion au serveur…"; render();
      const me = peer = new Peer(PREFIX + H.code, peerOpts());
      me.on("open", () => { if (peer !== me) return; tries = 0; setStatus(""); render(); });
      me.on("connection", c => { if (peer === me) onConn(c); });
      me.on("disconnected", () => {
        if (peer !== me || me.destroyed) return;
        setStatus("Connexion au serveur perdue, reconnexion…");
        setTimeout(() => { if (peer === me && !me.destroyed) { try { me.reconnect(); } catch (e) {} } }, 1500);
      });
      me.on("error", e => {
        if (peer !== me) return;
        if (e.type === "peer-unavailable") return;
        if (e.type === "unavailable-id") {
          if (H.phase === "lobby" && !players().length) { H.code = newCode(); save(); return setTimeout(connect, 200); }
          if (tries++ < 30) { setStatus("Le code de la partie se libère, nouvelle tentative…"); return setTimeout(connect, 3000); }
        }
        setStatus("Problème de connexion (" + e.type + "). Vérifiez la connexion internet ; nouvelle tentative…");
        if (["network", "server-error", "socket-error", "socket-closed"].includes(e.type)) setTimeout(() => { if (peer === me) connect(); }, 4000);
      });
    }
    function onConn(c) {
      c.on("data", m => { try { onMsg(c, m); } catch (e) { console.error(e); } });
      c.on("close", () => {
        const pid = c._pid;
        if (pid && conns[pid] === c) { delete conns[pid]; const p = H.players[pid]; if (p) { p.online = false; save(); render(); } }
      });
      c.on("error", () => {});
    }
    function send(pid, m) { const c = conns[pid]; if (c && c.open) { try { c.send(m); } catch (e) {} } }
    function toast(pid, text) { send(pid, { t: "toast", text }); }

    function viewOf(p) {
      const v = { t: "view", phase: H.phase, code: H.code, img: L.img, sub: L.sub,
        me: { pid: p.pid, name: p.name, color: p.color, score: p.score, rank: rankOf(p), n: players().length, k: p.k, N: nOf(p) },
        q: null, res: p.res, done: false, started: p.k > 0 || !!p.cur || !!p.res };
      if (p.cur) v.q = { id: p.cur.id, n: p.cur.q, kind: p.cur.kind, time: p.cur.time, partner: p.cur.partner || null, th: p.cur.thLabel || null, victim: p.cur.victimName || null, num: p.cur.num || null, stake: p.cur.stake };
      v.done = H.phase === "play" && !p.cur && !p.pending && p.k >= nOf(p);
      // filons of the other players: sign up, wait for everybody to load, then answer together
      v.filons = H.phase !== "play" ? [] : Object.values(H.filons || {}).filter(f => f.open && f.a !== p.pid && H.players[f.a])
        .map(f => ({ id: f.id, from: H.players[f.a].name, stage: f.stage, left: Math.max(0, f.until - Date.now()),
          joined: f.joins[p.pid], loaded: !!f.loaded[p.pid], tried: f.tries[p.pid] !== undefined,
          n: f.stage !== "choose" && f.joins[p.pid] === true ? f.q : null, ...filonCounts(f) }));
      if (p.cur && p.cur.kind === "filon" && H.filons && H.filons[p.cur.filon]) {
        const f = H.filons[p.cur.filon];
        Object.assign(v.q, { fid: f.id, fstage: f.stage, fleft: Math.max(0, f.until - Date.now()), ...filonCounts(f) });
      }
      if (H.phase === "end") v.ranking = sorted().map(o => ({ name: o.name, color: o.color, score: o.score, rank: rankOf(o) }));
      return v;
    }
    function push(pid) { const p = H.players[pid]; if (p) send(pid, viewOf(p)); }
    function pushAll() { players().forEach(p => push(p.pid)); }
    function feed(text, kind) { H.feed.unshift({ text, kind: kind || "" }); H.feed.length = Math.min(H.feed.length, 40); }

    function onMsg(c, m) {
      if (!m || typeof m !== "object") return;
      if (m.t === "hello") {
        let p = m.pid && H.players[m.pid];
        if (!p) {
          if (H.phase === "end") { c.send({ t: "view", phase: "end", sub: L.sub, me: null, ranking: sorted().map(o => ({ name: o.name, color: o.color, score: o.score, rank: rankOf(o) })) }); return; }
          let name = String(m.name || "").replace(/\s+/g, " ").trim().slice(0, 18) || "Chercheur";
          const taken = new Set(players().map(o => o.name.toLowerCase()));
          const base = name; let i = 2;
          while (taken.has(name.toLowerCase())) name = base + " " + i++;
          H.seq++;
          const pid = "p" + H.seq + newId();
          p = H.players[pid] = { pid, name, color: PCOL[(H.seq - 1) % PCOL.length], join: H.seq, score: 0, ok: 0, tot: 0, ch: 0, vols: 0, duels: 0, saves: 0,
            k: 0, deck: H.phase === "play" ? makeDeck() : [], solved: [], failed: [], cur: null, res: null, pending: null, online: true };
          if (H.phase === "play") feed(`${name} rejoint la partie.`);
        }
        if (conns[p.pid] && conns[p.pid] !== c) { try { conns[p.pid].close(); } catch (e) {} }
        c._pid = p.pid; conns[p.pid] = c; p.online = true;
        save(); push(p.pid); render();
        return;
      }
      const p = c._pid && H.players[c._pid];
      if (!p) return;
      if (m.t === "fjoin") {
        const f = (H.filons || {})[m.id];
        if (f && f.open && f.stage === "choose" && f.a !== p.pid && f.joins[p.pid] === undefined) {
          f.joins[p.pid] = !!m.yes; save(); filonTick();
        }
        pushAll(); render(); return;
      }
      if (m.t === "floaded") {
        const f = (H.filons || {})[m.id];
        if (f && f.open && (f.a === p.pid || f.joins[p.pid] === true) && !f.loaded[p.pid]) { f.loaded[p.pid] = true; save(); filonTick(); pushAll(); }
        return;
      }
      if (m.t === "ftry") {
        const f = (H.filons || {})[m.id];
        if (f && f.open && f.stage === "play" && f.joins[p.pid] === true && f.loaded[p.pid] && f.a !== p.pid && f.tries[p.pid] === undefined) {
          f.tries[p.pid] = ["a", "b", "c", "d"].includes(m.l) ? m.l : null;
          save();
        }
        push(p.pid); render();
      }
      else if (m.t === "next") nextFor(p);
      else if (m.t === "ans") answerFor(p, m.id, m.l);
    }

    /* ----- questions ----- */
    function pool() {
      const inS = n => H.series === "AB" || (H.series === "B" ? n > L.half : n <= L.half);
      return L.qs.filter(([n, th]) => H.themes[th] && inS(n)).map(x => x[0]);
    }
    function makeDeck() { return shuffle(pool()).slice(0, H.nQ); }
    const solvedIn = (o, th) => [...new Set(o.solved)].filter(n => L.THEME_OF[n] === th);
    const missedOf = o => { const sv = new Set(o.solved); return [...new Set(o.failed)].filter(n => !sv.has(n) && !sv.has(L.twin(n))); };
    // a partner must still have questions to ask for, so that the pending one is served
    const canPartner = (o, p) => o !== p && !o.pending && o.k < nOf(o) && o.online;
    function filonChance(p) {
      const n = players().length;
      if (n === 1) return 1 / 8;
      const above = players().filter(o => o.score > p.score).length;
      return 0.25 * above / (n - 1);
    }
    function leaderFor(p) {
      const order = sorted();
      if (order.length < 2) return null;
      const first = order[0];
      if (first.score - order[1].score < 2 || first === p) return null;
      return first;
    }
    function makeDuel(p, cur) {
      const opts = [];
      players().forEach(o => {
        if (!canPartner(o, p)) return;
        L.themes.forEach(({ id }) => { if (solvedIn(p, id).length && solvedIn(o, id).length) opts.push([o, id]); });
      });
      if (!opts.length) return false;
      const [o, th] = pick(opts);
      const lid = newId(), thLabel = L.themes.find(t => t.id === th).label;
      H.links[lid] = { id: lid, type: "duel", a: p.pid, b: o.pid, ra: null, rb: null, done: false };
      Object.assign(cur, { q: L.twin(pick(solvedIn(p, th))), kind: "duel", time: DTIME, stake: 2, link: lid, partner: o.name, thLabel });
      o.pending = { q: L.twin(pick(solvedIn(o, th))), kind: "duel", time: DTIME, stake: 2, link: lid, partner: p.name, thLabel, extra: true };
      feed(`Castagne : ${p.name} défie ${o.name} (${thLabel}).`, "duel");
      toast(o.pid, `${p.name} te défie en castagne ! Elle arrive à ta prochaine question.`);
      return true;
    }
    function makeRescue(p, cur) {
      const mine = missedOf(p);
      if (!mine.length) return false;
      const partners = players().filter(o => canPartner(o, p) && missedOf(o).length);
      if (!partners.length) return false;
      const o = pick(partners), lid = newId();
      H.links[lid] = { id: lid, type: "rescue", a: p.pid, b: o.pid, ra: null, rb: null, done: false };
      Object.assign(cur, { q: L.twin(pick(mine)), kind: "rescue", time: RTIME, stake: 2, link: lid, partner: o.name });
      o.pending = { q: L.twin(pick(missedOf(o))), kind: "rescue", time: RTIME, stake: 2, link: lid, partner: p.name, extra: true };
      feed(`Sauvetage : ${p.name} et ${o.name} font équipe.`, "rescue");
      toast(o.pid, `Sauvetage avec ${p.name} ! Il arrive à ta prochaine question.`);
      return true;
    }
    function makeFilon(p, cur) {
      const missed = missedOf(p);
      let q;
      if (missed.length) q = L.twin(pick(missed));
      else { const used = new Set(p.deck); const pl = pool().filter(n => !used.has(n)); q = pl.length ? pick(pl) : cur.q; }
      const fid = newId();
      H.filons = H.filons || {};
      H.filons[fid] = { id: fid, a: p.pid, q, tries: {}, open: true, stage: "choose", joins: {}, loaded: {}, until: Date.now() + F_CHOOSE };
      Object.assign(cur, { q, kind: "filon", time: FTIME, stake: 4, filon: fid });
    }

    function nextFor(p) {
      if (H.phase !== "play" || p.cur) { push(p.pid); return; }
      p.res = null;
      if (p.pending) {
        p.cur = Object.assign(p.pending, { id: newId() }); p.pending = null;
        save(); push(p.pid); render(); return;
      }
      if (p.k >= nOf(p)) { push(p.pid); render(); checkAllDone(); return; }
      const k = p.k++;
      const cur = { id: newId(), q: p.deck[k], kind: "normal", time: QTIME, stake: 1, num: k + 1 };
      const n = players().length, f = Math.min(1, 4 / n); // big classes: thefts and filons stay as frequent as with 4 players
      let done = false;
      if (n > 1 && k >= 2) {
        const u = Math.random(), pr = f / 6;
        if (u < pr) {
          const v = leaderFor(p);
          if (v) { Object.assign(cur, { kind: "raid", time: ETIME, victim: v.pid, victimName: v.name, stake: Math.min(3, v.score) }); done = true; }
        } else if (k >= 3 && u < pr + 1 / 8) done = makeDuel(p, cur);
        else if (k >= 3 && u < pr + 1 / 8 + 1 / 12) done = makeRescue(p, cur);
      }
      if (!done && k >= 2 && (window.__forceFilon || Math.random() < filonChance(p) * (n > 1 ? f : 1))) { window.__forceFilon = false; makeFilon(p, cur); }
      if (cur.kind === "raid") feed(`${p.name} tente un chapardage sur ${cur.victimName}…`, "raid");
      if (cur.kind === "filon") feed(`${p.name} a trouvé un filon !`, "filon");
      p.cur = cur;
      save(); if (cur.kind === "filon") pushAll(); else push(p.pid); render();
    }

    function answerFor(p, id, l) {
      const c = p.cur;
      if (!c || c.id !== id) { push(p.pid); return; }
      if (c.kind === "filon" && H.filons && H.filons[c.filon] && H.filons[c.filon].stage !== "play") { push(p.pid); return; }
      p.cur = null;
      l = ["a", "b", "c", "d"].includes(l) ? l : null;
      const right = L.ANSWER[c.q], ok = l === right;
      p.tot++;
      if (ok) { p.ok++; p.solved.push(c.q); } else p.failed.push(c.q);
      const R = right.toUpperCase();
      let text, wait = false, good = ok, changed = false;
      if (c.kind === "filon") {
        const winners = closeFilon(c.filon, ok);
        changed = true;
        if (ok) {
          p.score += 4; p.ch++;
          feed(`Filon exploité par ${p.name} : +4 pépites${winners.length ? `, et +1 pour ${winners.join(", ")}` : ""} !`, "filon");
          text = "Filon exploité ! +4 pépites." + (winners.length ? ` ${winners.length} chercheur${winners.length > 1 ? "s ont" : " a"} aussi trouvé : +1 pépite chacun.` : "");
        } else {
          feed(`${p.name} a raté son filon.`, "filon");
          text = (l ? "Raté ! " : "Temps écoulé ! ") + `Le filon t'échappe. La bonne réponse était ${R}.`;
        }
      } else if (c.kind === "raid") {
        const v = H.players[c.victim];
        if (ok && v) {
          const k = Math.min(3, v.score); v.score -= k; p.score += k; p.vols++; changed = true;
          toast(v.pid, `${p.name} t'a chapardé ${k} pépite${k > 1 ? "s" : ""} !`);
          feed(`${p.name} chaparde ${k} pépite${k > 1 ? "s" : ""} à ${v.name}.`, "raid");
          text = `Coup réussi ! Tu chapardes ${k} pépite${k > 1 ? "s" : ""} à ${v.name}.`;
        } else if (v && p.score > 0) {
          p.score -= 1; v.score += 1; changed = true;
          toast(v.pid, `${p.name} a raté son chapardage : il te paie 1 pépite d'amende.`);
          feed(`Le shérif veille : ${p.name} paie 1 pépite d'amende à ${v.name}.`, "raid");
          text = `Pris la main dans le sac ! La bonne réponse était ${R}. Tu paies 1 pépite d'amende à ${v.name}.`;
        } else text = `Pris la main dans le sac ! La bonne réponse était ${R}. Tu n'as pas de pépite pour payer l'amende.`;
      } else if (c.kind === "duel" || c.kind === "rescue") {
        const lk = H.links[c.link];
        if (lk && !lk.done) {
          if (lk.a === p.pid) lk.ra = { ok }; else lk.rb = { ok };
          text = (ok ? "Bonne réponse ! " : l ? `Raté ! La bonne réponse était ${R}. ` : `Temps écoulé ! La bonne réponse était ${R}. `) +
            `Le résultat ${c.kind === "duel" ? "de la castagne" : "du sauvetage"} arrive quand ${c.partner} aura répondu.`;
          wait = true;
        } else text = ok ? "Bonne réponse !" : `La bonne réponse était ${R}.`;
      } else {
        if (ok) { p.score += 1; changed = true; }
        text = ok ? "Bien joué ! +1 pépite." : l ? `Raté ! La bonne réponse était ${R}.` : `Temps écoulé ! La bonne réponse était ${R}.`;
      }
      p.res = { qid: c.id, n: c.q, kind: c.kind, choice: l, right, ok: good, text, wait, link: c.link || null };
      const lk = c.link && H.links[c.link];
      if (lk && !lk.done && lk.ra && lk.rb) resolveLink(lk);
      save();
      if (changed || (lk && lk.done)) pushAll(); else push(p.pid);
      render(); checkAllDone();
    }

    // filon stages: "choose" (15 s to sign up) -> "load" (everybody loads the question, hidden) -> "play" (shown to all at once)
    const filonNeed = f => [f.a, ...Object.keys(f.joins).filter(pid => f.joins[pid] === true && H.players[pid] && H.players[pid].online)];
    function filonCounts(f) {
      const need = f.stage === "choose" ? [] : filonNeed(f);
      return { nPart: Object.values(f.joins).filter(x => x === true).length, nNeed: need.length, nReady: need.filter(pid => f.loaded[pid]).length };
    }
    function filonTick() {
      if (!H || H.phase !== "play") return;
      let changed = false;
      Object.values(H.filons || {}).forEach(f => {
        if (!f.open) return;
        if (f.stage === "choose") {
          const others = players().filter(o => o.pid !== f.a && o.online);
          if (Date.now() >= f.until || others.every(o => f.joins[o.pid] !== undefined)) {
            f.stage = "load"; f.until = Date.now() + F_LOAD; changed = true;
            const names = Object.keys(f.joins).filter(pid => f.joins[pid] === true).map(pid => H.players[pid] && H.players[pid].name).filter(Boolean);
            const A = H.players[f.a];
            if (A) feed(names.length ? `Filon de ${A.name} : ${names.join(", ")} ${names.length > 1 ? "participent" : "participe"}.` : `Filon de ${A.name} : personne ne participe.`, "filon");
          }
        }
        if (f.stage === "load") {
          const need = filonNeed(f);
          if (need.every(pid => f.loaded[pid]) || Date.now() >= f.until) {
            f.stage = "play"; changed = true;
            need.forEach(pid => { if (!f.loaded[pid] && pid !== f.a) { f.joins[pid] = false; toast(pid, "La question du filon n'a pas pu se charger à temps : tu ne participes pas à ce filon."); } });
          }
        }
      });
      if (changed) { save(); pushAll(); render(); }
    }
    setInterval(filonTick, 500);

    // close a filon: the others who found the answer get 1 nugget, only if the owner found it too
    function closeFilon(fid, ownerOk) {
      const f = (H.filons || {})[fid], winners = [];
      if (!f || !f.open) return winners;
      f.open = false;
      const A = H.players[f.a], right = L.ANSWER[f.q], R = right.toUpperCase(), who = A ? A.name : "le joueur du filon";
      Object.entries(f.tries).forEach(([pid, l]) => {
        const o = H.players[pid]; if (!o) return;
        const okO = l === right;
        if (okO && ownerOk) { o.score += 1; o.fa = (o.fa || 0) + 1; winners.push(o.name); toast(pid, `Filon de ${who} : vous avez trouvé tous les deux, +1 pépite !`); }
        else if (okO) toast(pid, `Filon de ${who} : tu avais trouvé (${R}), mais ${who} s'est trompé. Pas de pépite.`);
        else toast(pid, `Filon de ${who} : raté, la bonne réponse était ${R}. Pas de pépite.`);
      });
      return winners;
    }

    function resolveLink(lk) {
      lk.done = true;
      const A = H.players[lk.a], B = H.players[lk.b];
      if (!A || !B) return;
      const a = !!(lk.ra && lk.ra.ok), b = !!(lk.rb && lk.rb.ok);
      let ga, gb, ta, tb;
      if (lk.type === "duel") {
        if (a && b) ga = gb = 1; else if (a) { ga = 2; gb = 0; } else if (b) { ga = 0; gb = 2; } else ga = gb = 0;
        if (ga > gb) A.duels++; if (gb > ga) B.duels++;
        const msg = (g, og, other) => g > og ? `Castagne gagnée contre ${other} : +${g} pépites !`
          : g === og ? (g ? `Castagne : ${other} et toi avez juste, +1 pépite chacun.` : `Castagne contre ${other} : personne n'a juste, pas de pépite.`)
          : `Castagne perdue contre ${other}.`;
        ta = msg(ga, gb, B.name); tb = msg(gb, ga, A.name);
        feed(ga > gb ? `${A.name} gagne la castagne contre ${B.name}.` : gb > ga ? `${B.name} gagne la castagne contre ${A.name}.` : ga ? `Castagne ${A.name} – ${B.name} : égalité, +1 chacun.` : `Castagne ${A.name} – ${B.name} : personne n'a juste.`, "duel");
      } else {
        const nOk = (a ? 1 : 0) + (b ? 1 : 0);
        ga = gb = nOk;
        if (nOk) { A.saves++; B.saves++; }
        const t = nOk === 2 ? "deux bonnes réponses, +2 pépites chacun !" : nOk === 1 ? "une bonne réponse, +1 pépite chacun." : "aucune bonne réponse, pas de pépite.";
        ta = `Sauvetage avec ${B.name} : ${t}`; tb = `Sauvetage avec ${A.name} : ${t}`;
        feed(`Sauvetage ${A.name} – ${B.name} : ${t}`, "rescue");
      }
      A.score += ga; B.score += gb;
      [[A, ta], [B, tb]].forEach(([P, t]) => {
        if (P.res && P.res.link === lk.id) {
          P.res.wait = false;
          P.res.text = P.res.text.replace(/Le résultat .*$/, "") + t;
        } else toast(P.pid, t);
      });
    }

    function allDone() { return players().length > 0 && players().every(p => !p.cur && !p.pending && p.k >= nOf(p)); }
    function checkAllDone() {
      if (H.phase === "play" && allDone() && !H.allDoneSaid) { H.allDoneSaid = true; feed("Tous les chercheurs ont fini leurs questions !"); setTimeout(() => { if (H.phase === "play" && allDone()) endGame(); }, 1500); }
    }
    function startGame() {
      const err = $("#herr");
      if (!pool().length) { if (err) err.textContent = "Coche au moins un thème."; return; }
      if (!players().length) { if (err) err.textContent = "Attends qu'au moins un élève ait rejoint la partie."; return; }
      H.phase = "play";
      players().forEach(p => Object.assign(p, { deck: makeDeck(), k: 0, score: 0, ok: 0, tot: 0, ch: 0, fa: 0, vols: 0, duels: 0, saves: 0, solved: [], failed: [], cur: null, res: null, pending: null }));
      H.links = {}; H.filons = {}; H.feed = []; H.allDoneSaid = false;
      feed("La partie commence !");
      save(); pushAll(); render();
    }
    function endGame() {
      Object.values(H.links).forEach(lk => { if (!lk.done) { lk.ra = lk.ra || { ok: false }; lk.rb = lk.rb || { ok: false }; resolveLink(lk); } });
      Object.keys(H.filons || {}).forEach(fid => closeFilon(fid, false));
      players().forEach(p => { p.cur = null; p.pending = null; });
      H.phase = "end";
      save(); pushAll(); render();
    }

    /* ----- views ----- */
    function render() {
      clearTimeout(renderT);
      renderT = setTimeout(draw, 60); // many messages can arrive together: draw once
    }
    function statusHTML() { return `<div class="status" id="hstatus" ${statusText ? "" : "hidden"}>${esc(statusText)}</div>`; }
    function qrHTML() {
      try { const q = qrcode(0, "M"); q.addData(joinURL()); q.make(); return q.createSvgTag({ cellSize: 6, margin: 2, scalable: true, alt: "QR code pour rejoindre la partie" }); }
      catch (e) { return ""; }
    }
    function draw() {
      if (!H) return;
      if (H.phase === "lobby") drawLobby();
      else if (H.phase === "play") drawLive();
      else drawEnd();
    }
    function drawLobby() {
      const ps = players();
      app.innerHTML = header(`Professeur · ${esc(L.sub)}`, statusHTML()) + `
        <div class="lobby">
          <section class="panel joinpanel">
            <h2>Rejoindre la partie</h2>
            <p>Scanne le QR code avec ton téléphone, ou va sur l'adresse ci-dessous et tape le code.</p>
            <div class="codebig" aria-label="Code de la partie">${esc(H.code)}</div>
            <div class="qr">${qrHTML()}</div>
            <div class="url">${esc(location.origin + location.pathname)}</div>
          </section>
          <section class="panel setup1">
            <h2>Préparer la partie</h2>
            <label class="f">Niveau ${segs("lv", Object.keys(D.LEVELS), H.level, v => D.LEVELS[v].label)}</label>
            <label class="f">Questions par joueur ${segs("nq", [10, 20, 40], H.nQ)}</label>
            <label class="f">Série de questions ${segs("se", ["A", "B", "AB"], H.series, v => v === "AB" ? "A et B" : "Série " + v)}</label>
            <div class="f"><span style="font-weight:700;font-size:15px">Thèmes</span>
              <div class="checks">${L.themes.map(t => `<label><input type="checkbox" data-th="${t.id}" ${H.themes[t.id] ? "checked" : ""}> ${esc(t.label)}</label>`).join("")}</div></div>
            <div class="f"><span style="font-weight:700;font-size:15px">Joueurs connectés : ${ps.length}</span>
              <div class="chips">${ps.length ? ps.map(p => `<span class="chip ${p.online ? "" : "off"}" style="--pc:${p.color}">${esc(p.name)}</span>`).join("") : '<span class="muted">En attente des élèves…</span>'}</div></div>
            <button class="primary" id="hgo">Lancer la partie</button>
            <div class="err" id="herr"></div>
          </section>
        </div>` + credit;
      bindSeg("lv", v => { if (v === H.level) return; H.level = v; L = level(v); H.themes = Object.fromEntries(L.themes.map(t => [t.id, true])); save(); pushAll(); draw(); });
      bindSeg("nq", v => { H.nQ = +v; save(); draw(); });
      bindSeg("se", v => { H.series = v; save(); draw(); });
      app.querySelectorAll("[data-th]").forEach(cb => { cb.onchange = () => { H.themes[cb.dataset.th] = cb.checked; save(); }; });
      $("#hgo").onclick = startGame;
    }
    function tagOf(p) {
      if (p.cur && p.cur.kind !== "normal") return `<span class="tag ${p.cur.kind === "filon" ? "filon" : p.cur.kind}">${KIND[p.cur.kind]}</span>`;
      if (!p.online) return `<span class="tag off">Hors ligne</span>`;
      if (!p.cur && !p.pending && p.k >= nOf(p)) return `<span class="tag done">Fini</span>`;
      return "";
    }
    function drawLive() {
      const ps = sorted();
      const box = $("#lbwrap");
      const rows = ps.map(p => `<li class="lbrow" style="--pc:${p.color}">
          <span class="pos">${rankOf(p)}</span>
          <span style="min-width:0"><span class="nm">${esc(p.name)}</span>${tagOf(p)}
            <span class="prog" aria-label="${Math.min(p.k, nOf(p))} questions sur ${nOf(p)}"><i style="width:${Math.min(100, p.k / nOf(p) * 100)}%"></i></span></span>
          <span class="pts">${p.score} ${NUG}</span></li>`).join("");
      const feedHTML = H.feed.map(f => `<li class="${f.kind}">${esc(f.text)}</li>`).join("");
      if (box && $("#feed")) { // update in place: the projector page does not flicker
        box.innerHTML = rows; $("#feed").innerHTML = feedHTML; setStatus(statusText);
        $("#pcount").textContent = ps.length; return;
      }
      app.innerHTML = header(`Professeur · ${esc(L.sub)}`, `${statusHTML()}<button class="iconbtn" id="hqr">Code : <strong>${esc(H.code)}</strong></button><button class="iconbtn" id="hend">Terminer la partie</button>`) + `
        <div class="live">
          <section class="panel"><h2>Classement <span class="muted" style="font-family:var(--f-body);font-size:16px">· <span id="pcount">${ps.length}</span> chercheurs</span></h2><ol class="lb" id="lbwrap">${rows}</ol></section>
          <section class="panel"><h2>Événements</h2><ul class="feed" id="feed">${feedHTML}</ul></section>
        </div>` + credit;
      $("#hend").onclick = () => { if (confirmEnd()) endGame(); };
      $("#hqr").onclick = () => {
        const ov = document.createElement("div"); ov.className = "overlay";
        ov.innerHTML = `<div class="box"><div class="codebig">${esc(H.code)}</div><div class="qr">${qrHTML()}</div><div class="url">${esc(location.origin + location.pathname)}</div><button class="primary" id="qrclose">Fermer</button></div>`;
        document.body.appendChild(ov); ov.onclick = e => { if (e.target === ov || e.target.id === "qrclose") ov.remove(); };
      };
    }
    let endArmed = 0;
    function confirmEnd() {
      const b = $("#hend");
      if (Date.now() - endArmed < 4000) return true;
      endArmed = Date.now(); if (b) b.textContent = "Confirmer : terminer ?";
      setTimeout(() => { const b2 = $("#hend"); if (b2) b2.textContent = "Terminer la partie"; }, 4000);
      return false;
    }
    function drawEnd() {
      const ps = sorted();
      app.innerHTML = header(`Professeur · ${esc(L.sub)}`) + `
        <section class="panel"><h2>Classement final</h2>
          <div class="podium">${ps.map(p => { const r = rankOf(p); return `<div class="rank ${r === 1 ? "first" : ""}" style="--pc:${p.color}">
            <span class="pos">${r}</span>
            <span style="min-width:0"><div class="nm">${esc(p.name)}</div>
              <div class="det">${p.ok} / ${p.tot} bonnes réponses · ${p.ch} filon${p.ch > 1 ? "s" : ""} exploité${p.ch > 1 ? "s" : ""} · ${p.fa || 0} filon${(p.fa || 0) > 1 ? "s" : ""} partagé${(p.fa || 0) > 1 ? "s" : ""} · ${p.vols} chapardage${p.vols > 1 ? "s" : ""} réussi${p.vols > 1 ? "s" : ""} · ${p.duels} castagne${p.duels > 1 ? "s" : ""} gagnée${p.duels > 1 ? "s" : ""} · ${p.saves} sauvetage${p.saves > 1 ? "s" : ""} réussi${p.saves > 1 ? "s" : ""}</div></span>
            <span class="pts">${p.score} ${NUG}</span></div>`; }).join("")}</div>
          <button class="primary" id="hnew" style="align-self:flex-start">Nouvelle partie</button>
        </section>` + credit;
      $("#hnew").onclick = () => { store.del(KEY); newGame(); };
    }
    return { init, _state: () => H };
  })();

  /* =====================================================================
     STUDENT (phone)
     ===================================================================== */
  const Student = (() => {
    let peer = null, conn = null, code = "", name = "", V = null, shown = null, timer = null, drawT = [], retry = null, banner = "", joining = false;
    const pidKey = () => "ruee-pid-" + code;

    function init(c) {
      code = String(c || "").toUpperCase().replace(/[^0-9A-Z]/g, "");
      name = store.get("ruee-name") || "";
      if (code && store.get(pidKey())) { join(); return; }
      renderJoin("");
    }
    function renderJoin(err) {
      joining = false;
      app.innerHTML = header("Rejoindre une partie") + `
        <section class="panel joinbox">
          <label class="f">Code de la partie <input id="jc" maxlength="5" autocomplete="off" autocapitalize="characters" spellcheck="false" value="${esc(code)}"></label>
          <label class="f">Ton nom <input id="jn" maxlength="18" autocomplete="nickname" value="${esc(name)}"></label>
          <button class="primary" id="jgo">Rejoindre la partie</button>
          <div class="err" id="jerr" aria-live="polite">${esc(err)}</div>
        </section>` + credit;
      const go = () => {
        code = $("#jc").value.toUpperCase().replace(/[^0-9A-Z]/g, ""); name = $("#jn").value.trim();
        if (code.length !== 5) { $("#jerr").textContent = "Le code a 5 caractères."; return; }
        if (!name) { $("#jerr").textContent = "Écris ton nom."; return; }
        store.set("ruee-name", name); join();
      };
      $("#jgo").onclick = go;
      app.querySelectorAll(".joinbox input").forEach(i => { i.onkeydown = e => { if (e.key === "Enter") go(); }; });
      (code ? $("#jn") : $("#jc")).focus();
    }
    function join() {
      joining = true;
      try { history.replaceState(null, "", location.pathname + "?p=" + code + extraQS()); } catch (e) {}
      app.innerHTML = header("Rejoindre une partie") + `<section class="panel joinbox"><p>Connexion à la partie <strong>${esc(code)}</strong>…</p></section>` + credit;
      open();
    }
    function open() {
      clearTimeout(retry);
      if (peer) { try { peer.destroy(); } catch (e) {} }
      if (!window.Peer) { renderJoin("La connexion n'a pas pu se charger. Recharge la page."); return; }
      const me = peer = new Peer(peerOpts());
      me.on("open", () => {
        if (peer !== me) return;
        const c = conn = me.connect(PREFIX + code, { reliable: true });
        c.on("open", () => { if (conn === c) c.send({ t: "hello", pid: store.get(pidKey()), name }); });
        c.on("data", m => { if (conn === c) { try { onMsg(m); } catch (e) { console.error(e); } } });
        c.on("close", () => { if (conn === c) lost(); });
        c.on("error", () => { if (conn === c) lost(); });
      });
      me.on("error", e => {
        if (peer !== me) return;
        if (e.type === "peer-unavailable" && !V) {
          try { me.destroy(); } catch (_) {}
          peer = null; store.del(pidKey());
          renderJoin("Partie introuvable : vérifie le code. Le professeur doit avoir ouvert la partie.");
          return;
        }
        lost();
      });
      me.on("disconnected", () => { if (peer === me && !me.destroyed) { try { me.reconnect(); } catch (e) {} } });
    }
    function lost() {
      if (!V && !joining) return;
      conn = null;
      setBanner("Connexion perdue… reconnexion en cours.");
      clearTimeout(retry); retry = setTimeout(open, 2500);
    }
    function setBanner(t) { banner = t; const el = $("#sbanner"); if (el) { el.textContent = t; el.hidden = !t; } }
    function send(m) { if (conn && conn.open) { try { conn.send(m); return true; } catch (e) {} } return false; }
    function toast(text) {
      const t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); t.textContent = text;
      document.querySelectorAll(".toast").forEach((o, i) => { o.style.top = (10 + (i + 1) * 64) + "px"; });
      document.body.appendChild(t);
      setTimeout(() => t.remove(), 5000);
    }
    function onMsg(m) {
      if (m.t === "view") {
        setBanner("");
        if (m.me) store.set(pidKey(), m.me.pid);
        V = m; joining = false; render(); renderFilonOffer(); updateFilonOwner();
      } else if (m.t === "toast") toast(m.text);
    }

    /* ----- other players' filons: sign up in a bar, then wait and answer in an overlay ----- */
    let ftry = null; const fskip = {};
    let fdead = {}; // filon id -> local time when its current stage ends
    function busy() { return shown && !shown.answered && shown.q && (shown.q.kind === "duel" || shown.q.kind === "filon"); }
    const secsTo = id => Math.max(0, Math.ceil(((fdead[id] || 0) - Date.now()) / 1000));
    setInterval(() => { document.querySelectorAll("[data-fleft]").forEach(el => { el.textContent = secsTo(el.dataset.fleft); }); }, 250);
    function renderFilonOffer() {
      const offers = (V && V.phase === "play" && V.filons) || [];
      offers.forEach(f => { fdead[f.id] = Date.now() + f.left; });
      if (V && V.q && V.q.fid) fdead[V.q.fid] = Date.now() + V.q.fleft;
      // the filon I take part in
      if (ftry) {
        const f = offers.find(o => o.id === ftry.id);
        updateFilonOverlay(f);
      } else {
        const mine = offers.find(o => o.joined === true && !fskip[o.id]);
        if (mine) { openFilon(mine); return; } // e.g. after reloading the page
      }
      // sign-up bar
      let bar = $("#fbar");
      const f = offers.find(o => o.stage === "choose" && o.joined == null && !fskip[o.id]);
      const show = !!(f && !ftry && !busy());
      document.body.classList.toggle("hasfbar", show);
      if (!show) { if (bar) bar.remove(); return; }
      if (!bar) { bar = document.createElement("div"); bar.id = "fbar"; bar.className = "fbar"; document.body.appendChild(bar); }
      if (bar.dataset.id === f.id) return;
      bar.dataset.id = f.id;
      bar.innerHTML = `<div class="fmsg"><strong>Filon chez ${esc(f.from)} !</strong> Veux-tu participer ? Tu gagnes 1 pépite si vous trouvez tous les deux. Réponds dans <strong data-fleft="${f.id}">${secsTo(f.id)}</strong> s.</div>
        <div class="fbtns"><button class="primary" id="fgo">Je participe</button><button class="ghost" id="fno">Non merci</button></div>`;
      $("#fno").onclick = () => { fskip[f.id] = true; send({ t: "fjoin", id: f.id, yes: false }); renderFilonOffer(); };
      $("#fgo").onclick = () => { send({ t: "fjoin", id: f.id, yes: true }); openFilon(Object.assign({}, f, { joined: true })); };
    }
    function openFilon(f) {
      const bar = $("#fbar"); if (bar) bar.remove();
      document.body.classList.remove("hasfbar");
      ftry = { id: f.id, from: f.from, closed: false, loading: false, ready: false, shownQ: false, answered: false };
      pauseCountdown();
      const ov = document.createElement("div"); ov.className = "overlay fo"; ov.id = "fov";
      ov.innerHTML = `<div class="fobox">
          <div class="title filon" style="font-size:30px">Filon de ${esc(f.from)}</div>
          <div class="board" id="foboard"><span class="ribbon filon">Filon</span>
            <div class="fowait" id="fowait">La question s'affichera en même temps pour tout le monde.</div>
            <img id="foimg" alt="Question du filon : énoncé et réponses a, b, c, d" width="1200" height="1050" style="display:none"></div>
          <div class="answers" id="foans">${["a", "b", "c", "d"].map(l => `<button class="ans" data-l="${l}" disabled>${l.toUpperCase()}</button>`).join("")}</div>
          <div id="fostate" aria-live="polite"></div>
          <button class="ghost" id="foback" hidden>Reprendre ma question</button>
        </div>`;
      document.body.appendChild(ov);
      ov.querySelectorAll("#foans .ans").forEach(b => { b.onclick = () => {
        if (!ftry || ftry.answered) return;
        ftry.answered = true;
        ov.querySelectorAll("#foans .ans").forEach(x => { x.disabled = true; if (x === b) x.classList.add("picked"); });
        send({ t: "ftry", id: ftry.id, l: b.dataset.l });
        $("#fostate").innerHTML = `<div class="feedback ok">Réponse ${b.dataset.l.toUpperCase()} enregistrée ! Résultat quand ${esc(ftry.from)} aura répondu.</div>`;
        showBack();
      }; });
      $("#foback").onclick = () => { const id = ftry && ftry.id; ov.remove(); if (id) fskip[id] = true; ftry = null; resumeCountdown(); renderFilonOffer(); };
      updateFilonOverlay(f);
    }
    function showBack() { const b = $("#foback"); if (b) { b.hidden = false; b.className = "primary"; } }
    function updateFilonOverlay(f) {
      if (!ftry || !$("#fov")) return;
      const st = $("#fostate"), wait = $("#fowait"), im = $("#foimg");
      if (!f) { // the filon is over
        if (!ftry.closed) {
          ftry.closed = true;
          $("#foans").querySelectorAll(".ans").forEach(x => { x.disabled = true; });
          if (!ftry.answered) st.innerHTML = '<div class="feedback">Le filon est terminé.</div>';
          else st.insertAdjacentHTML("beforeend", '<div class="feedback" style="margin-top:8px">Le filon est terminé : ton résultat arrive en message.</div>');
          showBack();
        }
        return;
      }
      if (f.joined === false) { // could not load in time
        wait.textContent = "La question n'a pas pu se charger à temps."; st.innerHTML = ""; showBack(); return;
      }
      if (f.stage === "choose") {
        st.innerHTML = `<p class="muted" style="margin:0">Tu participes ! Ta question est en pause. Les inscriptions se terminent dans <strong data-fleft="${f.id}">${secsTo(f.id)}</strong> s.</p>`;
        return;
      }
      if (f.n && !ftry.loading) { // load the question now, hidden until everybody is ready
        ftry.loading = true;
        const go = () => setImg(im, V.img, f.n).then(() => {
          if (!(im.complete && im.naturalWidth > 1)) throw new Error("img");
          ftry.ready = true; send({ t: "floaded", id: f.id });
        }).catch(() => setTimeout(() => { if (ftry && ftry.id === f.id && $("#fov")) go(); }, 1500));
        go();
      }
      if (f.stage === "load") {
        st.innerHTML = `<p class="muted" style="margin:0">Chargement de la question… ${f.nReady} / ${f.nNeed} chercheurs prêts.</p>`;
        return;
      }
      if (f.stage === "play" && f.loaded && !ftry.shownQ) {
        ftry.shownQ = true;
        wait.style.display = "none"; im.style.display = "";
        if (!ftry.answered) {
          $("#foans").querySelectorAll(".ans").forEach(x => { x.disabled = false; });
          st.innerHTML = `<p class="muted" style="margin:0">À toi ! Réponds avant ${esc(ftry.from)}.</p>`;
        }
      }
    }

    /* ----- my own filon: wait while the others sign up and load ----- */
    function filonOwnerOverlay(q) {
      let ov = $("#fown");
      if (!ov) {
        ov = document.createElement("div"); ov.className = "overlay"; ov.id = "fown";
        ov.innerHTML = `<div class="box"><div class="title filon">Tu as trouvé un filon !</div>
          <p>Tu auras <strong>${q.time} secondes</strong>. Si tu réponds juste, tu gagnes <strong>4 pépites</strong>. Les autres chercheurs peuvent participer : ceux qui trouvent gagnent <strong>1 pépite</strong>, mais seulement si <strong>tu trouves aussi</strong> !</p>
          <p id="fownst" style="font-size:18px;color:var(--muted)"></p></div>`;
        document.body.appendChild(ov);
      }
      return ov;
    }
    function updateFilonOwner() {
      const q = V && V.q;
      if (!q || q.kind !== "filon" || !shown || shown.id !== q.id || shown.answered) { const o = $("#fown"); if (o) o.remove(); return; }
      if (q.fstage === "play") {
        const o = $("#fown"); if (o) o.remove();
        if (!shown.started) shown.ready.then(() => {
          if (shown && shown.id === q.id && !shown.answered && !shown.started) { shown.started = true; $("#qimg").style.visibility = ""; startQ(q); }
        });
        return;
      }
      filonOwnerOverlay(q);
      const st = $("#fownst");
      st.innerHTML = q.fstage === "choose"
        ? `Les autres chercheurs choisissent s'ils participent : <strong data-fleft="${q.fid}">${secsTo(q.fid)}</strong> s. Participants : <strong>${q.nPart}</strong>.`
        : `Chargement de la question chez tout le monde… ${q.nReady} / ${q.nNeed} prêts.`;
    }

    function meBar() {
      const me = V.me;
      if (!me) return "";
      return `<div class="mebar" id="mebar" style="--pc:${me.color}"><span class="nm">${esc(me.name)}</span>
        <span class="rk">${me.rank}<sup>${me.rank === 1 ? "er" : "e"}</sup> / ${me.n}</span><span class="sc">${me.score} ${NUG}</span></div>`;
    }
    const top = () => header(esc(V.sub || "")) + `<div class="banner" id="sbanner" ${banner ? "" : "hidden"}>${esc(banner)}</div>` + meBar();
    function stopTimers() { if (timer) { clearInterval(timer); timer = null; } cd = null; drawT.forEach(clearTimeout); drawT = []; }

    function render() {
      if (!V) return;
      if (V.phase === "lobby") {
        stopTimers(); shown = null;
        app.innerHTML = top() + `<section class="panel"><h2>Bienvenue ${esc(V.me ? V.me.name : "")} !</h2>
          <p>Tu es dans la partie <strong>${esc(V.code)}</strong>. Attends que le professeur la lance.</p>${rulesHTML()}</section>` + credit;
        return;
      }
      if (V.phase === "end") {
        stopTimers(); shown = null;
        const r = V.ranking || [];
        app.innerHTML = header(esc(V.sub || "")) + meBar() + `<section class="panel"><h2>Fin de la partie !</h2>
          ${V.me ? `<p style="font-size:20px;color:var(--ore)">Tu termines <strong>${V.me.rank}<sup>${V.me.rank === 1 ? "er" : "e"}</sup></strong> sur ${V.me.n} avec <strong>${V.me.score}</strong> pépite${V.me.score > 1 ? "s" : ""}.</p>` : ""}
          <div class="podium">${r.slice(0, 10).map(o => `<div class="rank ${o.rank === 1 ? "first" : ""}" style="--pc:${o.color}"><span class="pos">${o.rank}</span><span class="nm">${esc(o.name)}</span><span class="pts">${o.score} ${NUG}</span></div>`).join("")}</div>
        </section>` + credit;
        return;
      }
      // play
      if (V.q) {
        if (shown && shown.id === V.q.id) {
          refreshBar();
          if (V.q.fid && V.q.fstage === "load" && shown.ready) shown.ready.then(() => send({ t: "floaded", id: V.q.fid }));
          if (shown.answered && shown.choice !== undefined) send({ t: "ans", id: shown.id, l: shown.choice }); // the answer was lost on the way
          return;
        }
        return showQuestion(V.q);
      }
      if (V.res) {
        if (shown && shown.id === V.res.qid) { refreshBar(); return showResult(V.res); }
        return showQuestion({ id: V.res.qid, n: V.res.n, kind: V.res.kind, num: null }, V.res);
      }
      stopTimers(); shown = null;
      if (V.done) {
        app.innerHTML = top() + `<section class="panel"><h2>Tu as fini tes questions !</h2>
          <p>Bravo ! Ton classement évolue encore pendant que les autres terminent : les filons des autres peuvent te rapporter des pépites, et un camarade peut encore te chaparder.</p></section>` + credit;
        return;
      }
      app.innerHTML = top() + `<section class="panel"><h2>${V.started ? "Prêt pour la suite ?" : "La partie commence !"}</h2>
        <p>Tu as ${V.me.N} questions. Réponds à ton rythme. Chaque question a un temps limité.</p>
        <button class="primary" id="snext">${V.started ? "Question suivante" : "Première question"}</button></section>` + credit;
      $("#snext").onclick = () => { $("#snext").disabled = true; send({ t: "next" }); };
    }
    function refreshBar() {
      const b = $("#mebar"); if (b && V.me) b.outerHTML = meBar();
      setBanner(banner);
    }

    function showQuestion(q, res) {
      stopTimers();
      shown = { id: q.id, answered: !!res, choice: res ? res.choice : undefined, q };
      const ribbon = q.kind === "filon" ? '<span class="ribbon filon">Filon</span>' : q.kind === "raid" ? '<span class="ribbon raid">Chapardage</span>'
        : q.kind === "duel" ? `<span class="ribbon duel">Castagne${q.th ? " · " + esc(q.th) : ""}</span>` : q.kind === "rescue" ? '<span class="ribbon rescue">Sauvetage</span>' : "";
      const what = q.num ? `Question ${q.num} sur ${V.me.N}` : q.kind === "duel" ? "Castagne" : q.kind === "rescue" ? "Sauvetage" : "Question";
      const stake = q.kind === "filon" ? `${nugs(4)} 4 pépites` : q.kind === "raid" ? `${nugs(3)} jusqu'à 3 pépites`
        : q.kind === "duel" ? `${nugs(2)} 2 pépites` : q.kind === "rescue" ? `${nugs(2)} jusqu'à 2 pépites chacun` : `${nugs(1)} 1 pépite`;
      const info = q.kind === "raid" && q.victim ? `<div class="feedback ko" style="font-size:15px">Tu chapardes ${esc(q.victim)}. Le shérif veille : si tu te trompes, tu lui paies 1 pépite d'amende.</div>`
        : q.kind === "duel" && q.partner ? `<div class="duelbox"><span class="who now" style="--pc:${V.me.color}">${esc(V.me.name)}</span><span class="vs">contre</span><span class="who" style="--pc:#ff8a3d">${esc(q.partner)}</span></div>`
        : q.kind === "rescue" && q.partner ? `<div class="feedback ok" style="font-size:15px">Sauvetage avec ${esc(q.partner)} : vous avez le droit de vous entraider !</div>`
        : q.kind === "filon" ? `<div class="feedback ok" style="font-size:15px">Les autres chercheurs peuvent tenter ta question : ils gagnent 1 pépite s'ils trouvent et si tu trouves aussi.</div>` : "";
      app.innerHTML = top() + `
        <div class="play">
          <div class="board player" style="--pc:${V.me.color}">${ribbon}
            <img id="qimg" alt="Question : énoncé, figure et réponses a, b, c, d" width="1200" height="1050">
          </div>
          <div class="side"><div class="panel">
            <div class="progress">${what}</div>
            <div class="stake">En jeu : <span class="nugs">${stake}</span></div>
            ${info}
            ${q.kind === "duel" && !res ? '<div class="draw" id="draw" aria-live="assertive"></div>' : ""}
            ${res ? "" : `<div class="timer" id="timer"><div class="row"><span>Temps restant</span><span class="secs" id="secs">${q.time} s</span></div><div class="bar"><i id="barfill"></i></div></div>`}
            <div class="answers" id="ans" ${q.kind === "duel" && !res ? 'style="visibility:hidden"' : ""}>${["a", "b", "c", "d"].map(l => `<button class="ans" data-l="${l}" disabled>${l.toUpperCase()}</button>`).join("")}</div>
            <div id="fb" aria-live="polite"></div>
          </div></div>
        </div>` + credit;
      app.querySelectorAll(".ans").forEach(b => { b.onclick = () => answer(b.dataset.l); });
      const im = $("#qimg");
      if (res) { setImg(im, V.img, q.n).catch(() => {}); showResult(res); return; }
      // the timer only starts once the question is fully displayed
      const secs = $("#secs"); if (secs) secs.textContent = "…";
      const ready = loadQuestion(im, q);
      if (q.kind === "filon" && q.fid) { // shown to everybody at the same time
        im.style.visibility = "hidden";
        shown.ready = ready;
        ready.then(() => send({ t: "floaded", id: q.fid }));
        return;
      }
      const begin = () => ready.then(() => { if (shown && shown.id === q.id && !shown.answered) startQ(q); });
      if (q.kind !== "normal") intro(q, begin, ready); else begin();
    }
    // resolves only when the question image is loaded and drawn; retries on a bad connection
    function loadQuestion(im, q) {
      return new Promise(resolve => {
        let tries = 0;
        const fb = () => $("#fb");
        const attempt = () => {
          if (!shown || shown.q !== q) return;
          setImg(im, V.img, q.n).then(() => {
            if (!(im.complete && im.naturalWidth > 1)) throw new Error("img");
            const f = fb(); if (f && f.dataset.loading) { f.innerHTML = ""; delete f.dataset.loading; }
            resolve();
          }).catch(() => {
            tries++;
            const f = fb();
            if (f) {
              f.dataset.loading = "1";
              f.innerHTML = `<div class="feedback">Chargement de la question… Le chrono démarrera quand elle sera affichée.</div>
                <button class="ghost" id="imgretry" style="margin-top:8px;width:100%">Réessayer</button>`;
              const b = $("#imgretry"); if (b) b.onclick = () => { b.disabled = true; attempt(); };
            }
            setTimeout(attempt, Math.min(8000, 1500 * tries));
          });
        };
        attempt();
      });
    }
    function intro(q, then, ready) {
      const ov = document.createElement("div"); ov.className = "overlay";
      const t = q.kind === "filon" ? ["filon", "Tu as trouvé un filon !", `Tu as <strong>${q.time} secondes</strong>. Si tu réussis, tu gagnes <strong>4 pépites</strong>. Les autres chercheurs peuvent tenter la même question : ceux qui trouvent gagnent <strong>1 pépite</strong>, mais seulement si <strong>tu trouves aussi</strong> !`]
        : q.kind === "raid" ? ["", "Chapardage !", `Réponds juste en ${q.time} secondes et tu prends jusqu'à <strong>3 pépites</strong> à <strong>${esc(q.victim || "")}</strong>, le plus riche. Mais attention, <strong>le shérif veille</strong> : si tu te trompes, tu lui paies 1 pépite d'amende !`]
        : q.kind === "duel" ? ["", "Castagne !", `Tu affrontes <strong>${esc(q.partner || "")}</strong> sur une question que tu as déjà réussie, avec d'autres valeurs. Les réponses apparaissent au signal « Dégaine ! ». Juste et l'autre faux : 2 pépites. Les deux justes : 1 pépite chacun.`]
        : ["", "Sauvetage !", `Tu fais équipe avec <strong>${esc(q.partner || "")}</strong>. Chacun refait une question ratée, avec d'autres valeurs. Deux bonnes réponses : 2 pépites chacun. Une seule : 1 pépite chacun. <strong>Vous avez le droit de vous entraider !</strong>`];
      const col = q.kind === "duel" ? "#ff8a3d" : q.kind === "rescue" ? "var(--ok)" : q.kind === "raid" ? "var(--bad)" : "";
      ov.innerHTML = `<div class="box"><div class="title ${t[0]}" ${col ? `style="color:${col}"` : ""}>${t[1]}</div><p>${t[2]}</p><button class="primary" id="ready">C'est parti !</button></div>`;
      document.body.appendChild(ov);
      const b = ov.querySelector("#ready");
      b.onclick = () => { ov.remove(); then(); };
      // the start button waits until the question is displayed
      if (ready) {
        b.disabled = true; b.textContent = "Chargement de la question…";
        ready.then(() => { if (b.isConnected) { b.disabled = false; b.textContent = "C'est parti !"; b.focus(); } });
      } else b.focus();
    }
    function startQ(q) {
      const ansBox = $("#ans");
      if (!ansBox) return;
      const enable = () => { ansBox.style.visibility = "visible"; ansBox.querySelectorAll(".ans").forEach(b => { b.disabled = false; }); };
      countdown(q.time, () => answer(null));
      if (ftry) pauseCountdown(); // the player is busy on someone else's filon
      if (q.kind !== "duel") { enable(); return; }
      // castagne: the buttons appear for the last 4 seconds, while "3, 2, 1, Dégaine !" counts down
      const box = $("#draw"), open = (q.time - 4) * 1000;
      ["3", "2", "1", "Dégaine !"].forEach((txt, i) => drawT.push(setTimeout(() => {
        if (!box || !box.isConnected) return;
        box.textContent = txt; box.classList.toggle("go", i === 3);
        if (i === 0) enable();
      }, open + i * 1000)));
    }
    let cd = null; // running countdown {D, end, onEnd} or paused {D, left, onEnd}
    function countdown(D, onEnd, leftMs) {
      if (timer) clearInterval(timer);
      const end = performance.now() + (leftMs != null ? leftMs : D * 1000);
      cd = { D, end, onEnd };
      const secsEl = $("#secs"), fill = $("#barfill"), box = $("#timer");
      if (!secsEl) return;
      timer = setInterval(() => {
        const left = Math.max(0, end - performance.now()), s = Math.ceil(left / 1000);
        secsEl.textContent = s + " s"; fill.style.width = (left / (D * 1000) * 100) + "%";
        box.classList.toggle("low", s <= 5);
        if (left <= 0) { clearInterval(timer); timer = null; cd = null; onEnd(); }
      }, 100);
    }
    function pauseCountdown() {
      if (!timer || !cd) return;
      clearInterval(timer); timer = null;
      cd = { D: cd.D, left: Math.max(0, cd.end - performance.now()), onEnd: cd.onEnd, paused: true };
      const secs = $("#secs"); if (secs) secs.textContent = "pause";
    }
    function resumeCountdown() { if (cd && cd.paused) countdown(cd.D, cd.onEnd, cd.left); }
    function answer(l) {
      if (!shown || shown.answered) return;
      stopTimers();
      shown.answered = true; shown.choice = l;
      app.querySelectorAll(".ans").forEach(b => { b.disabled = true; if (b.dataset.l === l) b.classList.add("picked"); });
      const d = $("#draw"); if (d) d.textContent = "";
      $("#fb").innerHTML = '<div class="feedback">Réponse envoyée…</div>';
      send({ t: "ans", id: shown.id, l });
    }
    function showResult(res) {
      const ansBox = $("#ans"); if (!ansBox) return;
      ansBox.style.visibility = "visible";
      const t = $("#timer"); if (t) t.remove();
      const d = $("#draw"); if (d) d.remove();
      ansBox.querySelectorAll(".ans").forEach(b => {
        b.disabled = true; b.classList.remove("picked");
        if (b.dataset.l === res.right) b.classList.add("right"); else if (b.dataset.l === res.choice) b.classList.add("wrong");
      });
      const last = V.me.k >= V.me.N;
      $("#fb").innerHTML = `<div class="feedback ${res.wait ? "" : res.ok ? "ok" : "ko"}">${esc(res.text)}</div>
        <button class="primary" id="snext" style="margin-top:10px;width:100%">${last ? "Continuer" : "Question suivante"}</button>`;
      const nx = $("#snext");
      nx.onclick = () => { nx.disabled = true; send({ t: "next" }); };
    }
    return { init, _v: () => V };
  })();

  /* ---------- boot ---------- */
  if (params.has("p")) Student.init(params.get("p"));
  else if (params.has("prof")) Host.init();
  else renderMenu();
  window.__ruee = { Host, Student };
})();
