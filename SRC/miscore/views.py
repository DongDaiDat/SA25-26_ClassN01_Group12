# miscore/views.py
from django.http import HttpResponse, JsonResponse, Http404
from django.templatetags.static import static
from django.apps import apps
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.shortcuts import get_object_or_404

def ui_shell(request):
    css = static("mis-ui/style.css")
    js  = static("mis-ui/app.js")
    html = f"""<!doctype html>
<html lang="vi"><head>
  <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Education Management</title>
  <link rel="stylesheet" href="{css}"/>
</head><body>
  <div id="root"></div>
  <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script type="text/babel" src="{js}"></script>
</body></html>"""
    return HttpResponse(html)

def api_schools(request):
    """
    Trả JSON đúng shape cho trường School của bạn:
      { items: [ {id, name, university, is_active}, ... ] }
    """
    School = apps.get_model("miscore", "School")
    # Nếu University khác app hoặc khác tên, sửa lại chuỗi dưới đây
    # University = apps.get_model("miscore", "University")

    qs = School.objects.select_related("university").all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(university__name__icontains=q))

    qs = qs.order_by("name")

    items = [{
        "id": s.id,
        "name": s.name or "",
        "university": (s.university.name if getattr(s, "university_id", None) else ""),
        "is_active": bool(s.is_active),
    } for s in qs[:1000]]

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})


def api_faculties(request):
    """
    JSON: { items: [ {id, code, name, school, is_active}, ... ] }
    - school dùng str(School) => "Tên trường (Đại học ...)" nếu có university.
    """
    Faculty = apps.get_model("miscore", "Faculty")

    qs = (Faculty.objects
          .select_related("school", "school__university")
          .all())

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q) |
            Q(school__name__icontains=q) |
            Q(school__university__name__icontains=q)
        )

    order = request.GET.get("order") or "name"  # tuỳ chọn ?order=code|-name|-code
    if order in ("name", "code", "-name", "-code"):
        qs = qs.order_by(order)

    items = [{
        "id": f.id,
        "code": f.code or "",
        "name": f.name or "",
        "school": str(f.school) if getattr(f, "school_id", None) else "",
        "is_active": bool(getattr(f, "is_active", True)),
    } for f in qs[:2000]]

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})




def api_lecturers(request):
    """
    JSON: { items:[{id,name,faculty,school,position,is_active,email,phone}, ... ] }
    - Hỗ trợ ?q=, ?order= (name|faculty|school|position|-name|...), minimal paging client-side.
    """
    Lecturer = apps.get_model("miscore", "Lecturer")

    qs = (Lecturer.objects
          .select_related("faculty", "school", "school__university")
          .all())

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(position__icontains=q) |
            Q(faculty__name__icontains=q) | Q(faculty__code__icontains=q) |
            Q(school__name__icontains=q) |
            Q(email__icontains=q) | Q(phone__icontains=q)
        )

    order = (request.GET.get("order") or "name").strip()
    allowed = {
        "name": "name",
        "faculty": "faculty__name",
        "school": "school__name",
        "position": "position",
        "is_active": "is_active",
    }
    desc = order.startswith("-")
    key = order[1:] if desc else order
    order_by = allowed.get(key, "name")
    if desc:
        order_by = "-" + order_by
    qs = qs.order_by(order_by, "id")

    items = [{
        "id": r.id,
        "name": r.name or "",
        "faculty": r.faculty.name if r.faculty_id else "",
        "school": str(r.school) if r.school_id else "",
        "position": r.position or "",
        "is_active": bool(r.is_active),
        "email": r.email or "",
        "phone": r.phone or "",
    } for r in qs[:3000]]   # đủ rộng, UI sẽ paginate client-side

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})



