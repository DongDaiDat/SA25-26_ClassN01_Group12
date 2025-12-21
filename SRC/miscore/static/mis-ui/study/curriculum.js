// study/curriculum.js (v20) — export PDF fixed to /study/curriculum/pdf
(function () {
  const VER = 'v20';
  console.log('CURRICULUM: file loaded', VER);

  let mounted = false;
  let CUR_ID = null;

  // DOM helpers
  const $  = (s, d=document) => d.querySelector(s);
  const $$ = (s, d=document) => Array.from(d.querySelectorAll(s));
  const text = (el, s) => { if (el) el.textContent = s; };

  // refs
  const host = $('#cur-body');
  const elQ = $('#cur-q'), elClear = $('#cur-clear');
  const elList = $('#cur-list'), elPrev = $('#cur-prev'), elNext = $('#cur-next'), elPage = $('#cur-page');

  const elMajor = $('#cur-major'), elFaculty = $('#cur-faculty'), elYear = $('#cur-year'), elCredits = $('#cur-credits');

  const elFilter = $('#cur-fi'), elSem = $('#cur-sem'), elType = $('#cur-type'), elActive = $('#cur-active');
  const elExport = $('#cur-export');

  const elTbody = $('#cur-tbody'), elRelBody = $('#cur-rel-body');

  // state
  let ALL = []; let page = 1, PER_PAGE = 15;
  let ITEMS = [], RELS = [], INFO = null;

  // fetcher
  async function getJSON(url){
    const r = await fetch(url, {cache:'no-store'});
    if (!r.ok) throw new Error(`fetch ${url} -> ${r.status}`);
    return r.json();
  }

  async function loadCurricula(){
    const q = (elQ?.value||'').trim();
    const url = `/api/curricula?q=${encodeURIComponent(q)}&order=major`;
    const data = await getJSON(url);
    ALL = data?.items || [];
    if (page > maxPage()) page = maxPage() || 1;
    renderCurricula();

    if (!CUR_ID && ALL.length) selectCurriculum(ALL[0].id, true);
  }

  async function loadItems(){
    if (!CUR_ID) return;
    const q   = (elFilter?.value||'').trim();
    const sem = elSem?.value || 'all';
    const typ = elType?.value || 'all';
    const act = elActive?.checked ? '1' : '0';
    const data = await getJSON(`/api/curriculum-items?cur=${CUR_ID}&q=${encodeURIComponent(q)}&sem=${sem}&type=${typ}&active=${act}`);
    ITEMS = data?.items || []; INFO = data?.info || null;
    renderInfo(); renderItems();
  }

  async function loadRelations(){
    if (!CUR_ID) return;
    const data = await getJSON(`/api/curriculum-relations?cur=${CUR_ID}`);
    RELS = data?.items || [];
    renderRelations();
  }

  // render
  function maxPage(){ return Math.max(1, Math.ceil((ALL.length||0)/PER_PAGE)); }

  function renderCurricula(){
    elList.innerHTML = '';
    if (!ALL.length){ elList.innerHTML = `<li class="cur-empty" style="list-style:none;border:none;margin:8px;">Không có CTĐT.</li>`; text(elPage,'1/1'); return; }

    const start = (page-1)*PER_PAGE;
    const slice = ALL.slice(start, start+PER_PAGE);
    slice.forEach(c => {
      const li = document.createElement('li');
      li.dataset.id = c.id;
      li.innerHTML = `<div>${escapeHtml(c.major||'')} — <small>${escapeHtml(String(c.year||''))}</small></div><small>${escapeHtml(c.faculty||'')}</small>`;
      if (c.id === CUR_ID) li.classList.add('active');
      li.addEventListener('click', () => selectCurriculum(c.id, true));
      elList.appendChild(li);
    });

    text(elPage, `${page}/${maxPage()}`);
    elPrev.disabled = (page<=1); elNext.disabled = (page>=maxPage());
  }

  function renderInfo(){
    text(elMajor,   INFO?.major   || '—');
    text(elFaculty, INFO?.faculty || '—');
    text(elYear,    INFO?.year!=null ? String(INFO.year) : '—');
    text(elCredits, INFO?.total_active_credits!=null ? String(INFO.total_active_credits) : '0.0');
  }

  function renderItems(){
    elTbody.innerHTML = '';
    if (!CUR_ID){ elTbody.innerHTML = `<tr><td colspan="9" class="cur-empty">Chưa chọn CTĐT.</td></tr>`; return; }
    if (!ITEMS.length){ elTbody.innerHTML = `<tr><td colspan="9" class="cur-empty">Không có học phần.</td></tr>`; return; }

    elTbody.innerHTML = ITEMS.map(it => `
      <tr>
        <td>${escapeHtml(it.code||'')}</td>
        <td>${escapeHtml(it.name||'')}</td>
        <td>${escapeHtml(it.faculty||'')}</td>
        <td>${num(it.credits)}</td><td>${num(it.credits_lt)}</td><td>${num(it.credits_th)}</td>
        <td>${it.semester_no ?? ''}</td>
        <td>${it.requirement_label || ''}</td>
        <td>${it.is_active ? '✓' : ''}</td>
      </tr>
    `).join('');
  }

  function renderRelations(){
    elRelBody.innerHTML = '';
    if (!CUR_ID){ elRelBody.innerHTML = `<tr><td colspan="3" class="cur-empty">Chưa chọn CTĐT.</td></tr>`; return; }
    if (!RELS.length){ elRelBody.innerHTML = `<tr><td colspan="3" class="cur-empty">Không có quan hệ học phần.</td></tr>`; return; }

    elRelBody.innerHTML = RELS.map(r => `
      <tr>
        <td><div>${escapeHtml(r.course_code||'')}</div><div style="opacity:.75">— ${escapeHtml(r.course_name||'')}</div></td>
        <td>${escapeHtml(r.relation_label||'')}</td>
        <td>${escapeHtml(r.related_code||'')} — ${escapeHtml(r.related_name||'')}</td>
      </tr>
    `).join('');
  }

  // actions
  async function selectCurriculum(id, pushUrl){
    CUR_ID = id || null;
    if (elExport) elExport.disabled = !CUR_ID;

    $$('.cur-list li').forEach(li => li.classList.toggle('active', Number(li.dataset.id)===Number(id)));

    elTbody.innerHTML   = `<tr><td colspan="9" class="cur-empty">Đang tải học phần...</td></tr>`;
    elRelBody.innerHTML = `<tr><td colspan="3" class="cur-empty">Đang tải quan hệ...</td></tr>`;
    text(elMajor,'—'); text(elFaculty,'—'); text(elYear,'—'); text(elCredits,'0.0');

    try { await Promise.all([loadItems(), loadRelations()]); }
    catch(e){ console.error('CURRICULUM: load fail', e); elTbody.innerHTML = `<tr><td colspan="9" class="cur-empty">Lỗi tải học phần.</td></tr>`; elRelBody.innerHTML = `<tr><td colspan="3" class="cur-empty">Lỗi tải quan hệ.</td></tr>`; }

    if (pushUrl){
      const u = new URL(location.href); u.searchParams.set('cur', String(id)); history.replaceState(null,'',u.toString());
    }
  }

  function bind(){
    elQ?.addEventListener('input', () => { page=1; loadCurricula().catch(()=>{}); });
    elClear?.addEventListener('click', () => { if (elQ){ elQ.value=''; page=1; } loadCurricula().catch(()=>{}); });

    elPrev?.addEventListener('click', () => { if (page>1){ page--; renderCurricula(); } });
    elNext?.addEventListener('click', () => { if (page<maxPage()){ page++; renderCurricula(); } });

    const refresh = () => loadItems().catch(()=>{});
    elFilter?.addEventListener('input', refresh);
    elSem?.addEventListener('change', refresh);
    elType?.addEventListener('change', refresh);
    elActive?.addEventListener('change', refresh);

    elExport?.addEventListener('click', () => {
      if (!CUR_ID) return;
      // Dùng endpoint UI đã map: name='ui_curriculum_pdf'
      const url = `/study/curriculum/pdf?cur=${encodeURIComponent(CUR_ID)}`;

      // (Nếu muốn tạm dùng export của Admin, uncomment dòng sau)
      // const url = `/admin/miscore/curriculumformmanageadmin/export_pdf?curriculum=${encodeURIComponent(CUR_ID)}`;

      window.open(url, '_blank', 'noopener');
    });
  }

  function mount(force=false){
    if (!host) return;
    if (!force && mounted) return;
    mounted = true;

    if (elExport) elExport.disabled = true;
    bind();

    const curParam = new URL(location.href).searchParams.get('cur');
    loadCurricula().then(() => {
      if (curParam){
        const found = ALL.find(x => String(x.id)===String(curParam));
        if (found) selectCurriculum(found.id, true);
      }
    }).catch(console.error);
  }

  // utils
  const escapeHtml = s => String(s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num = x => (x==null || x==='') ? '' : String(x);

  // auto-mount
  mount(true);
})();
