from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_reconcile_registered_payments(self):
        """Reconcile posted invoice lines against posted payment entries for the same partner/account."""
        invoice_moves = self.filtered(
            lambda move: move.is_invoice(include_receipts=False)
            and move.state == "posted"
            and move.payment_state in ("not_paid", "partial", "in_payment")
        )

        for move in invoice_moves:
            receivable_payable_lines = move.line_ids.filtered(
                lambda line: line.account_id.account_type in ("asset_receivable", "liability_payable")
                and not line.reconciled
            )
            if not receivable_payable_lines:
                continue

            partner = move.commercial_partner_id
            company = move.company_id

            payment_lines = self.env["account.move.line"].search(
                [
                    ("company_id", "=", company.id),
                    ("partner_id", "=", partner.id),
                    ("account_id", "in", receivable_payable_lines.account_id.ids),
                    ("payment_id", "!=", False),
                    ("parent_state", "=", "posted"),
                    ("reconciled", "=", False),
                ],
                order="date, id",
            )

            for account in receivable_payable_lines.account_id:
                invoice_lines = receivable_payable_lines.filtered(lambda line: line.account_id == account)
                matching_payment_lines = payment_lines.filtered(lambda line: line.account_id == account)
                if matching_payment_lines:
                    (invoice_lines | matching_payment_lines).reconcile()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Reconciliation complete"),
                "message": _("Registered payments were reconciled against this invoice when matching entries were found."),
                "type": "success",
                "sticky": False,
            },
        }
