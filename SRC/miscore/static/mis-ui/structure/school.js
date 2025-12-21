(function () {
  const KEY = "structure-school";
  const PAGE_SIZE = 10;
  const API_URL = "/api/schools";  // đọc DB thật

  let allItems = [];
  let filtered = [];
  let page = 1, pageCount = 1;

  let $tbody, $empty, $prev, $next, $info, $input, $clear, $drawer, $backdrop, $drawerTitle, $drawerBody, $close;

  const qs  = (s) => document.querySelector(s);
  const qsa = (s) => Array.from(document.querySelectorAll(s));

  function icon(flag) {
    if (flag) {
      return `<svg class="status-ic ok" viewBox="0 0 24 24" fill="none" stroke-width="2">
        <circle cx="12" cy="12" r="9"/>
        <path d="M7 12l3 3 7-7" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>`;
    }
    return `<svg class="status-ic no" viewBox="0 0 24 24" fill="none" stroke-width="2">
      <circle cx="12" cy="12" r="9"/>
      <path d="M8 8l8 8M16 8l-8 8" stroke-linecap="round"/>
    </svg>`;
  }

  function render() {
    pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    if (page > pageCount) page = pageCount;
    const start = (page - 1) * PAGE_SIZE;
    const rows = filtered.slice(start, start + PAGE_SIZE);

    if (!rows.length) {
      $tbody.innerHTML = "";
      $empty.hidden = false;
    } else {
      $empty.hidden = true;
      $tbody.innerHTML = rows.map(it => `
        <tr data-id="${it.id}">
          <td><strong>${it.name || ""}</strong></td>
          <td>${it.university || ""}</td>
          <td>${icon(!!it.is_active)}</td>
        </tr>
      `).join("");
    }

    $info.textContent = `${rows.length ? start + 1 : 0}-${Math.min(start + PAGE_SIZE, filtered.length)} / ${filtered.length}`;
    $prev.disabled = (page <= 1);
    $next.disabled = (page >= pageCount);

    qsa("#school-tbody tr").forEach(tr => {
      tr.addEventListener("click", () => {
        const id = Number(tr.getAttribute("data-id"));
        const item = allItems.find(x => x.id === id);
        openDrawer(item);
      });
    });
  }

  function applyFilter() {
    const q = $input.value.trim().toLowerCase();
    if (!q) {
      filtered = [...allItems];
    } else {
      filtered = allItems.filter(it =>
        (it.name && it.name.toLowerCase().includes(q)) ||
        (it.university && it.university.toLowerCase().includes(q))
      );
    }
    page = 1;
    render();
  }

  function openDrawer(item) {
    if (!item) return;
    $drawerTitle.textContent = item.name || "(no name)";
    $drawerBody.innerHTML = `
      <dl>
        <dt>University</dt><dd>${item.university || ""}</dd>
        <dt>Is active</dt><dd>${icon(!!item.is_active)}</dd>
        <dt>ID</dt><dd>${item.id}</dd>
      </dl>
    `;
    $backdrop.hidden = false;
    $drawer.hidden = false;
    requestAnimationFrame(() => $drawer.classList.add("open"));
  }

  function closeDrawer() {
    $drawer.classList.remove("open");
    setTimeout(() => { $drawer.hidden = true; $backdrop.hidden = true; }, 200);
  }

  async function initData() {
    try {
      const r = await fetch(API_URL, { headers: { "Accept": "application/json" } });
      const data = await r.json();
      allItems = Array.isArray(data.items) ? data.items : [];
    } catch {
      allItems = [];
    }
    applyFilter();
  }

  function bindEvents() {
    $input.addEventListener("input", applyFilter);
    $clear.addEventListener("click", () => { $input.value = ""; applyFilter(); });
    $prev.addEventListener("click", () => { if (page > 1) { page--; render(); } });
    $next.addEventListener("click", () => { if (page < pageCount) { page++; render(); } });
    $close.addEventListener("click", closeDrawer);
    $backdrop.addEventListener("click", closeDrawer);
  }

  function init() {
    $tbody = qs("#school-tbody");
    $empty = qs("#school-empty");
    $prev  = qs("#school-prev");
    $next  = qs("#school-next");
    $info  = qs("#school-page-info");
    $input = qs("#school-search-input");
    $clear = qs("#school-search-clear");
    $drawer = qs("#school-drawer");
    $backdrop = qs("#school-backdrop");
    $drawerTitle = qs("#drawer-title");
    $drawerBody  = qs("#drawer-body");
    $close = qs("#drawer-close");

    bindEvents();
    initData();
  }

  window.addEventListener("misui:page-mounted", (ev) => {
    if (ev.detail?.key === KEY) init();
  });
})();
