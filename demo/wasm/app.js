// Kongming wasm demo. Loads the decoder engine + en substrate with staged
// progress (the user asked to always see what's happening), then parses
// typed sentences via km_decode_text_json and draws an arc diagram.

const $ = (id) => document.getElementById(id);

// ── staged progress ─────────────────────────────────────────────────

function stage(id, state, detail) {
  const li = $(id);
  li.classList.remove("pending", "active", "done", "failed");
  li.classList.add(state);
  if (detail !== undefined) li.querySelector(".detail").textContent = detail;
}

async function fetchWithProgress(url, bar, onDetail) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`${url}: HTTP ${resp.status}`);
  const total = +resp.headers.get("Content-Length") || 0;
  const reader = resp.body.getReader();
  const chunks = [];
  let loaded = 0;
  bar.hidden = false;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    loaded += value.length;
    if (total) bar.value = (100 * loaded) / total;
    onDetail(
      `${(loaded / 1e6).toFixed(1)}${total ? " / " + (total / 1e6).toFixed(1) : ""} MB`,
    );
  }
  bar.hidden = true;
  const out = new Uint8Array(loaded);
  let at = 0;
  for (const c of chunks) {
    out.set(c, at);
    at += c.length;
  }
  return out;
}

// ── wasm plumbing ───────────────────────────────────────────────────

let mem, exportsRef;

function put(bytes) {
  const p = exportsRef.km_alloc(bytes.length) >>> 0; // heap can top 2 GB
  new Uint8Array(mem.buffer, p, bytes.length).set(bytes);
  return p;
}

async function boot() {
  try {
    stage("st-wasm", "active", "downloading…");
    const wasmBytes = await fetchWithProgress("kongming_wasm.wasm", $("pg-wasm"), (d) =>
      stage("st-wasm", "active", d),
    );
    stage("st-wasm", "active", "instantiating…");
    const imports = {
      env: {
        km_log: (p, l) => {
          const line = new TextDecoder().decode(new Uint8Array(mem.buffer, p >>> 0, l));
          const log = $("loadlog");
          log.textContent = line;
          if (line.startsWith("PANIC")) console.error(line);
        },
      },
    };
    const { instance } = await WebAssembly.instantiate(wasmBytes, imports);
    exportsRef = instance.exports;
    mem = exportsRef.memory;
    stage("st-wasm", "done", `${(wasmBytes.length / 1e6).toFixed(2)} MB`);

    stage("st-sub", "active", "downloading…");
    const sub = await fetchWithProgress(
      "substrate.en.kms.zst",
      $("pg-sub"),
      (d) => stage("st-sub", "active", d),
    );
    stage("st-sub", "done", `${(sub.length / 1e6).toFixed(2)} MB`);

    stage("st-load", "active", "inflating + indexing…");
    const t0 = performance.now();
    const langs = new TextEncoder().encode("en");
    const rc = exportsRef.km_load_substrate(put(sub), sub.length, put(langs), langs.length);
    if (rc !== 0) throw new Error(`substrate load failed (${rc})`);
    stage("st-load", "done", `${((performance.now() - t0) / 1000).toFixed(1)} s`);
    $("loadlog").textContent = "";

    $("workbench").hidden = false;
    $("text").focus();
  } catch (e) {
    for (const id of ["st-wasm", "st-sub", "st-load"])
      if ($(id).classList.contains("active")) stage(id, "failed", String(e));
    console.error(e);
  }
}

// ── parse + render ──────────────────────────────────────────────────

function parse() {
  const text = $("text").value.trim();
  if (!text) return;
  const bytes = new TextEncoder().encode(text);
  const t0 = performance.now();
  const r = Number(exportsRef.km_decode_text_json(put(bytes), bytes.length));
  const ms = performance.now() - t0;
  if (r < 0) {
    const why = { "-2": "not valid text", "-3": "no parse found", "-4": "nothing to parse" }[r] ?? r;
    $("status").textContent = `✗ ${why}`;
    $("svg").replaceChildren();
    $("table").replaceChildren();
    return;
  }
  const json = new TextDecoder().decode(
    new Uint8Array(mem.buffer, exportsRef.km_result_ptr() >>> 0, r),
  );
  const sent = JSON.parse(json);
  $("status").textContent = `parsed ${sent.tokens.length} tokens in ${ms.toFixed(0)} ms`;
  // Brat-style SVG, rendered in Rust from the decoded SentenceProto.
  const sv = Number(exportsRef.km_last_svg());
  $("svg").innerHTML =
    sv > 0
      ? new TextDecoder().decode(new Uint8Array(mem.buffer, exportsRef.km_result_ptr() >>> 0, sv))
      : "";
  renderTable(sent);
}

function renderTable(sent) {
  const rows = sent.tokens
    .map(
      (t, i) =>
        `<tr><td>${i + 1}</td><td>${t.text}</td><td>${t.lemma}</td><td>${t.upos}</td>` +
        `<td>${t.head}</td><td>${t.deprel}</td><td>${t.ner}</td></tr>`,
    )
    .join("");
  $("table").innerHTML =
    `<table><tr><th>#</th><th>text</th><th>lemma</th><th>upos</th><th>head</th><th>deprel</th><th>ner</th></tr>${rows}</table>`;
}

$("go").addEventListener("click", parse);
$("text").addEventListener("keydown", (e) => {
  if (e.key === "Enter") parse();
});

boot();
