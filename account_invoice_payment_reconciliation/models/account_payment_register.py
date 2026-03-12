from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _get_batch_available_journals(self, batch_result):
        """Keep default behavior and additionally expose cash journals."""
        journals = super()._get_batch_available_journals(batch_result)

        company = self.company_id or self.env.company
        cash_journals = self.env["account.journal"].search(
            [
                ("company_id", "=", company.id),
                ("type", "=", "cash"),
            ]
        )
        return (journals | cash_journals).sorted(key=lambda journal: journal.sequence)
