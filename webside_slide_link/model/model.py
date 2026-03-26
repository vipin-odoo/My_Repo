# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import url_for



class SlideSlideLink(models.Model):

    _inherit = "slide.slide.link"

    is_default = fields.Boolean(string="Is Default")


    

class SlideSlide(models.Model):

    _inherit = "slide.slide"


    is_external_link = fields.Boolean('External link')
    new_url = fields.Char('External Url')
    custom_embed_code =fields.Html('Embed Code',compute="_compute_embed_code", readonly=True,store=True)


    def _generate_certification_url(self):
        """ get a map of certification url for certification slide from `self`. The url will come from the survey user input:
                1/ existing and not done user_input for member of the course
                2/ create a new user_input for member
                3/ for no member, a test user_input is created and the url is returned
            Note: the slide.slides.partner should already exist

            We have to generate a new invite_token to differentiate pools of attempts since the
            course can be enrolled multiple times.
        """
        certification_urls = {}
        for slide in self.filtered(lambda slide: slide.slide_type == 'certification' and slide.survey_id):
            if slide.channel_id.is_member:
                user_membership_id_sudo = slide.user_membership_id.sudo()
                certificate_attended_id = self.env['survey.user_input'].sudo().search([('slide_id','=',slide.id),('partner_id','=',self.env.user.partner_id.id)])
                if certificate_attended_id:
                    last_user_input = next(user_input for user_input in certificate_attended_id.sorted(
                        lambda user_input: user_input.create_date, reverse=True
                    ))
                    
                    
                    certification_urls[slide.id] = last_user_input.get_start_url()
                else:
                    user_input = slide.survey_id.sudo()._create_answer(
                        partner=self.env.user.partner_id,
                        check_attempts=False,
                        **{
                            'slide_id': slide.id,
                            'slide_partner_id': user_membership_id_sudo.id
                        },
                        invite_token=self.env['survey.user_input']._generate_invite_token()
                    )
                    certification_urls[slide.id] = user_input.get_start_url()
            else:
                user_input = slide.survey_id.sudo()._create_answer(
                    partner=self.env.user.partner_id,
                    check_attempts=False,
                    test_entry=True, **{
                        'slide_id': slide.id
                    }
                )
                certification_urls[slide.id] = user_input.get_start_url()
        return certification_urls



    @api.depends('document_id', 'slide_type', 'mime_type','is_external_link','new_url')
    def _compute_embed_code(self):
        base_url = request and request.httprequest.url_root
        for record in self:
            if not record.is_external_link:
                if not base_url:
                    base_url = record.get_base_url()
                if base_url[-1] == '/':
                    base_url = base_url[:-1]
                if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
                    slide_url = base_url + url_for('/slides/embed/%s?page=1' % record.id)
                    record.custom_embed_code='<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
                    record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
                elif record.slide_type == 'video' and record.document_id:
                    if not record.mime_type:
                        # embed youtube video
                        query = urls.url_parse(record.url).query
                        query = query + '&theme=light' if query else 'theme=light'
                        record.embed_code = '<iframe src="//www.youtube-nocookie.com/embed/%s?%s" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id, query)
                        record.custom_embed_code='<iframe src="//www.youtube-nocookie.com/embed/%s?%s" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id, query)
                    else:
                        # embed google doc video
                        record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
                        record.custom_embed_code='<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
                else:
                    record.embed_code = False
                    record.custom_embed_code=False
            else:
                if record.new_url:
                    record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true"  frameborder="0"></iframe>' % (record.new_url)
                    record.custom_embed_code='<video type="video/mp4" controls="1" autoplay="1" name="media" controlslist="nodownload" ><source src="%s" type="video/mp4"/></video>'% (record.new_url)
                else:
                    record.embed_code = False
                    record.custom_embed_code=False
    

    def get_linked_records_info(self):
    	web_link=False
    	if self.slide_type=='webpage':
    		for link in self.link_ids:
    			if link.is_default:
    				web_link=link.link

    	if web_link != False:
    		return [1,web_link]
    	else:
    		return [0]




