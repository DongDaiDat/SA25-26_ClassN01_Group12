from django.urls import path
from . import views

urlpatterns = [
    # UI shell: trả về giao diện mis-ui/index.html
    path("", views.ui_shell, name="root-ui"),
    path("ui/", views.ui_shell, name="ui"),

    # APIs
    path("api/schools", views.api_schools, name="api-schools"),
    path("api/faculties", views.api_faculties, name="api-faculties"),
    path("api/lecturers", views.api_lecturers, name="api-lecturers"),
    path("api/majors", views.api_majors, name="api-majors"),
    path("api/courses", views.api_courses, name="api-courses"),
    path("api/curricula", views.api_curricula, name="api_curricula"),
    path("api/curriculum-items", views.api_curriculum_items, name="api_curriculum_items"),
    path("api/curriculum-relations", views.api_curriculum_relations, name="api_curriculum_relations"),
    path("api/tuitions", views.api_tuitions, name="api_tuitions"),
    path("api/me", views.api_me, name="api_me"),
    path("api/whoami", views.api_whoami, name="api_whoami"),
    path("study/curriculum/pdf", views.ui_export_curriculum_pdf, name="ui_curriculum_pdf"),
]
