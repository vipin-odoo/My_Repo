{
    "name": "School Management",
    "summary": "Manage schools, students, teachers, and enrollments",
    "description": """
School Management module for Odoo 19.
Includes student, teacher, course, and enrollment management.
    """,
    "author": "Codex",
    "website": "https://example.com",
    "category": "Education",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "data/school_sequence.xml",
        "security/ir.model.access.csv",
        "views/school_student_views.xml",
        "views/school_teacher_views.xml",
        "views/school_course_views.xml",
        "views/school_enrollment_views.xml",
        "views/school_menu_views.xml",
    ],
    "demo": [
        "data/school_demo.xml",
    ],
    "application": True,
    "installable": True,
}
