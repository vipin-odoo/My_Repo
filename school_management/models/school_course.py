from odoo import api, fields, models


class SchoolCourse(models.Model):
    _name = "school.course"
    _description = "Course"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Text()
    teacher_id = fields.Many2one("school.teacher", string="Teacher")
    seats = fields.Integer(default=30)
    enrollment_ids = fields.One2many("school.enrollment", "course_id", string="Enrollments")
    enrolled_count = fields.Integer(compute="_compute_enrolled_count", store=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("school_course_code_unique", "UNIQUE(code)", "Course code must be unique."),
    ]

    @api.depends("enrollment_ids")
    def _compute_enrolled_count(self):
        for course in self:
            course.enrolled_count = len(course.enrollment_ids)
