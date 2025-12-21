(function () {
  const KEY = "structure-faculty";
  const API_URL = "/api/faculties";

  // Tự tính số dòng mỗi trang theo chiều cao màn hình
  let PAGE_SIZE = computePageSize();      // thường 20–30 line => rất ít trang
  function computePageSize() {
    const vh = window.innerHeight || 800;
    const reserved = 260; // header + toolbar + padding + pagination (ước lượng an toàn)
    const rowH = 44;      // chiều cao 1 dòng (ước lượng theo CSS)
    return Math.max(20, Math.min(100, Math.floor((vh - reserved) / rowH)));
  }
  window.addEventListener("resize", () => {
    const n = computePageSize();
    if (n !== PAGE_SIZE) { PAGE_SIZE = n; render(); }
  });

  let allItems = [], filtered = [];
  let page = 1, pageCount = 1;

  // sort: name | code | school
  let sortKey = "name";
  let sortDir = "asc";

  let $tbody, $empty, $prev, $next, $info, $input, $clear;
  let $thName, $thCode, $thSchool, $indName, $indCode, $indSchool;

  const qs  = (s) => document.querySelector(s);
  const qsa = (s) => Array.from(document.querySelectorAll(s));

  function icon(flag) {
    return flag
      ? `<svg class="status-ic ok" viewBox="0 0 24 24" fill="none" stroke-width="2">
           <circle cx="12" cy="12" r="9"/><path d="M7 12l3 3 7-7" stroke-linecap="round" stroke-linejoin="round"/>
         </svg>`
      : `<svg class="status-ic no" viewBox="0 0 24 24" fill="none" stroke-width="2">
           <circle cx="12" cy="12" r="9"/><path d="M8 8l8 8M16 8l-8 8" stroke-linecap="round"/>
         </svg>`;
  }

  function applySort(list) {
    const k = sortKey, mul = (sortDir === "asc" ? 1 : -1);
    return list.slice().sort((a, b) => {
      const A = (a[k] || "").toString().toLowerCase();
      const B = (b[k] || "").toString().toLowerCase();
      if (A < B) return -1 * mul;
      if (A > B) return  1 * mul;
      return 0;
    });
  }

  function updateIndicators() {
    [$indName, $indCode, $indSchool].forEach(el => el.classList.remove("show","desc"));
    const map = { name: $indName, code: $indCode, school: $indSchool };
    const el = map[sortKey];
    el.classList.add("show");
    if (sortDir === "desc") el.classList.add("desc");
  }

  function render() {
    const data = applySort(filtered);
    pageCount = Math.max(1, Math.ceil(data.length / PAGE_SIZE));
    if (page > pageCount) page = pageCount;

    const start = (page - 1) * PAGE_SIZE;
    const rows = data.slice(start, start + PAGE_SIZE);

    if (!rows.length) {
      $tbody.innerHTML = ""; $empty.hidden = false;
    } else {
      $empty.hidden = true;
      $tbody.innerHTML = rows.map(it => `
        <tr>
          <td><strong>${it.code || ""}</strong></td>
          <td>${it.name || ""}</td>
          <td>${it.school || ""}</td>
          <td>${icon(!!it.is_active)}</td>
        </tr>
      `).join("");
    }

    $info.textContent = `${rows.length ? start + 1 : 0}-${Math.min(start + PAGE_SIZE, data.length)} / ${data.length}`;
    $prev.disabled = (page <= 1);
    $next.disabled = (page >= pageCount);

    updateIndicators();
  }

  function applyFilter() {
    const q = $input.value.trim().toLowerCase();
    filtered = !q ? [...allItems] : allItems.filter(it =>
      (it.code && it.code.toLowerCase().includes(q)) ||
      (it.name && it.name.toLowerCase().includes(q)) ||
      (it.school && it.school.toLowerCase().includes(q))
    );
    page = 1; render();
  }

  async function initData() {
    try {
      const r = await fetch(API_URL, { headers: { "Accept": "application/json" } });
      const data = await r.json();
      allItems = Array.isArray(data.items) ? data.items : [];
    } catch { allItems = []; }
    applyFilter();
  }

  function toggleSort(key) {
    if (sortKey === key) sortDir = (sortDir === "asc" ? "desc" : "asc");
    else { sortKey = key; sortDir = "asc"; }
    render();
  }

  function bindEvents() {
    $input.addEventListener("input", applyFilter);
    $clear.addEventListener("click", () => { $input.value = ""; applyFilter(); });
    $prev.addEventListener("click", () => { if (page > 1) { page--; render(); } });
    $next.addEventListener("click", () => { if (page < pageCount) { page++; render(); } });

    $thName.addEventListener("click",   () => toggleSort("name"));
    $thCode.addEventListener("click",   () => toggleSort("code"));
    $thSchool.addEventListener("click", () => toggleSort("school"));
  }

  function init() {
    $tbody = qs("#faculty-tbody");
    $empty = qs("#faculty-empty");
    $prev  = qs("#faculty-prev");
    $next  = qs("#faculty-next");
    $info  = qs("#faculty-page-info");
    $input = qs("#faculty-search-input");
    $clear = qs("#faculty-search-clear");

    $thName   = qs("#th-name");
    $thCode   = qs("#th-code");
    $thSchool = qs("#th-school");
    $indName   = qs("#sort-name");
    $indCode   = qs("#sort-code");
    $indSchool = qs("#sort-school");

    bindEvents();
    initData();
  }

  window.addEventListener("misui:page-mounted", (ev) => {
    if (ev.detail?.key === KEY) init();
  });
})();
