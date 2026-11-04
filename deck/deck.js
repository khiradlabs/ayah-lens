/* Ayah Lens live demo deck.  Plain JS, no dependencies, no build step, works from file://.
   Shared by index.html (the deck) and notes.html (speaker notes window).
   Query flags: debug=1 (corner readout), start=1 (skip the Space gate), slide=N&step=K (jump on load),
                qa=1 (transitions off, for screenshots and layout checks), toggle=off|<path> (override slide 5 clip). */
(function () {
  'use strict';

  var PAGE = document.body.getAttribute('data-page');
  var Q = new URLSearchParams(location.search);
  var DEBUG = Q.get('debug') === '1';
  var QA = Q.get('qa') === '1';
  var CHANNEL = 'ayah-lens-deck';
  var STATE_KEY = 'ayah-lens-deck-state';
  var CMD_KEY = 'ayah-lens-deck-cmd';
  // Keys the notes window forwards to the deck. Same set as the deck's own navigation keys.
  var FORWARD_KEYS = { 'ArrowRight': 1, 'ArrowLeft': 1, ' ': 1, 'PageUp': 1, 'PageDown': 1, 'Home': 1, 'End': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1 };

  // ==== EMBEDDED DATA (copied from media/verse-2-282.json and media/ribbon-2-282.json) ====
  // file:// pages cannot fetch() local JSON in Chrome, so the data is inlined here.
  // With debug=1 over http(s), the page re-fetches both JSON files and reports whether they still match.
  var VERSE = { ref: "2:282", count: 128, words: ["يَٰٓأَيُّهَا", "ٱلَّذِينَ", "ءَامَنُوٓاْ", "إِذَا", "تَدَايَنتُم", "بِدَيۡنٍ", "إِلَىٰٓ", "أَجَلٖ", "مُّسَمّٗى", "فَٱكۡتُبُوهُۚ", "وَلۡيَكۡتُب", "بَّيۡنَكُمۡ", "كَاتِبُۢ", "بِٱلۡعَدۡلِۚ", "وَلَا", "يَأۡبَ", "كَاتِبٌ", "أَن", "يَكۡتُبَ", "كَمَا", "عَلَّمَهُ", "ٱللَّهُۚ", "فَلۡيَكۡتُبۡ", "وَلۡيُمۡلِلِ", "ٱلَّذِي", "عَلَيۡهِ", "ٱلۡحَقُّ", "وَلۡيَتَّقِ", "ٱللَّهَ", "رَبَّهُۥ", "وَلَا", "يَبۡخَسۡ", "مِنۡهُ", "شَيۡـٔٗاۚ", "فَإِن", "كَانَ", "ٱلَّذِي", "عَلَيۡهِ", "ٱلۡحَقُّ", "سَفِيهًا", "أَوۡ", "ضَعِيفًا", "أَوۡ", "لَا", "يَسۡتَطِيعُ", "أَن", "يُمِلَّ", "هُوَ", "فَلۡيُمۡلِلۡ", "وَلِيُّهُۥ", "بِٱلۡعَدۡلِۚ", "وَٱسۡتَشۡهِدُواْ", "شَهِيدَيۡنِ", "مِن", "رِّجَالِكُمۡۖ", "فَإِن", "لَّمۡ", "يَكُونَا", "رَجُلَيۡنِ", "فَرَجُلٞ", "وَٱمۡرَأَتَانِ", "مِمَّن", "تَرۡضَوۡنَ", "مِنَ", "ٱلشُّهَدَآءِ", "أَن", "تَضِلَّ", "إِحۡدَىٰهُمَا", "فَتُذَكِّرَ", "إِحۡدَىٰهُمَا", "ٱلۡأُخۡرَىٰۚ", "وَلَا", "يَأۡبَ", "ٱلشُّهَدَآءُ", "إِذَا", "مَا", "دُعُواْۚ", "وَلَا", "تَسۡـَٔمُوٓاْ", "أَن", "تَكۡتُبُوهُ", "صَغِيرًا", "أَوۡ", "كَبِيرًا", "إِلَىٰٓ", "أَجَلِهِۦۚ", "ذَٰلِكُمۡ", "أَقۡسَطُ", "عِندَ", "ٱللَّهِ", "وَأَقۡوَمُ", "لِلشَّهَٰدَةِ", "وَأَدۡنَىٰٓ", "أَلَّا", "تَرۡتَابُوٓاْ", "إِلَّآ", "أَن", "تَكُونَ", "تِجَٰرَةً", "حَاضِرَةٗ", "تُدِيرُونَهَا", "بَيۡنَكُمۡ", "فَلَيۡسَ", "عَلَيۡكُمۡ", "جُنَاحٌ", "أَلَّا", "تَكۡتُبُوهَاۗ", "وَأَشۡهِدُوٓاْ", "إِذَا", "تَبَايَعۡتُمۡۚ", "وَلَا", "يُضَآرَّ", "كَاتِبٞ", "وَلَا", "شَهِيدٞۚ", "وَإِن", "تَفۡعَلُواْ", "فَإِنَّهُۥ", "فُسُوقُۢ", "بِكُمۡۗ", "وَٱتَّقُواْ", "ٱللَّهَۖ", "وَيُعَلِّمُكُمُ", "ٱللَّهُۗ", "وَٱللَّهُ", "بِكُلِّ", "شَيۡءٍ", "عَلِيمٞ"] };
  var RIBBON = { ref: "2:282", denominator: 36, steps: [{"t": 0.0, "counter": [4, 5], "words": [10, 14]}, {"t": 0.53, "counter": [5, 6], "words": [13, 18]}, {"t": 2.7, "counter": [6, 7], "words": [15, 22]}, {"t": 5.53, "counter": [7, 8], "words": [19, 24]}, {"t": 10.63, "counter": [8, 9], "words": [23, 27]}, {"t": 11.0, "counter": [9, 10], "words": [25, 30]}, {"t": 13.33, "counter": [10, 11], "words": [28, 34]}] };
  // ==== END EMBEDDED DATA ====

  // ---------------------------------------------------------------------------------------------
  // Slide outline and speaker notes (one entry per build step; index 0 is the slide as it opens).
  // Script source: submission/DEMO-SCRIPT-V1.0.md draft 5, first person. [Brackets] are stage cues.
  // {{5: ...}} is spoken only when the Hifz slide is present.
  // ---------------------------------------------------------------------------------------------
  var SLIDES = [
    { n: 1, title: 'What I see', steps: 2, notes: [
      "I'm listening to a reciter streaming on my laptop, wearing Meta's display glasses. This is what I see. [Clip plays with sound, 9.9 s. 2:281 portions, then 2:282 arrives at about 9.5 s.]",
      "The verse appears with its meaning, and when he moves on, the lens follows.",
      "I'm not tapping anything."
    ] },
    { n: 2, title: 'Why', steps: 3, notes: [
      "About two billion Muslims, by Pew's 2020 estimate. [The number counts up, then settles.]",
      "Many of us hear the Quran daily and cannot follow the Arabic.",
      "Looking a verse up pulls you out of the moment. [Phone clip plays, silent.]",
      "The meaning should come to you."
    ] },
    { n: 3, title: 'Ayah Lens', steps: 6, notes: [
      "This is Ayah Lens. [Phone screen recording plays, silent, on the right.]",
      "The Meta Ray-Ban Display glasses listen.",
      "Muse Voice writes out the Arabic as it is recited. The audio goes to Muse Voice.",
      "The software finds the verse, and your place inside it.",
      "Muse Spark prepares the match to the published English, in advance.",
      "And the meaning follows the recitation into the lens.",
      "And that is the easy part."
    ] },
    { n: 4, title: 'The hard case', steps: 3, notes: [
      "The hard part is knowing where you are. More than six thousand verses, phrases that repeat across them, and listeners who join halfway through. So watch this one. [2:282 ringed, the longest verse] [Clip plays with sound, 15 s. The lit span follows the lens.]",
      "Same verse number, the whole way.",
      "But the words on the lens keep moving, because Ayah Lens follows your place inside the verse.",
      "The longest verse in the Quran, 128 words.{{5: And if you would rather, the meaning steps aside.}}"
    ] },
    { n: 5, title: 'Hifz', steps: 2, notes: [
      "If you are memorizing, the English gets in the way. So switch it off. [Clip plays with sound.]",
      "The Arabic keeps following on its own.",
      "And when you want the meaning back, it returns."
    ] },
    { n: 6, title: 'What is real', steps: 3, notes: [
      "That is the whole product. Here is what is real. [Three numbers count up.]",
      "Transcription and tracking run live.",
      "Only Spark's English pairing is prepared in advance.",
      "I wrote the software in ten days, Oct 26 to Nov 4. Fifty-nine tests check the matching, the source text and the frame delivery. Watch one more verse arrive."
    ] },
    { n: 7, title: 'Close', steps: 1, notes: [
      "[2:282 arrives on the lens; Arabic first, translation on the phone] Many listeners hear these words without following them.",
      "Now the meaning can follow. Hear the recitation. Follow the meaning. [Card on screen. Let the recitation finish, two seconds of quiet.]"
    ] }
  ];

  function slideMeta(n) { for (var i = 0; i < SLIDES.length; i++) if (SLIDES[i].n === n) return SLIDES[i]; return null; }
  function pad2(x) { return (x < 10 ? '0' : '') + x; }
  function fmtInt(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function noteText(raw, skipped) {
    var has5 = !skipped || skipped.indexOf(5) < 0;
    return raw.replace(/\{\{5:([^}]*)\}\}/g, function (_, t) { return has5 ? t : ''; });
  }

  if (PAGE === 'notes') { initNotes(); } else { initDeck(); }

  // =============================================================================================
  // NOTES WINDOW
  // =============================================================================================
  function initNotes() {
    var root = document.getElementById('notes');
    var st = { n: 1, step: 0, started: false, t0: 0, skipped: [], synced: false };
    var elWhere = root.querySelector('.where'), elStep = root.querySelector('.stepinfo'), elClock = root.querySelector('.clock');
    var elState = root.querySelector('.state'), elScript = root.querySelector('.script'), elNext = root.querySelector('.next'), elSkip = root.querySelector('.skipnote');

    function active() { return SLIDES.filter(function (s) { return st.skipped.indexOf(s.n) < 0; }); }

    function render() {
      var meta = slideMeta(st.n) || SLIDES[0];
      var act = active();
      elWhere.textContent = 'Slide ' + meta.n + ' of ' + SLIDES.length + ' · ' + meta.title;
      elStep.textContent = 'Step ' + Math.min(st.step, meta.steps) + ' of ' + meta.steps;
      var msg = '';
      if (!st.synced) msg = 'Not linked to the deck. Open index.html, then press N there.';
      else if (!st.started) msg = 'Deck is open and waiting for the first Space in the deck window.';
      elState.textContent = msg;
      elScript.textContent = '';
      for (var i = 0; i <= meta.steps; i++) {
        var raw = noteText(meta.notes[i] || '', st.skipped);
        var p = document.createElement('p');
        p.className = 'ln ' + (i < st.step ? 'done' : (i === st.step ? 'now' : ''));
        raw.split(/(\[[^\]]*\])/).forEach(function (part) {
          if (!part) return;
          if (part.charAt(0) === '[') { var c = document.createElement('span'); c.className = 'cue'; c.textContent = part; p.appendChild(c); }
          else p.appendChild(document.createTextNode(part));
        });
        elScript.appendChild(p);
      }
      var idx = act.indexOf(meta);
      var nxt = idx >= 0 && idx < act.length - 1 ? act[idx + 1] : null;
      elNext.textContent = nxt ? ('After this slide: ' + nxt.n + ' · ' + nxt.title) : 'Last slide.';
      var cur = root.querySelector('.ln.now');
      if (cur && cur.scrollIntoView) { try { cur.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) {} }
    }

    function applyMsg(m) {
      if (!m || m.type !== 'state') return;
      st.n = m.n; st.step = m.step; st.started = !!m.started; st.t0 = m.t0 || 0; st.skipped = m.skipped || []; st.synced = true;
      elSkip.textContent = st.skipped.length ? 'Slide ' + st.skipped.join(', ') + ' is skipped (no clip).' : '';
      render(); tick();
    }
    function tick() {
      if (st.started && st.t0) {
        var s = Math.max(0, Math.floor((Date.now() - st.t0) / 1000));
        elClock.textContent = pad2(Math.floor(s / 60)) + ':' + pad2(s % 60);
      } else elClock.textContent = '';
    }
    setInterval(tick, 500);

    // Three links, so one working path is enough: BroadcastChannel, window.postMessage from the opener, localStorage event.
    var chan = null;
    try { if ('BroadcastChannel' in window) { chan = new BroadcastChannel(CHANNEL); chan.onmessage = function (e) { applyMsg(e.data); }; } } catch (e) { chan = null; }
    window.addEventListener('message', function (e) { applyMsg(e.data); });
    window.addEventListener('storage', function (e) { if (e.key === STATE_KEY && e.newValue) { try { applyMsg(JSON.parse(e.newValue)); } catch (x) {} } });
    try { var saved = localStorage.getItem(STATE_KEY); if (saved) applyMsg(JSON.parse(saved)); } catch (e) {}
    function hello() {
      try { if (chan) chan.postMessage({ type: 'hello' }); } catch (e) {}
      try { if (window.opener) window.opener.postMessage({ type: 'hello' }, '*'); } catch (e) {}
    }
    hello();
    setInterval(function () { if (!st.synced) hello(); }, 1500);

    // Keys pressed here drive the deck. This window never advances itself: it only shows what the deck reports.
    function sendKey(k) {
      var m = { type: 'key', key: k, id: Date.now() + '-' + Math.random().toString(36).slice(2), ts: Date.now() };
      try { if (chan) chan.postMessage(m); } catch (e) {}
      try { if (window.opener && !window.opener.closed) window.opener.postMessage(m, '*'); } catch (e) {}
      try { localStorage.setItem(CMD_KEY, JSON.stringify(m)); } catch (e) {}
    }
    window.addEventListener('keydown', function (e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (!FORWARD_KEYS[e.key]) return;
      e.preventDefault();
      if (!e.repeat) sendKey(e.key);
    });
    root.querySelector('.prev').addEventListener('click', function () { sendKey('ArrowLeft'); });
    root.querySelector('.nextbtn').addEventListener('click', function () { sendKey('ArrowRight'); });
    render();
  }

  // =============================================================================================
  // DECK
  // =============================================================================================
  function initDeck() {
    if (QA) document.body.classList.add('qa');
    var stage = document.getElementById('stage');
    var gate = document.getElementById('gate');
    var toastEl = document.getElementById('toast');
    var bar = document.getElementById('bar');
    var SL = [];                      // active slides
    var cur = { i: -1, step: 0 };
    var started = false, t0 = 0, ready = false, skipped = [];
    var userMuted = false, soundBlocked = false;
    var scale = 1, notesWin = null, logLines = [];
    var chan = null;

    function log(s) { logLines.push(s); if (logLines.length > 6) logLines.shift(); }

    // ---------- scaling ----------
    function fit() {
      scale = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
      stage.style.transform = 'translate(-50%, -50%) scale(' + scale + ')';
    }
    window.addEventListener('resize', fit);
    fit();

    // ---------- toast ----------
    var toastTimer = 0;
    function toast(msg) {
      toastEl.textContent = msg; toastEl.classList.add('on');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function () { toastEl.classList.remove('on'); }, 1500);
    }

    // ---------- animation helpers (token-cancelled) ----------
    var anim = { token: 0, timers: [] };
    function stopAnims() { anim.token++; anim.timers.forEach(clearTimeout); anim.timers = []; }
    function later(ms, fn) {
      var tk = anim.token;
      anim.timers.push(setTimeout(function () { if (tk === anim.token) fn(); }, ms));
    }
    function countUp(el, to, dur, delay, done) {
      var tk = anim.token;
      el.textContent = '0';
      later(delay || 0, function () {
        var s = performance.now();
        function f(now) {
          if (tk !== anim.token) return;
          var p = Math.min(1, (now - s) / dur), e = 1 - Math.pow(1 - p, 3);
          el.textContent = fmtInt(Math.round(to * e));
          if (p < 1) requestAnimationFrame(f); else if (done) done();
        }
        requestAnimationFrame(f);
      });
    }

    // ---------- slide list (slide 5 only if toggle.mp4 loads) ----------
    function buildSlides(skipFive) {
      SL = []; skipped = [];
      SLIDES.forEach(function (meta) {
        var el = document.getElementById('s' + meta.n);
        if (!el) return;
        if (meta.n === 5 && skipFive) { el.parentNode.removeChild(el); skipped.push(5); return; }
        var maxb = 0;
        [].forEach.call(el.querySelectorAll('.b'), function (b) { maxb = Math.max(maxb, +b.getAttribute('data-b')); });
        SL.push({ n: meta.n, el: el, title: meta.title, steps: meta.steps, domSteps: maxb, videos: [].slice.call(el.querySelectorAll('video')) });
      });
    }
    function allVideos() { var out = []; SL.forEach(function (s) { out = out.concat(s.videos); }); return out; }

    function probeToggle(cb) {
      var v = document.getElementById('v5');
      if (!v) { cb(false); return; }
      var ov = Q.get('toggle');
      if (ov === 'off') { cb(false); return; }
      v.setAttribute('src', ov || v.getAttribute('data-src'));
      var done = false, tm;
      function fin(ok) { if (done) return; done = true; clearTimeout(tm); cb(ok); }
      v.addEventListener('loadedmetadata', function () { fin(true); });
      v.addEventListener('error', function () { fin(false); });
      tm = setTimeout(function () { fin(v.readyState >= 1 && !v.error); }, 3000);
      if (v.error) fin(false);
      else if (v.readyState >= 1) fin(true);
    }

    // ---------- clips ----------
    function applyAudio(v) {
      var wants = v.getAttribute('data-audio') === '1';
      v.muted = !(wants && !userMuted && !soundBlocked);
      v.volume = 1;
    }
    function startClip(v, restart) {
      applyAudio(v);
      if (restart) { try { v.currentTime = 0; } catch (e) {} }
      var p;
      try { p = v.play(); } catch (e) { log('play threw ' + e.name); }
      if (p && p.catch) p.catch(function (err) {
        if (err && err.name === 'AbortError') return;
        if (!v.muted && v.getAttribute('data-audio') === '1') {
          soundBlocked = true; applyAudio(v);
          var p2; try { p2 = v.play(); } catch (e2) {}
          if (p2 && p2.catch) p2.catch(function (e3) { log('play failed ' + (e3 && e3.name)); });
          toast('Sound blocked. Press M');
        } else log('play rejected ' + (err && err.name));
      });
    }
    function stopClip(v, reset) {
      try { v.pause(); } catch (e) {}
      if (reset) { try { v.currentTime = 0; } catch (e) {} }
    }
    function clipStartStep(v) { return +v.getAttribute('data-start') || 0; }

    // ---------- slide hooks ----------
    function setupS2(fresh) {
      var el = document.getElementById('s2'), num = document.getElementById('num2');
      el.classList.remove('counting', 'settled');
      if (!fresh || QA) { num.textContent = '2,000,000,000'; el.classList.add('settled'); return; }
      el.classList.add('counting');
      countUp(num, 2000000000, 800, 0, function () {
        later(550, function () { el.classList.remove('counting'); el.classList.add('settled'); });
      });
    }
    function setupS6(fresh) {
      [].forEach.call(document.querySelectorAll('#s6 .count'), function (el, k) {
        var to = +el.getAttribute('data-to');
        if (!fresh || QA) el.textContent = fmtInt(to);
        else countUp(el, to, 800, k * 150);
      });
    }

    // ---------- ribbon (slide 4) ----------
    var ribbonEl = document.getElementById('ribbon'), counterEl = document.getElementById('counter4');
    var ribbonWords = [], ribbonIdx = -1, ribbonVideo = document.getElementById('v4'), lastT = 0;
    (function buildRibbon() {
      var frag = document.createDocumentFragment();
      VERSE.words.forEach(function (w, i) {
        var s = document.createElement('span');
        s.className = 'w'; s.setAttribute('data-i', String(i + 1)); s.textContent = w;
        frag.appendChild(s); ribbonWords.push(s);
        if (i < VERSE.words.length - 1) frag.appendChild(document.createElement('wbr'));
      });
      ribbonEl.appendChild(frag);
    })();
    function ribbonStepFor(t) {
      var idx = 0;
      for (var k = 0; k < RIBBON.steps.length; k++) if (t >= RIBBON.steps[k].t - 1e-6) idx = k;
      return idx;
    }
    function updateRibbon(force) {
      var t = ribbonVideo ? ribbonVideo.currentTime : 0;
      if (!(t >= 0)) t = 0;
      lastT = t;
      var idx = ribbonStepFor(t);
      if (idx === ribbonIdx && !force) return;
      ribbonIdx = idx;
      var s = RIBBON.steps[idx], a = s.words[0], b = s.words[1];
      for (var i = 0; i < ribbonWords.length; i++) ribbonWords[i].classList.toggle('lit', i + 1 >= a && i + 1 <= b);
      counterEl.textContent = 'Portion ' + s.counter[0] + '-' + s.counter[1] + ' of ' + RIBBON.denominator + ' on the lens';
      ribbonEl.setAttribute('data-step', String(idx));
      ribbonEl.setAttribute('data-lit', a + '-' + b);
    }
    if (ribbonVideo) ['timeupdate', 'seeked', 'seeking', 'loadedmetadata', 'play', 'playing', 'ended'].forEach(function (ev) {
      ribbonVideo.addEventListener(ev, function () { updateRibbon(false); });
    });

    // ---------- state machine ----------
    function applyBuilds(sl, step) {
      [].forEach.call(sl.el.querySelectorAll('.b'), function (el) {
        el.classList.toggle('on', step >= +el.getAttribute('data-b'));
      });
    }
    function enter(sl, step, fresh) {
      stopAnims();
      if (sl.n === 2) setupS2(fresh);
      if (sl.n === 6) setupS6(fresh);
      sl.videos.forEach(function (v) {
        if (step >= clipStartStep(v)) startClip(v, true); else stopClip(v, true);
      });
      if (sl.n === 4) updateRibbon(true);
    }
    function leave(sl) { sl.videos.forEach(function (v) { stopClip(v, false); }); }
    function onStep(sl, step, prevStep) {
      sl.videos.forEach(function (v) {
        var s = clipStartStep(v);
        if (s > 0) {
          if (step >= s && prevStep < s) startClip(v, true);
          else if (step < s && prevStep >= s) stopClip(v, true);
        }
      });
    }
    function setState(i, step, how, force) {
      if (i < 0 || i >= SL.length) return;
      var changing = force || cur.i !== i;
      var prevStep = cur.step;
      if (changing) {
        if (cur.i >= 0) leave(SL[cur.i]);
        SL.forEach(function (s, k) { s.el.classList.toggle('active', k === i); });
        cur.i = i; cur.step = step;
        applyBuilds(SL[i], step);
        enter(SL[i], step, step === 0 && how !== 'back');
      } else {
        cur.step = step;
        applyBuilds(SL[i], step);
        onStep(SL[i], step, prevStep);
      }
      afterChange();
    }
    function start(i, step) {
      started = true; t0 = Date.now();
      gate.classList.add('gone');
      setState(i, step || 0, 'jump', true);
    }
    function next() {
      if (!started) { start(0, 0); return; }
      var sl = SL[cur.i];
      if (cur.step < sl.steps) setState(cur.i, cur.step + 1, 'fwd');
      else if (cur.i < SL.length - 1) setState(cur.i + 1, 0, 'fwd');
    }
    function prev() {
      if (!started) return;
      if (cur.step > 0) setState(cur.i, cur.step - 1, 'back');
      else if (cur.i > 0) setState(cur.i - 1, SL[cur.i - 1].steps, 'back');
    }
    function jumpTo(n) {
      for (var k = 0; k < SL.length; k++) if (SL[k].n === n) {
        if (!started) start(k, 0); else setState(k, 0, 'jump', true);
        return true;
      }
      toast('No slide ' + n);
      return false;
    }
    function restartClip() {
      if (!started) return;
      var sl = SL[cur.i];
      sl.videos.forEach(function (v) { if (cur.step >= clipStartStep(v)) startClip(v, true); });
      if (sl.n === 4) updateRibbon(true);
    }

    // ---------- progress bar, notes sync ----------
    function updateBar() {
      var total = 0, done = 0;
      SL.forEach(function (s, k) { if (k < cur.i) done += s.steps + 1; total += s.steps + 1; });
      if (cur.i >= 0) done += cur.step;
      bar.style.width = (started && total > 1 ? (done / (total - 1)) * 100 : 0) + '%';
    }
    function stateMsg() {
      var sl = SL[Math.max(0, cur.i)];
      return { type: 'state', n: sl ? sl.n : 1, step: cur.step, steps: sl ? sl.steps : 0, started: started, t0: t0, skipped: skipped, ts: Date.now() };
    }
    function broadcast() {
      if (!SL.length) return;
      var m = stateMsg();
      try { if (chan) chan.postMessage(m); } catch (e) {}
      try { localStorage.setItem(STATE_KEY, JSON.stringify(m)); } catch (e) {}
      try { if (notesWin && !notesWin.closed) notesWin.postMessage(m, '*'); } catch (e) {}
    }
    try {
      if ('BroadcastChannel' in window) { chan = new BroadcastChannel(CHANNEL); chan.onmessage = function (e) { onRemote(e.data); }; }
    } catch (e) { chan = null; }
    window.addEventListener('message', function (e) { onRemote(e.data); });
    window.addEventListener('storage', function (e) { if (e.key === CMD_KEY && e.newValue) { try { onRemote(JSON.parse(e.newValue)); } catch (x) {} } });
    // Messages from the notes window: 'hello' (send state) and 'key' (drive the deck). A command can arrive on all three links; ids dedupe it.
    var seenCmd = [];
    function onRemote(m) {
      if (!m) return;
      if (m.type === 'hello') { broadcast(); return; }
      if (m.type !== 'key' || !ready) return;
      if (seenCmd.indexOf(m.id) >= 0) return;
      seenCmd.push(m.id); if (seenCmd.length > 40) seenCmd.shift();
      if (!FORWARD_KEYS[m.key]) return;
      // Sound needs a key press in this window once; a key typed only in the notes window cannot unlock it.
      if (!started && navigator.userActivation && !navigator.userActivation.hasBeenActive) { toast('Press Space in this window first'); return; }
      handleNavKey(m.key, false);
    }
    function afterChange() { updateBar(); broadcast(); }

    // ---------- keyboard ----------
    function toggleFullscreen() {
      var d = document, fs = d.fullscreenElement || d.webkitFullscreenElement;
      try {
        if (fs) { var ex = d.exitFullscreen || d.webkitExitFullscreen; if (ex) { var r = ex.call(d); if (r && r.catch) r.catch(function () {}); } }
        else { var e = d.documentElement, rq = e.requestFullscreen || e.webkitRequestFullscreen; if (rq) { var r2 = rq.call(e); if (r2 && r2.catch) r2.catch(function () {}); } }
      } catch (err) {}
    }
    function openNotes() {
      var w = null;
      try { w = window.open('notes.html', 'ayah-lens-notes', 'width=1000,height=760,left=60,top=60'); } catch (e) {}
      if (w) { notesWin = w; setTimeout(broadcast, 400); setTimeout(broadcast, 1200); }
      else toast('Pop-up blocked. Open notes.html');
    }
    // Navigation keys, shared by the deck window and the notes window. Returns true if the key is one of them.
    function handleNavKey(k, repeat) {
      switch (k) {
        case 'ArrowRight': case ' ': case 'Spacebar': case 'PageDown': if (!repeat) next(); return true;
        case 'ArrowLeft': case 'PageUp': if (!repeat) prev(); return true;
        case 'Home': if (!repeat && started) setState(0, 0, 'jump', cur.i === 0); return true;
        case 'End': if (!repeat && started) setState(SL.length - 1, SL[SL.length - 1].steps, 'back'); return true;
        default:
          if (/^[1-7]$/.test(k)) { if (!repeat) jumpTo(+k); return true; }
      }
      return false;
    }
    window.addEventListener('keydown', function (e) {
      if (!ready) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      var k = e.key, nav = false;
      if (soundBlocked && !userMuted) {
        soundBlocked = false; allVideos().forEach(applyAudio);
        if (k === 'm' || k === 'M') { e.preventDefault(); toast('Sound on'); return; }
      }
      if (handleNavKey(k, e.repeat)) nav = true;
      else switch (k) {
        case 'f': case 'F': nav = true; toggleFullscreen(); break;
        case 'm': case 'M': nav = true; userMuted = !userMuted; allVideos().forEach(applyAudio); toast(userMuted ? 'Sound off' : 'Sound on'); break;
        case 'r': case 'R': nav = true; restartClip(); break;
        case 'n': case 'N': nav = true; openNotes(); break;
      }
      if (nav) e.preventDefault();
    });

    // ---------- debug corner ----------
    var dbg = null;
    if (DEBUG) { dbg = document.createElement('div'); dbg.id = 'dbg'; document.body.appendChild(dbg); }
    var jsonNote = 'embedded data only (file://)';
    function checkJson() {
      if (location.protocol === 'file:' || !window.fetch) return;
      Promise.all([fetch('media/verse-2-282.json').then(function (r) { return r.json(); }), fetch('media/ribbon-2-282.json').then(function (r) { return r.json(); })]).then(function (r) {
        var okV = JSON.stringify(r[0].words) === JSON.stringify(VERSE.words);
        var okR = JSON.stringify(r[1].steps) === JSON.stringify(RIBBON.steps);
        jsonNote = 'json vs embedded: verse ' + (okV ? 'match' : 'DIFFERENT') + ', ribbon ' + (okR ? 'match' : 'DIFFERENT');
      }).catch(function () { jsonNote = 'json fetch failed'; });
    }
    function litRange() {
      var a = 0, b = 0;
      for (var i = 0; i < ribbonWords.length; i++) if (ribbonWords[i].classList.contains('lit')) { if (!a) a = i + 1; b = i + 1; }
      return a ? a + '-' + b : 'none';
    }
    function updateDebug() {
      if (!dbg) return;
      var sl = SL[cur.i], v = sl && sl.videos[0], s = RIBBON.steps[Math.max(0, ribbonIdx)];
      var l1 = 'slide ' + (sl ? sl.n : '-') + '/' + SLIDES.length + '  step ' + cur.step + '/' + (sl ? sl.steps : 0) + '  started=' + started + '  scale=' + scale.toFixed(3);
      var l2 = v ? ('clip ' + (v.getAttribute('src') || '').replace('media/', '') + '  t=' + v.currentTime.toFixed(2) + '/' + (v.duration || 0).toFixed(2) + '  paused=' + v.paused + ' ended=' + v.ended + ' muted=' + v.muted) : 'no clip';
      var l3 = 'ribbon step ' + ribbonIdx + ' (t>=' + s.t.toFixed(2) + ')  counter ' + s.counter[0] + '-' + s.counter[1] + '/' + RIBBON.denominator + '  lit words ' + s.words[0] + '-' + s.words[1] + '  DOM lit ' + litRange() + '  clock t=' + lastT.toFixed(2);
      dbg.textContent = l1 + '\n' + l2 + '\n' + l3 + '\n' + jsonNote + (logLines.length ? '\n' + logLines.join('\n') : '');
    }

    // ---------- main loop: ribbon reads the video clock every frame, plus the timeupdate and seek events above ----------
    function tick() {
      if (cur.i >= 0 && SL[cur.i] && SL[cur.i].n === 4) updateRibbon(false);
      if (DEBUG) updateDebug();
      requestAnimationFrame(tick);
    }

    // ---------- layout / media check used by CHECK.md (window.__deck.qa()) ----------
    function effOpacity(el) {
      var o = 1;
      for (var n = el; n && n !== stage; n = n.parentElement) {
        var cs = getComputedStyle(n);
        if (cs.visibility === 'hidden' || cs.display === 'none') return 0;
        o *= parseFloat(cs.opacity);
      }
      return o;
    }
    function textRects(root) {
      var out = [], w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n;
      var sr = stage.getBoundingClientRect();
      while ((n = w.nextNode())) {
        if (!n.nodeValue.trim()) continue;
        var el = n.parentElement;
        if (effOpacity(el) < 0.5) continue;
        var rg = document.createRange(); rg.selectNodeContents(n);
        var rects = rg.getClientRects();
        for (var i = 0; i < rects.length; i++) {
          var r = rects[i];
          if (r.width < 1 || r.height < 1) continue;
          out.push({ el: el, node: n, text: n.nodeValue.trim().slice(0, 28),
            l: (r.left - sr.left) / scale, t: (r.top - sr.top) / scale, r: (r.right - sr.left) / scale, b: (r.bottom - sr.top) / scale,
            fs: parseFloat(getComputedStyle(el).fontSize) });
        }
      }
      return out;
    }
    function runQA() {
      var report = { scale: scale, win: window.innerWidth + 'x' + window.innerHeight, slides: [], clips: [], errors: [] };
      var savedI = cur.i, savedStep = cur.step;
      var wasQA = document.body.classList.contains('qa');
      document.body.classList.add('qa');
      var okStart = started;
      if (!started) { started = true; gate.classList.add('gone'); }
      SL.forEach(function (sl, k) {
        for (var step = 0; step <= sl.steps; step++) {
          setState(k, step, step === 0 ? 'fwd' : 'fwd', step === 0);
          var issues = [], rects = textRects(sl.el), minFs = 999;
          rects.forEach(function (q) {
            if (q.fs < minFs) minFs = q.fs;
            if (q.fs < 39.99) issues.push('font ' + q.fs + 'px: ' + q.text);
            if (q.l < -0.5 || q.t < -0.5 || q.r > 1920.5 || q.b > 1080.5) issues.push('outside stage: ' + q.text + ' [' + [q.l, q.t, q.r, q.b].map(Math.round) + ']');
          });
          var rib = rects.filter(function (q) { return q.el.classList.contains('w'); });
          var oth = rects.filter(function (q) { return !q.el.classList.contains('w'); });
          for (var a = 0; a < oth.length; a++) for (var c = a + 1; c < oth.length; c++) {
            var A = oth[a], B = oth[c];
            if (A.node === B.node) continue;
            // text boxes include font ascent/descent padding; shrink 14% top and bottom before testing ink overlap
            var ha = (A.b - A.t) * 0.14, hb = (B.b - B.t) * 0.14;
            var iw = Math.min(A.r, B.r) - Math.max(A.l, B.l), ih = Math.min(A.b - ha, B.b - hb) - Math.max(A.t + ha, B.t + hb);
            if (iw > 2 && ih > 2) issues.push('overlap: "' + A.text + '" and "' + B.text + '"');
          }
          if (sl.n === 4) {
            var rr = ribbonEl.getBoundingClientRect(), sr = stage.getBoundingClientRect();
            var rb = (rr.bottom - sr.top) / scale, rt = (rr.top - sr.top) / scale;
            var lines = Math.round((rr.height / scale) / 76);
            if (rb > 1070) issues.push('ribbon bottom ' + Math.round(rb));
            var tag = document.querySelector('#s4 .tag4').getBoundingClientRect();
            if ((tag.bottom - sr.top) / scale > rt) issues.push('tag overlaps ribbon');
            report.ribbon = { top: Math.round(rt), bottom: Math.round(rb), lines: lines };
          }
          if (sl.steps !== sl.domSteps) issues.push('steps mismatch notes=' + sl.steps + ' dom=' + sl.domSteps);
          report.slides.push({ slide: sl.n, step: step, texts: rects.length, ribbonWords: rib.length, minFont: minFs === 999 ? null : minFs, issues: issues });
        }
      });
      allVideos().forEach(function (v) {
        report.clips.push({ src: v.getAttribute('src'), ready: v.readyState, dur: +(v.duration || 0).toFixed(2), w: v.videoWidth, h: v.videoHeight, err: v.error ? v.error.code : 0 });
      });
      if (!wasQA && !QA) document.body.classList.remove('qa');
      if (savedI >= 0) setState(savedI, savedStep, 'back', true);
      return report;
    }

    // ---------- debug / QA hooks ----------
    window.__deck = {
      state: function () { var sl = SL[cur.i]; return { slide: sl ? sl.n : 0, step: cur.step, steps: sl ? sl.steps : 0, started: started, ribbonStep: ribbonIdx, lit: litRange(), counter: counterEl.textContent, skipped: skipped.slice(), muted: userMuted, soundBlocked: soundBlocked }; },
      next: next, prev: prev, jump: jumpTo, restart: restartClip, qa: runQA,
      seek: function (t) {
        var sl = SL[cur.i], v = sl && sl.videos[0];
        if (!v) return Promise.resolve(false);
        return new Promise(function (res) {
          var done = function () { updateRibbon(false); res(true); };
          v.pause(); v.addEventListener('seeked', done, { once: true }); v.currentTime = t;
          setTimeout(done, 1500);
        });
      },
      clip: function () { var sl = SL[cur.i]; return sl && sl.videos[0]; },
      ready: null
    };

    // ---------- boot ----------
    var fontsReady = (document.fonts && document.fonts.load) ? Promise.all([document.fonts.load('42px UthmanicHafs', VERSE.words[0])]).catch(function () {}) : Promise.resolve();
    var probed = new Promise(function (res) { probeToggle(function (ok) { buildSlides(!ok); res(ok); }); });
    window.__deck.ready = Promise.all([fontsReady, probed]).then(function () {
      ready = true;
      updateBar();
      if (DEBUG) { checkJson(); }
      requestAnimationFrame(tick);
      var qs = +Q.get('slide'), qstep = +Q.get('step') || 0;
      if (Q.get('start') === '1' || qs) {
        var idx = 0;
        if (qs) { for (var k = 0; k < SL.length; k++) if (SL[k].n === qs) idx = k; }
        start(idx, Math.min(qstep, SL[idx].steps));
      } else {
        broadcast();
      }
      return true;
    });
  }
})();
