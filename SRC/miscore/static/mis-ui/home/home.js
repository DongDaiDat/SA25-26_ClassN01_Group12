// Home intro (v3) — idempotent mount, không ảnh hưởng global
(function(){
  const VER='v3'; console.log('HOME intro loaded', VER);
  let mounted=false;

  function mount(force=false){
    const root=document.querySelector('.home-wrap');
    if(!root) return;
    if(!force && (mounted || root.dataset.mounted==='1')) return;
    mounted=true; root.dataset.mounted='1';

    // (tuỳ chọn) chèn tên người dùng nếu tìm thấy ở topbar
    try{
      const who=document.querySelector('.topbar-user-name,[data-user-name]');
      const title=root.querySelector('.home-title');
      if(who && title && !title.dataset.personalized){
        const name=who.textContent.trim();
        if(name) title.innerHTML = `Chào mừng <b>${name}</b> đến với Hệ thống Quản lý Chương trình Đào tạo`;
        title.dataset.personalized='1';
      }
    }catch(_){}
  }

  function unmount(){
    mounted=false;
    const root=document.querySelector('.home-wrap');
    if(root) root.removeAttribute('data-mounted');
  }

  window.__forceMountHome=()=>mount(true);

  let tries=0;(function wait(){
    if(document.querySelector('.home-wrap')) return mount(true);
    if(++tries<40) setTimeout(wait,50);
  })();

  addEventListener('pagehide',unmount);
  addEventListener('popstate',unmount);
})();
