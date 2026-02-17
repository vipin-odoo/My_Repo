from odoo import api, fields, models


class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Student"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    student_code = fields.Char(required=True, copy=False, readonly=True, default="New")
    date_of_birth = fields.Date(tracking=True)
    email = fields.Char()
    phone = fields.Char()
    active = fields.Boolean(default=True)
    enrollment_ids = fields.One2many("school.enrollment", "student_id", string="Enrollments")

    _sql_constraints = [
        ("school_student_code_unique", "UNIQUE(student_code)", "Student code must be unique."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("student_code", "New") == "New":
                vals["student_code"] = self.env["ir.sequence"].next_by_code("school.student") or "New"
        return super().create(vals_list)
