// Structure / Major – view-only (v10)
(function(){
  const VER = "v10";
  console.log("MAJ: file loaded", VER);

  const KEY = "structure-major";
  let mounted = false;
  const els = {};
  const state = { q:"", order:"code", page:1, size:100, items:[] }; // 100/ trang

  const $  = (s,r=document)=>r.querySelector(s);
  const $$ = (s,r=document)=>Array.from(r.querySelectorAll(s));
  const esc = s => (s==null?"":String(s)).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

  const okIcon = () => '<svg class="status-ic ok" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path d="M7 12l3 3 6-6" stroke-width="2"></path></svg>';
  const noIcon = () => '<svg class="status-ic no" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke-width="2"></circle><path d="M8 8l8 8M16 8l-8 8" stroke-width="2"></path></svg>';

  function getEls(){
    els.tbody = $("#maj-tbody");
    els.q = $("#maj-q");
    els.clear = $("#maj-clear");
    els.prev = $("#maj-prev");
    els.next = $("#maj-next");
    els.pageinfo = $("#maj-pageinfo");
    els.sortable = $$(".major-table thead th.sortable");
    return !!els.tbody;
  }

  function syncSortUI(){
    els.sortable.forEach(th=>{
      const key = th.getAttribute("data-key");
      const desc = state.order.startsWith("-");
      const cur  = desc ? state.order.slice(1) : state.order;
      const span = th.querySelector(".sort-ind");
      if(!span) return;
      if(key===cur){ span.classList.add("show"); span.classList.toggle("desc", desc); }
      else { span.classList.remove("show","desc"); }
    });
  }

  const apiUrl = ()=> {
    const p = [];
    if(state.q) p.push("q="+encodeURIComponent(state.q));
    p.push("order="+encodeURIComponent(state.order));
    return "/api/majors" + (p.length? "?"+p.join("&") : "");
  };

  async function load(){
    els.tbody.innerHTML = '<tr><td colspan="5" class="major-empty">Đang tải…</td></tr>';
    syncSortUI();
    try{
      const res = await fetch(apiUrl(), { headers:{Accept:"application/json"}, credentials:"same-origin" });
      if(!res.ok) throw new Error("HTTP "+res.status);
      const data = await res.json();
      state.items = Array.isArray(data.items)? data.items : [];
      state.page = 1;
      console.log("MAJ: loaded", state.items.length, "items");
      render();
    }catch(e){
      console.error("MAJ: load error", e);
      els.tbody.innerHTML = '<tr><td colspan="5" class="major-empty">Lỗi tải dữ liệu</td></tr>';
    }
  }

  function render(){
    const total = state.items.length;
    const pages = Math.max(1, Math.ceil(total/state.size));
    state.page = Math.min(state.page, pages);

    const start = (state.page-1)*state.size;
    const rows = state.items.slice(start, start+state.size);

    if(!rows.length){
      els.tbody.innerHTML = '<tr><td colspan="5" class="major-empty">Không có dữ liệu</td></tr>';
    }else{
      els.tbody.innerHTML = rows.map(r=>`
        <tr>
          <td>${esc(r.code)}</td>
          <td>${esc(r.name)}</td>
          <td>${esc(r.faculty)}</td>
          <td>${esc(r.school)}</td>
          <td>${r.is_active ? okIcon() : noIcon()}</td>
        </tr>
      `).join("");
    }

    els.pageinfo.textContent = `${state.page}/${pages}`;
    els.prev.disabled = state.page<=1;
    els.next.disabled = state.page>=pages;
  }

  function bind(){
    // sort
    els.sortable.forEach(th=>{
      th.addEventListener("click", ()=>{
        const key = th.getAttribute("data-key");
        const d = state.order.startsWith("-");
        const cur = d ? state.order.slice(1) : state.order;
        state.order = (key===cur) ? (d? key : "-"+key) : key;
        load();
      });
    });
    // search debounce
    let t;
    els.q.addEventListener("input", ()=>{
      clearTimeout(t);
      t = setTimeout(()=>{ state.q=(els.q.value||"").trim(); state.page=1; load(); },300);
    });
    els.clear.addEventListener("click", ()=>{ els.q.value=""; state.q=""; state.page=1; load(); });

    // paging (client)
    els.prev.addEventListener("click", ()=>{ if(state.page>1){ state.page--; render(); } });
    els.next.addEventListener("click", ()=>{ const pages=Math.max(1,Math.ceil(state.items.length/state.size)); if(state.page<pages){ state.page++; render(); } });
  }

  function mount(){
    if(mounted) return true;
    if(!getEls()) return false;
    mounted = true;
    console.log("MAJ: mount OK");
    bind();
    load();
    return true;
  }

  document.addEventListener("misui:page-mounted", ev=>{
    if(ev?.detail?.key === KEY) mount();
  });

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", ()=>setTimeout(mount,0));
  else setTimeout(mount,0);

  window.__forceMountMajor = mount;
})();
