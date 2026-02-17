from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SchoolEnrollment(models.Model):
    _name = "school.enrollment"
    _description = "Enrollment"

    name = fields.Char(compute="_compute_name", store=True)
    student_id = fields.Many2one("school.student", required=True, ondelete="cascade")
    course_id = fields.Many2one("school.course", required=True, ondelete="cascade")
    enrollment_date = fields.Date(default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )

    _sql_constraints = [
        (
            "school_enrollment_unique_student_course",
            "UNIQUE(student_id, course_id)",
            "A student can only be enrolled once per course.",
        ),
    ]

    @api.depends("student_id", "course_id")
    def _compute_name(self):
        for rec in self:
            if rec.student_id and rec.course_id:
                rec.name = f"{rec.student_id.name} - {rec.course_id.name}"
            else:
                rec.name = "New Enrollment"

    @api.constrains("course_id")
    def _check_course_seats(self):
        for rec in self:
            if not rec.course_id:
                continue
            active_enrollments = self.search_count(
                [
                    ("course_id", "=", rec.course_id.id),
                    ("id", "!=", rec.id),
                    ("state", "in", ["draft", "enrolled", "completed"]),
                ]
            ) + 1
            if rec.course_id.seats and active_enrollments > rec.course_id.seats:
                raise ValidationError("No seats available for this course.")
