// miscore/static/miscore/autofaculty.js
(function(){
  var $ = (window.django && window.django.jQuery) || window.jQuery;
  if (!$) { console.warn("autofaculty: jQuery not found"); return; }
  console.log("autofaculty: loaded v7");

  function ready(fn){
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function(){
    // Major: id hoặc name (khi select2)
    var $major = $("#id_major");
    if (!$major.length) $major = $('[name="major"]');

    // Ô hiển thị tên khoa – gom hết các khả năng Django Admin render
    var $facNm = $(
      "#id_faculty_name, " +                // input có id
      "[name='faculty_name'], " +           // input theo name
      ".field-faculty_name input, " +       // input trong row theo class field-*
      ".form-row.field-faculty_name input, "+
      ".field-faculty_name .readonly"       // fallback dạng div.readonly
    );

    if (!$major.length || !$facNm.length) {
      console.warn("autofaculty: missing elements", {
        major: $major.length, facNm: $facNm.length
      });
      return;
    }

    function setFacultyName(name){
      var text = name || "";
      $facNm.each(function(){
        var $el = $(this);
        if ($el.is("input,textarea")) $el.val(text);
        else $el.text(text);
      });
    }

    function update(){
      var mid = $major.val();
      console.log("autofaculty:update", {mid: mid, facNmCount: $facNm.length});
      if (!mid) { setFacultyName(""); return; }
      $.get("/admin/miscore/curriculum/ajax/major-faculty/", { major: mid })
       .done(function(res){
          console.log("autofaculty:resp", res);
          if (res && res.ok) setFacultyName(res.faculty_name || "");
          else setFacultyName("");
       })
       .fail(function(err){
          console.warn("autofaculty:ajax fail", err);
          setFacultyName("");
       });
    }

    // chạy ngay + khi đổi ngành (kể cả select2)
    update();
    $major.on("change", update);
    try { $major.on("select2:select", update); } catch(e) {}
  });
})();
