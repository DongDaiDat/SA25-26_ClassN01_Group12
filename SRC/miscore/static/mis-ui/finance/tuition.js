// static/mis-ui/study/tuition.js (v1)
(() => {
  console.log("TUITION: file loaded v1");

  const $  = (s,p=document)=>p.querySelector(s);
  const $$ = (s,p=document)=>Array.from(p.querySelectorAll(s));
  const nf = new Intl.NumberFormat('vi-VN');
  const cf = new Intl.NumberFormat('vi-VN', {style:'currency', currency:'VND', maximumFractionDigits:0});

  const elQ = $('#tui-q');
  const elClear = $('#tui-clear');
  const elOrder = $('#tui-order');
  const elTbody = $('#tui-tbody');
  const elPrev = $('#tui-prev');
  const elNext = $('#tui-next');
  const elPage = $('#tui-page');

  let ALL = [];
  let VIEW = [];
  let page = 1;
  const PER = 15;

  function render() {
    const totalPages = Math.max(1, Math.ceil(VIEW.length / PER));
    page = Math.min(page, totalPages);
    const rows = VIEW.slice((page-1)*PER, page*PER);

    if (!rows.length) {
      elTbody.innerHTML = `<tr><td class="tui-empty" colspan="8">Không có dữ liệu.</td></tr>`;
    } else {
      elTbody.innerHTML = rows.map(r => `
        <tr>
          <td>${r.major || ''}</td>
          <td>${r.faculty || ''}</td>
          <td>${r.year ?? ''}</td>
          <td>${nf.format(r.total_credits ?? 0)}</td>
          <td>${cf.format(r.price_per_credit ?? 0)}</td>
          <td><strong>${cf.format(r.total_amount ?? 0)}</strong></td>
          <td>${r.updated_at || ''}</td>
          <td>${r.note || ''}</td>
        </tr>
      `).join('');
    }

    elPage.textContent = `${page}/${totalPages}`;
    elPrev.disabled = page <= 1;
    elNext.disabled = page >= totalPages;
  }

  function applyFilter() {
    const q = (elQ.value || '').trim().toLowerCase();
    VIEW = !q ? ALL : ALL.filter(it =>
      (it.major||'').toLowerCase().includes(q) ||
      (it.faculty||'').toLowerCase().includes(q) ||
      String(it.year||'').includes(q) ||
      (it.note||'').toLowerCase().includes(q)
    );
    page = 1;
    render();
  }

  async function load() {
    elTbody.innerHTML = `<tr><td class="tui-empty" colspan="8">Đang tải…</td></tr>`;
    const order = elOrder.value || 'major';
    const r = await fetch(`/api/tuitions?order=${encodeURIComponent(order)}`);
    const j = await r.json();
    ALL = j.items || [];
    VIEW = ALL.slice(0);
    page = 1;
    render();
  }

  function bind() {
    elQ.addEventListener('input', applyFilter);
    elClear.addEventListener('click', () => { elQ.value=''; applyFilter(); });
    elOrder.addEventListener('change', load);
    elPrev.addEventListener('click', ()=>{ if(page>1){page--; render();} });
    elNext.addEventListener('click', ()=>{ const max=Math.max(1,Math.ceil(VIEW.length/PER)); if(page<max){page++; render();} });
  }

  async function mount() { bind(); await load(); }
  if (document.readyState !== 'loading') mount(); else document.addEventListener('DOMContentLoaded', mount);

  // Cho debug từ Console
  window.__forceMountTuition = mount;
})();
