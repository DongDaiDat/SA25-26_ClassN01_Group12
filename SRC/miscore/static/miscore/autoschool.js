// miscore/static/miscore/autoschool.js
(function(){
  var $ = (window.django && window.django.jQuery) || window.jQuery;
  if (!$) { console.warn("autoschool: jQuery not found"); return; }

  function ready(fn){
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function(){
    var $fac = $("#id_faculty");
    // Ưu tiên input disabled 'school_name'; fallback readonly div '#id_school'
    var $out = $("#id_school_name");
    if (!$out.length) $out = $("#id_school");

    if (!$fac.length || !$out.length) {
      console.warn("autoschool: missing elements", {fac: $fac.length, out: $out.length});
      return;
    }

    function setOut(text){
      if ($out.is("input,textarea")) $out.val(text || "");
      else $out.text(text || "");
    }

    function update(){
      var fid = $fac.val();
      if (!fid) { setOut(""); return; }
      $.get("/admin/miscore/major/ajax/faculty-school/", { faculty: fid })
       .done(function(res){
          setOut((res && res.ok && res.school_name) ? res.school_name : "");
       })
       .fail(function(){ setOut(""); });
    }

    update();                 // nạp ngay khi mở form
    $fac.on("change", update); // và mỗi lần đổi Faculty
  });
})();
