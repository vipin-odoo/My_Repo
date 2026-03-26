from odoo import http, _
from odoo import api, fields, models, _

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, content_disposition, route

class PortalAccount(CustomerPortal):

    @route(['/my/payslip/download/<int:payslip_id>'], type='http', auth="public")
    def download_pdf(self, payslip_id, **kw):
        payslip_id = request.env['hr.payslip'].sudo().search([('id','=',payslip_id)], limit=1)
        if not payslip_id:
            return None
        pdf, _ = request.env.ref('om_hr_payroll.action_report_payslip').sudo()._render_qweb_pdf(payslip_id.id)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

        
    
