from odoo import fields, models


class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "Teacher"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    subject = fields.Char(tracking=True)
    email = fields.Char()
    phone = fields.Char()
    course_ids = fields.One2many("school.course", "teacher_id", string="Courses")
    active = fields.Boolean(default=True)
