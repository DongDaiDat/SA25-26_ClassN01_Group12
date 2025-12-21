// Structure / Lecturer – view-only (v10, modal on name click)
(function () {
  const VER = "v10";
  console.log("LECT: file loaded", VER);

  const KEY = "structure-lecture";
  let mounted = false;
  const els = {};
  const state = { q: "", order: "name", page: 1, size: 50, items: [] };

  const $  = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));
  const esc = s => (s==null?"":String(s)).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  const okIcon = () => '<svg class="status-ic ok" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path d="M7 12l3 3 6-6" stroke-width="2"></path></svg>';
  const noIcon = () => '<svg class="status-ic no" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path d="M8 8l8 8M16 8l-8 8" stroke-width="2"></path></svg>';

  function getEls() {
    els.tbody = $("#lec-tbody");
    els.q = $("#lec-q");
    els.clear = $("#lec-clear");
    els.prev = $("#lec-prev");
    els.next = $("#lec-next");
    els.pageinfo = $("#lec-pageinfo");
    els.sortable = $$(".lec-table thead th.sortable");

    // modal
    els.modal   = $("#lec-modal");
    els.mdClose = $("#lec-modal .lec-modal__close");
    els.mdBd    = $("#lec-modal .lec-modal__backdrop");
    els.mdName  = $("#lec-md-name");
    els.mdPos   = $("#lec-md-position");
    els.mdFaculty = $("#lec-md-faculty");
    els.mdSchool  = $("#lec-md-school");
    els.mdEmail   = $("#lec-md-email");
    els.mdPhone   = $("#lec-md-phone");
    els.mdActive  = $("#lec-md-active");

    return !!els.tbody;
  }

  function syncSortUI() {
    els.sortable.forEach(th => {
      const key = th.getAttribute("data-key");
      const desc = state.order.startsWith("-");
      const cur  = desc ? state.order.slice(1) : state.order;
      const span = th.querySelector(".sort-ind");
      if (!span) return;
      if (key === cur) { span.classList.add("show"); span.classList.toggle("desc", desc); }
      else { span.classList.remove("show","desc"); }
    });
  }

  function buildApiUrl() {
    const p = [];
    if (state.q) p.push("q="+encodeURIComponent(state.q));
    p.push("order="+encodeURIComponent(state.order));
    return "/api/lecturers" + (p.length ? "?"+p.join("&") : "");
  }

  async function load() {
    els.tbody.innerHTML = '<tr><td colspan="5" class="lec-empty">Đang tải…</td></tr>';
    syncSortUI();
    try {
      const res = await fetch(buildApiUrl(), { headers:{Accept:"application/json"}, credentials:"same-origin" });
      if (!res.ok) throw new Error("HTTP "+res.status);
      const data = await res.json();
      state.items = Array.isArray(data.items) ? data.items : [];
      state.page = 1;
      console.log("LECT: loaded", state.items.length, "items");
      render();
    } catch(e) {
      console.error("LECT: load error", e);
      els.tbody.innerHTML = '<tr><td colspan="5" class="lec-empty">Lỗi tải dữ liệu</td></tr>';
    }
  }

  function render() {
    const total = state.items.length;
    const pages = Math.max(1, Math.ceil(total / state.size));
    state.page = Math.min(state.page, pages);

    const start = (state.page - 1) * state.size;
    const rows = state.items.slice(start, start + state.size);

    if (!rows.length) {
      els.tbody.innerHTML = '<tr><td colspan="5" class="lec-empty">Không có dữ liệu</td></tr>';
    } else {
      els.tbody.innerHTML = rows.map(r => `
        <tr data-id="${r.id}">
          <td><a href="#" class="lec-name" data-id="${r.id}">${esc(r.name)}</a></td>
          <td>${esc(r.faculty)}</td>
          <td>${esc(r.school)}</td>
          <td>${esc(r.position)}</td>
          <td>${r.is_active ? okIcon() : noIcon()}</td>
        </tr>
      `).join("");
    }

    els.pageinfo.textContent = `${state.page}/${pages}`;
    els.prev.disabled = state.page <= 1;
    els.next.disabled = state.page >= pages;
  }

  function bindEvents() {
    // sort
    els.sortable.forEach(th => {
      th.addEventListener("click", () => {
        const key = th.getAttribute("data-key");
        const d = state.order.startsWith("-");
        const cur = d ? state.order.slice(1) : state.order;
        state.order = (key === cur) ? (d ? key : "-"+key) : key;
        load();
      });
    });

    // search debounce
    let t;
    els.q.addEventListener("input", () => {
      clearTimeout(t);
      t = setTimeout(()=>{ state.q = (els.q.value||"").trim(); state.page=1; load(); }, 300);
    });
    els.clear.addEventListener("click", ()=>{ els.q.value=""; state.q=""; state.page=1; load(); });

    // paging (client)
    els.prev.addEventListener("click", ()=>{ if (state.page>1){ state.page--; render(); } });
    els.next.addEventListener("click", ()=>{ const pages=Math.max(1,Math.ceil(state.items.length/state.size)); if (state.page<pages){ state.page++; render(); } });

    // delegate click name -> modal
    els.tbody.addEventListener("click", (ev) => {
      const a = ev.target.closest("a.lec-name");
      if (!a) return;
      ev.preventDefault();
      const id = Number(a.getAttribute("data-id"));
      const item = state.items.find(x => x.id === id);
      if (item) showModal(item);
    });

    // modal close
    [els.mdClose, els.mdBd].forEach(btn => btn && btn.addEventListener("click", hideModal));
    document.addEventListener("keydown", (e)=>{ if(e.key==="Escape") hideModal(); });
  }

  function showModal(it) {
    els.mdName.textContent = it.name || "—";
    els.mdPos.textContent = it.position || "—";
    els.mdFaculty.textContent = it.faculty || "—";
    els.mdSchool.textContent  = it.school || "—";
    els.mdActive.textContent  = it.is_active ? "Active" : "Inactive";

    // email, phone clickable nếu có
    els.mdEmail.innerHTML = it.email ? `<a href="mailto:${esc(it.email)}">${esc(it.email)}</a>` : "—";
    els.mdPhone.innerHTML = it.phone ? `<a href="tel:${esc(it.phone)}">${esc(it.phone)}</a>` : "—";

    els.modal.classList.remove("hidden");
    els.modal.setAttribute("aria-hidden", "false");
  }
  function hideModal() {
    els.modal.classList.add("hidden");
    els.modal.setAttribute("aria-hidden", "true");
  }

  function mount() {
    if (mounted) return true;
    if (!getEls()) return false;
    mounted = true;
    console.log("LECT: mount OK");
    bindEvents();
    load();
    return true;
  }

  // hỗ trợ shell cũ
  document.addEventListener("misui:page-mounted", (ev) => { if (ev?.detail?.key === KEY) mount(); });

  // tự mount
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ()=>setTimeout(mount,0));
  else setTimeout(mount,0);

  window.__forceMountLecture = mount;
})();