def api_majors(request):
    """
    JSON: { items: [ {id, code, name, faculty, school, is_active}, ... ] }
    - ?q=  tìm theo code/name/faculty/school
    - ?order= code|name|faculty|school|is_active (thêm dấu '-' để đảo)
    """
    Major = apps.get_model("miscore", "Major")
    qs = (Major.objects
          .select_related("faculty", "school", "school__university")
          .all())

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q) |
            Q(faculty__name__icontains=q) | Q(faculty__code__icontains=q) |
            Q(school__name__icontains=q) |
            Q(school__university__name__icontains=q)
        )

    order = (request.GET.get("order") or "code").strip()
    allowed = {
        "code": "code",
        "name": "name",
        "faculty": "faculty__name",
        "school": "school__name",
        "is_active": "is_active",
    }
    desc = order.startswith("-")
    key  = order[1:] if desc else order
    order_by = allowed.get(key, "code")
    if desc:
        order_by = "-" + order_by
    qs = qs.order_by(order_by, "id")

    items = [{
        "id": m.id,
        "code": m.code or "",
        "name": m.name or "",
        "faculty": m.faculty.name if m.faculty_id else "",
        "school": str(m.school) if m.school_id else "",
        "is_active": bool(m.is_active),
    } for m in qs[:3000]]

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})


def api_courses(request):
    """
    JSON: { items:[{id,code,name,faculty,credits,credits_lt,credits_th,is_active}, ...] }
    - Hỗ trợ ?q=, ?order=(code|name|faculty|credits|credits_lt|credits_th|is_active, kèm dấu -)
    """
    Course = apps.get_model("miscore", "Course")

    qs = (Course.objects
          .select_related("faculty")
          .all())

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q) |
            Q(faculty__name__icontains=q) | Q(faculty__code__icontains=q)
        )

    order = (request.GET.get("order") or "code").strip()
    allowed = {
        "code": "code",
        "name": "name",
        "faculty": "faculty__name",
        "credits": "credits",
        "credits_lt": "credits_lt",
        "credits_th": "credits_th",
        "is_active": "is_active",
    }
    desc = order.startswith("-")
    key  = order[1:] if desc else order
    order_by = allowed.get(key, "code")
    if desc: order_by = "-" + order_by
    qs = qs.order_by(order_by, "id")

    items = [{
        "id": r.id,
        "code": r.code or "",
        "name": r.name or "",
        "faculty": r.faculty.name if r.faculty_id else "",
        "credits": float(r.credits) if r.credits is not None else 0.0,
        "credits_lt": float(r.credits_lt) if r.credits_lt is not None else 0.0,
        "credits_th": float(r.credits_th) if r.credits_th is not None else 0.0,
        "is_active": bool(r.is_active),
    } for r in qs[:3000]]

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})



def api_curricula(request):
    """
    JSON: { items: [{id, major, faculty, year}], ... }
    Hỗ trợ ?q=, ?order=(major|faculty|year, có thể kèm '-')
    """
    Curriculum = apps.get_model("miscore", "Curriculum")

    qs = (Curriculum.objects
          .select_related("major", "faculty")
          .all())

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(major__name__icontains=q) | Q(major__code__icontains=q) |
            Q(faculty__name__icontains=q) |
            Q(year__icontains=q)
        )

    order = (request.GET.get("order") or "major").strip()
    allowed = {
        "major": "major__name",
        "faculty": "faculty__name",
        "year": "-year",  # mặc định năm mới trước
    }
    desc = order.startswith("-")
    key  = order[1:] if desc else order
    order_by = allowed.get(key, "major__name")
    if desc:
        # nếu user cố ý '-year' lần nữa thì vẫn tôn trọng
        if not order_by.startswith("-"):
            order_by = "-" + order_by
        else:
            order_by = order_by[1:]
    qs = qs.order_by(order_by, "id")

    items = [{
        "id": c.id,
        "major": getattr(c.major, "name", "") or "",
        "faculty": str(c.faculty) if getattr(c, "faculty_id", None) else "",
        "year": int(c.year),
    } for c in qs[:3000]]

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})


