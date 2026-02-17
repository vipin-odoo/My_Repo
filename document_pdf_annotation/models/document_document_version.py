import json

from odoo import fields, models


class DocumentDocumentVersion(models.Model):
    _name = "document.document.version"
    _description = "Document PDF Version"
    _order = "version_number desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    document_id = fields.Many2one("document.document", required=True, ondelete="cascade", index=True)
    version_number = fields.Integer(required=True, default=1)
    file_data = fields.Binary(string="Annotated PDF", attachment=True)
    file_name = fields.Char(string="Filename")
    annotation_data = fields.Text(string="Annotation Data JSON")
    created_by = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    created_on = fields.Datetime(required=True, default=fields.Datetime.now)

    _sql_constraints = [
        (
            "document_version_unique",
            "unique(document_id, version_number)",
            "Version number must be unique per document.",
        )
    ]

    def _compute_name(self):
        for record in self:
            record.name = f"{record.document_id.display_name} - v{record.version_number}"

    def action_open_in_annotator(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "document_pdf_annotation.client_action",
            "name": "Annotate PDF",
            "params": {
                "document_id": self.document_id.id,
                "version_id": self.id,
            },
        }

    def get_annotation_payload(self):
        self.ensure_one()
        if not self.annotation_data:
            return {}
        try:
            return json.loads(self.annotation_data)
        except json.JSONDecodeError:
            return {}
