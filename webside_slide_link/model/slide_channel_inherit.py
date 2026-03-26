# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import url_for



class SlideChannel(models.Model):

    _inherit = "slide.channel"



    @api.model
    def create(self, vals):
        res=super(SlideChannel, self).create(vals)
        channel_partner_env=self.env['slide.channel.partner'].sudo()
        user_ids = self.env['res.users'].sudo().search([('id','!=',self.env.user.id)])
        for user in user_ids:


            enrol_id=channel_partner_env.create({
                            'channel_id':res.id,
                            'partner_id':user.partner_id.id,

                        })

        return res



    def write(self, vals):
        res= super(SlideChannel, self).write(vals)
        if 'active' in vals:
            if vals['active']:
                channel_partner_env=self.env['slide.channel.partner'].sudo()
                user_ids = self.env['res.users'].sudo().search([('id','!=',self.env.user.id)])
                for user in user_ids:
                    enrol_id=channel_partner_env.search([('channel_id','=',self.id),('partner_id','=',user.partner_id.id)])
                    if not enrol_id:

                        new_enrol_id=channel_partner_env.create({
                                        'channel_id':self.id,
                                        'partner_id':user.partner_id.id,

                                    })




        return res
    