def api_curriculum_items(request):
    """
    GET /api/curriculum-items?cur=<id>&q=&sem=&type=&active=0|1
    Trả: {
      ok: true,
      info: { id, major, faculty, year, total_active_credits },
      items: [{
        id, code, name, faculty, credits, credits_lt, credits_th,
        semester_no, requirement_type, requirement_label, is_active
      }, ...]
    }
    """
    Curriculum = apps.get_model("miscore", "Curriculum")
    ListCourse  = apps.get_model("miscore", "ListCourse")

    cur_id = request.GET.get("cur") or request.GET.get("curriculum")
    if not cur_id:
        raise Http404("Missing cur")

    try:
        cur = (Curriculum.objects
               .select_related("major", "faculty")
               .get(pk=cur_id))
    except Curriculum.DoesNotExist:
        raise Http404("Curriculum not found")

    qs = (ListCourse.objects
          .select_related("course", "course__faculty")
          .filter(curriculum=cur))

    # --- filters (client vẫn lọc tiếp, nhưng cho phép lọc nhẹ từ server) ---
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(course__code__icontains=q) |
            Q(course__name__icontains=q) |
            Q(course__faculty__name__icontains=q)
        )

    sem = (request.GET.get("sem") or "").strip()
    if sem and sem.lower() != "all":
        try:
            qs = qs.filter(semester_no=int(sem))
        except ValueError:
            pass

    rqt = (request.GET.get("type") or "").strip().upper()
    if rqt in {"COMPULSORY", "ELECTIVE"}:
        qs = qs.filter(requirement_type=rqt)

    if (request.GET.get("active") or "0") == "1":
        qs = qs.filter(is_active=True)

    items = []
    for r in qs.order_by("semester_no", "course__code"):
        c = r.course
        items.append({
            "id": r.id,
            "code": c.code or "",
            "name": c.name or "",
            "faculty": c.faculty.name if c.faculty_id else "",
            "credits": float(c.credits or 0),
            "credits_lt": float(c.credits_lt or 0),
            "credits_th": float(c.credits_th or 0),
            "semester_no": int(r.semester_no or 0),
            "requirement_type": r.requirement_type,
            "requirement_label": "Bắt buộc" if r.requirement_type == "COMPULSORY" else "Tự chọn",
            "is_active": bool(r.is_active),
        })

    total_active = (ListCourse.objects
                    .filter(curriculum=cur, is_active=True)
                    .aggregate(t=Coalesce(Sum("course__credits"), Decimal("0")))["t"] or Decimal("0"))

    return JsonResponse({
        "ok": True,
        "info": {
            "id": cur.id,
            "major": str(cur.major),
            "faculty": str(cur.faculty),
            "year": int(cur.year),
            "total_active_credits": float(total_active),
        },
        "items": items,
    }, json_dumps_params={"ensure_ascii": False})


def api_curriculum_relations(request):
    """
    GET /api/curriculum-relations?cur=<id>
    Trả: {
      ok: true,
      items: [{
        course_code, course_name,
        relation_type, relation_label,
        related_code, related_name
      }, ...]
    }
    """
    Curriculum = apps.get_model("miscore", "Curriculum")
    ListCourseRelation = apps.get_model("miscore", "ListCourseRelation")

    cur_id = request.GET.get("cur") or request.GET.get("curriculum")
    if not cur_id:
        raise Http404("Missing cur")

    try:
        _ = Curriculum.objects.only("id").get(pk=cur_id)
    except Curriculum.DoesNotExist:
        raise Http404("Curriculum not found")

    rels = (ListCourseRelation.objects
            .select_related("course_item__course", "related_item__course")
            .filter(curriculum_id=cur_id)
            .order_by("course_item__course__code", "relation_type", "related_item__course__code"))

    label = {"PREREQUISITE": "Tiên quyết", "PREPARATORY": "Học trước", "COREQUISITE": "Song hành"}

    out = []
    for r in rels:
        a = r.course_item.course
        b = r.related_item.course
        out.append({
            "course_code": a.code or "",
            "course_name": a.name or "",
            "relation_type": r.relation_type,
            "relation_label": label.get(r.relation_type, r.relation_type),
            "related_code": b.code or "",
            "related_name": b.name or "",
        })

    return JsonResponse({"ok": True, "items": out}, json_dumps_params={"ensure_ascii": False})




