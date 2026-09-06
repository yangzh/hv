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
      "substrate.en.parquet.zst",
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
    $("arcs").textContent = "";
    $("table").replaceChildren();
    $("pretty").textContent = "";
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
  $("arcs").textContent = renderArcText(sent);
  renderTable(sent);
  $("pretty").textContent = JSON.stringify(sent, null, 2);
}

// Text arc diagram: box-drawing arcs above a monospace token row.
// Shorter arcs sit lower; deprel labels ride their arc; ▾ marks the
// dependent end; the root token is flagged in the upos row.
function renderArcText(sent) {
  const toks = sent.tokens;
  let col = 0;
  const centers = [];
  const cells = [];
  for (const t of toks) {
    const w = Math.max([...t.text].length, [...t.upos].length);
    centers.push(col + Math.floor(w / 2));
    cells.push({ at: col, w });
    col += w + 2;
  }
  const width = col;

  const arcs = toks
    .map((t, i) => ({ dep: i, head: t.head - 1, label: t.deprel }))
    .filter((a) => a.head >= 0)
    .sort((a, b) => Math.abs(a.dep - a.head) - Math.abs(b.dep - b.head));
  const level = arcs.map(() => 1);
  for (let i = 0; i < arcs.length; i++)
    for (let j = 0; j < i; j++) {
      const [al, ar] = [Math.min(arcs[i].dep, arcs[i].head), Math.max(arcs[i].dep, arcs[i].head)];
      const [bl, br] = [Math.min(arcs[j].dep, arcs[j].head), Math.max(arcs[j].dep, arcs[j].head)];
      if (bl >= al && br <= ar && level[j] >= level[i]) level[i] = level[j] + 1;
    }
  const maxL = Math.max(1, ...level);
  const grid = Array.from({ length: maxL }, () => new Array(width).fill(" "));
  const rowOf = (l) => maxL - l; // level 1 = bottom row

  // Highest arcs first so lower spans + verticals compose with ┼.
  const order = arcs.map((_, i) => i).sort((a, b) => level[b] - level[a]);
  for (const i of order) {
    const a = arcs[i];
    const r = rowOf(level[i]);
    const [c1, c2] = [centers[a.dep], centers[a.head]].sort((x, y) => x - y);
    for (let c = c1 + 1; c < c2; c++)
      grid[r][c] = grid[r][c] === "│" ? "┼" : "─";
    // Corners; two arcs meeting at a shared head column form ┬.
    grid[r][c1] = grid[r][c1] === "╮" ? "┬" : "╭";
    grid[r][c2] = grid[r][c2] === "╭" ? "┬" : "╮";
    for (let rr = r + 1; rr < maxL; rr++)
      for (const c of [c1, c2])
        grid[rr][c] = grid[rr][c] === "─" ? "┼" : grid[rr][c] === " " ? "│" : grid[rr][c];
    // Label centered on the run, clamped inside the corners.
    const label = a.label;
    if (c2 - c1 - 1 >= label.length + 2) {
      const at = Math.max(c1 + 2, Math.floor((c1 + c2) / 2 - label.length / 2));
      for (let k = 0; k < label.length && at + k < c2 - 1; k++) grid[r][at + k] = label[k];
    }
  }
  // Arrowheads last: the dependent's foot, always visible.
  for (const a of arcs) grid[maxL - 1][centers[a.dep]] = "▾";

  const pad = (s, w) => s + " ".repeat(Math.max(0, w - [...s].length));
  const tokRow = toks.map((t, i) => pad(t.text, cells[i].w)).join("  ");
  const uposRow = toks
    .map((t, i) => pad(t.head === 0 ? t.upos + "*" : t.upos, cells[i].w))
    .join("  ");
  return [...grid.map((r) => r.join("").replace(/\s+$/, "")), tokRow, uposRow].join("\n");
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
