import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    file = fields.Binary(string="PDF File", attachment=True)
    annotation_version = fields.Integer(default=0, readonly=True)
    annotation_history_ids = fields.One2many(
        "pdf.annotation.history",
        "document_id",
        string="Annotation History",
    )
    annotation_history_count = fields.Integer(compute="_compute_annotation_history_count")
    latest_annotation_json = fields.Text(readonly=True)
    latest_annotated_attachment_id = fields.Many2one("ir.attachment", readonly=True)
    latest_annotated_by_id = fields.Many2one("res.users", readonly=True)
    latest_annotated_on = fields.Datetime(readonly=True)

    @api.depends("annotation_history_ids")
    def _compute_annotation_history_count(self):
        for document in self:
            document.annotation_history_count = len(document.annotation_history_ids)

    def _is_pdf_document(self):
        self.ensure_one()
        return self.mimetype == "application/pdf" or bool(self.file)

    def _get_or_create_source_attachment(self):
        self.ensure_one()
        if self.attachment_id:
            return self.attachment_id
        if not self.file:
            return False

        attachment = self.env["ir.attachment"].create(
            {
                "name": f"{self.name or 'document'}.pdf",
                "datas": self.file,
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        self.write({"attachment_id": attachment.id, "mimetype": "application/pdf"})
        return attachment

    def action_open_pdf_annotator(self):
        self.ensure_one()
        if not self._is_pdf_document():
            raise UserError(_("Only PDF documents can be annotated."))

        return {
            "type": "ir.actions.client",
            "name": _("PDF Annotator"),
            "tag": "pdf_document_annotator.annotator",
            "target": "new",
            "context": {
                "active_id": self.id,
            },
        }

    def action_view_annotation_history(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Annotation History"),
            "res_model": "pdf.annotation.history",
            "view_mode": "tree,form",
            "domain": [("document_id", "=", self.id)],
            "context": {"default_document_id": self.id},
            "target": "current",
        }

    def get_pdf_annotation_payload(self):
        self.ensure_one()
        if not self._is_pdf_document():
            raise UserError(_("Only PDF documents can be annotated."))

        attachment = self._get_or_create_source_attachment()
        return {
            "document_id": self.id,
            "document_name": self.name,
            "attachment_id": attachment.id if attachment else False,
            "attachment_url": f"/web/content/{attachment.id}?download=false" if attachment else False,
            "annotation_version": self.annotation_version,
            "latest_annotation_json": self.latest_annotation_json,
        }

    def save_pdf_annotation(self, annotation_json, note=None, tools_used=None, annotated_pdf_data=None):
        self.ensure_one()
        if not self._is_pdf_document():
            raise UserError(_("Only PDF documents can be annotated."))

        try:
            payload = json.loads(annotation_json or "{}")
        except json.JSONDecodeError as error:
            raise UserError(_("Invalid annotation payload: %s") % error) from error

        next_version = self.annotation_version + 1

        attachment = False
        if annotated_pdf_data:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"{self.name or 'document'}_annotated_v{next_version}.pdf",
                    "datas": annotated_pdf_data,
                    "mimetype": "application/pdf",
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )

        history = self.env["pdf.annotation.history"].create(
            {
                "document_id": self.id,
                "version": next_version,
                "name": _("Version %s") % next_version,
                "note": note,
                "annotation_json": annotation_json,
                "annotated_attachment_id": attachment.id if attachment else False,
                "user_id": self.env.user.id,
                "tools_used": ", ".join(tools_used or []),
                "page_count": payload.get("page_count", 0),
            }
        )

        values = {
            "annotation_version": next_version,
            "latest_annotation_json": annotation_json,
            "latest_annotated_attachment_id": attachment.id if attachment else False,
            "latest_annotated_by_id": self.env.user.id,
            "latest_annotated_on": fields.Datetime.now(),
            "mimetype": "application/pdf",
        }
        if annotated_pdf_data:
            values["file"] = annotated_pdf_data
        self.write(values)

        self.message_post(
            body=_("PDF annotations updated to version <b>%s</b> by %s.")
            % (next_version, self.env.user.display_name)
        )
        return {
            "ok": True,
            "version": next_version,
            "history_id": history.id,
        }

    def restore_pdf_annotation_version(self, history_id):
        self.ensure_one()
        history = self.env["pdf.annotation.history"].browse(history_id).exists()
        if not history or history.document_id != self:
            raise UserError(_("Invalid history entry."))

        self.write(
            {
                "latest_annotation_json": history.annotation_json,
                "latest_annotated_attachment_id": history.annotated_attachment_id.id,
                "latest_annotated_by_id": self.env.user.id,
                "latest_annotated_on": fields.Datetime.now(),
                "file": history.annotated_attachment_id.datas if history.annotated_attachment_id else self.file,
            }
        )
        self.message_post(
            body=_("Restored annotation snapshot from version <b>%s</b> by %s.")
            % (history.version, self.env.user.display_name)
        )
        return {"ok": True}