def api_tuitions(request):
    """
    JSON: { items: [ {id,curriculum_id,major,faculty,year,total_credits,price_per_credit,total_amount,note,updated_at}, ... ] }
    - Hỗ trợ ?q=
    - Hỗ trợ ?order=(major|faculty|year|total_credits|price_per_credit|total_amount|updated_at) kèm '-' để đảo chiều.
    - Trả tối đa 3000 bản ghi, UI tự paginate client-side.
    """
    Tuition = apps.get_model("miscore", "Tuition")

    qs = (Tuition.objects
          .select_related("curriculum", "curriculum__major", "curriculum__faculty")
          .all())

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(curriculum__major__name__icontains=q) |
            Q(curriculum__faculty__name__icontains=q) |
            Q(curriculum__year__icontains=q) |
            Q(note__icontains=q)
        )

    order = (request.GET.get("order") or "major").strip()
    allowed = {
        "major": "curriculum__major__name",
        "faculty": "curriculum__faculty__name",
        "year": "curriculum__year",
        "total_credits": "total_credits",
        "price_per_credit": "price_per_credit",
        "total_amount": "total_amount",
        "updated_at": "updated_at",
    }
    desc = order.startswith("-")
    key = order[1:] if desc else order
    order_by = allowed.get(key, "curriculum__major__name")
    if desc:
        order_by = "-" + order_by
    qs = qs.order_by(order_by, "id")

    items = [{
        "id": r.id,
        "curriculum_id": r.curriculum_id,
        "major": r.curriculum.major.name if r.curriculum and r.curriculum.major_id else "",
        "faculty": r.curriculum.faculty.name if r.curriculum and r.curriculum.faculty_id else "",
        "year": r.curriculum.year if r.curriculum else None,
        "total_credits": float(r.total_credits or 0),
        "price_per_credit": float(r.price_per_credit or 0),
        "total_amount": float(r.total_amount or 0),
        "note": r.note or "",
        "updated_at": r.updated_at.strftime("%Y-%m-%d %H:%M:%S") if r.updated_at else "",
    } for r in qs[:3000]]

    return JsonResponse({"items": items}, json_dumps_params={"ensure_ascii": False})

def api_me(request):
    """
    Trả trạng thái đăng nhập để UI render:
    { ok, is_auth, username, name, email, role, is_staff, is_superuser }
    role lấy từ Profile.role nếu có, mặc định 'STUDENT'
    """
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"ok": True, "is_auth": False})

    Profile = apps.get_model("miscore", "Profile")
    prof = Profile.objects.filter(user_id=user.id).first()
    role = getattr(prof, "role", "STUDENT")

    return JsonResponse({
        "ok": True,
        "is_auth": True,
        "username": user.get_username(),
        "name": (user.get_full_name() or user.get_username()),
        "email": user.email or "",
        "role": role,                  # STUDENT | STAFF | OFFICE
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    })

def api_whoami(request):
    u = request.user
    if not u.is_authenticated:
        return JsonResponse({"ok": False, "user": None})
    role = getattr(getattr(u, "profile", None), "role", "")
    label = {"STAFF":"Cán bộ","OFFICE":"Phòng ban","STUDENT":"Sinh viên"}.get(
        role, "Cán bộ" if u.is_staff else "Sinh viên"
    )
    return JsonResponse({
        "ok": True,
        "user": {
            "id": u.id,
            "username": u.username,
            "full_name": u.get_full_name() or u.username,
            "email": u.email,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
            "role": role,
            "role_label": label,
        }
    })


def ui_export_curriculum_pdf(request):
    Curriculum = apps.get_model("miscore", "Curriculum")
    ListCourse = apps.get_model("miscore", "ListCourse")
    # nhận ?cur=ID (hoặc ?curriculum=ID)
    cid = request.GET.get("cur") or request.GET.get("curriculum")
    if not cid:
        raise Http404("Missing cur")

    cur = get_object_or_404(
        Curriculum.objects.select_related("major", "faculty"),
        pk=cid
    )
    items = (
        ListCourse.objects
        .select_related("course", "course__faculty")
        .filter(curriculum=cur)
        .order_by("semester_no", "course__code")
    )
    total_active = (
        ListCourse.objects
        .filter(curriculum=cur, is_active=True)
        .aggregate(t=Coalesce(Sum("course__credits"), Decimal("0")))["t"]
        or Decimal("0")
    )

    # dùng lại util render của Admin (đã hoạt động OK)
    from .pdf_utils import render_curriculum_pdf
    pdf_bytes = render_curriculum_pdf(cur, items, total_active)

    fname = f'CTDT_{cur.major}_{cur.year}.pdf'.replace(" ", "_")
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{fname}"'
    return resp