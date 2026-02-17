from odoo import fields, models


class PdfAnnotationHistory(models.Model):
    _name = "pdf.annotation.history"
    _description = "PDF Annotation History"
    _order = "version desc, create_date desc"

    document_id = fields.Many2one(
        "document.document",
        required=True,
        ondelete="cascade",
        index=True,
    )
    version = fields.Integer(required=True, index=True)
    name = fields.Char(required=True)
    note = fields.Text()
    annotation_json = fields.Text(required=True)
    annotated_attachment_id = fields.Many2one("ir.attachment", string="Annotated PDF")
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    tools_used = fields.Char(help="Comma-separated tool names used in this revision")
    page_count = fields.Integer()

    _sql_constraints = [
        (
            "document_version_unique",
            "unique(document_id, version)",
            "A document version must be unique.",
        )
    ]
