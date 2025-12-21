// static/mis-ui/news/news.js (v3)
(function () {
  const VER = 'v3';
  console.log('NEWS: file loaded', VER);

  function q(sel, root=document){ return root.querySelector(sel); }
  function qa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

  // Lấy ngày mới nhất và đổ "Cập nhật gần nhất"
  function setLastUpdate() {
    const dates = qa('.news-card').map(n => n.getAttribute('data-date') || '');
    const latest = dates.sort().slice(-1)[0] || '';
    if (latest) {
      const [y,m,d] = latest.split('-');
      q('#news-last-update').textContent = `${d}/${m}/${y}`;
    }
  }

  // Render “Bản tin nhanh” (5 tin mới nhất)
  function renderQuickList() {
    const list = q('#news-quick');
    if (!list) return;
    const cards = qa('.news-card').sort((a,b)=> (a.dataset.date < b.dataset.date ? 1 : -1));
    list.innerHTML = cards.slice(0,5).map(c=>{
      const date = c.dataset.date.split('-').reverse().join('/');
      const title = q('.news-card__title', c).textContent.trim();
      return `<li><b>${date}</b> — <a href="#!" class="news-jump">${title}</a></li>`;
    }).join('');
    // nhảy tới card khi click
    list.addEventListener('click', e=>{
      const a = e.target.closest('.news-jump'); if(!a) return;
      const t = a.textContent.trim();
      const card = qa('.news-card').find(c => q('.news-card__title', c).textContent.trim() === t);
      if(card){ card.scrollIntoView({behavior:'smooth', block:'center'}); card.classList.add('pulse');
        setTimeout(()=>card.classList.remove('pulse'), 800);
      }
      e.preventDefault();
    });
  }

  // Lọc theo chip + ô tìm
  function setupFilter() {
    const chips = qa('.news-chip');
    const input = q('#news-q');
    let cat = 'all';

    function apply() {
      const kw = (input.value || '').toLowerCase().trim();
      const cards = qa('.news-card');
      let visible = 0;

      cards.forEach(c=>{
        const tags = (c.dataset.tags || '').toLowerCase();
        const byCat = (cat === 'all') || tags.includes(cat);
        const text = (q('.news-card__title', c).textContent + ' ' +
                      q('.news-card__desc', c).textContent + ' ' + tags).toLowerCase();
        const byKw = !kw || text.includes(kw);
        const show = byCat && byKw;
        c.style.display = show ? '' : 'none';
        if (show) visible++;
      });

      q('.news-empty').hidden = (visible !== 0);
    }

    chips.forEach(b=>{
      b.addEventListener('click', ()=>{
        chips.forEach(x=>x.classList.remove('is-active'));
        b.classList.add('is-active');
        cat = b.dataset.filter || 'all';
        apply();
      });
    });
    input.addEventListener('input', apply);

    apply();
  }

  // Hiệu ứng nhỏ khi nhảy tới card
  const stylePulse = document.createElement('style');
  stylePulse.textContent = `.news-card.pulse{ box-shadow:0 0 0 4px rgba(14,165,233,.25); transition:box-shadow .2s; }`;
  document.head.appendChild(stylePulse);

  // Kick
  document.addEventListener('DOMContentLoaded', ()=>{
    setLastUpdate();
    renderQuickList();
    setupFilter();
  });
})();
