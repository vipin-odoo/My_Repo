from odoo.addons.base_rest.controllers import main
from odoo.http import content_disposition, request, route, serialize_exception

class MyRestController(main.RestController):
    _root_path = '/my_services_api/'
    _collection_name = 'base_rest_auth_user_service.services'




# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from collections import defaultdict

import base64
import json
import logging
import math
import werkzeug
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad


from odoo import http, tools, _
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class WebsiteSlides(WebsiteProfile):



    def decrypt(self,enc):
        key="aR1h7EefwlPNVkvTHwfs6w=="
        enc = base64.b64decode(enc)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        return unpad(cipher.decrypt(enc),16)

    #http://localhost:8069/download/certificate?login=sachin@gmail.com&password=admin&db=Test-api&certificate=5

    @http.route('''/download/certificate''', type='http', auth="public", website=True, sitemap=True)
    def action_get_certificate(self, **kwargs):
        token = self.decrypt(kwargs['token'].replace(' ', '+'))
        key =self.decrypt(kwargs['key'].replace(' ', '+'))
        logging.info("----------------%s",str(token.decode("utf-8")))
        logging.info("----------------%s",str(key.decode("utf-8")))
        logging.info("----------------%s",str(kwargs['db']))
        survey_id = request.env["survey.user_input"].sudo().browse(int(kwargs['certificate']))
        uid = request.session.authenticate(kwargs['db'], key.decode("utf-8"), token.decode("utf-8"))
        return request.redirect('/survey/'+str(survey_id.survey_id.id)+'/get_certification')
        
    #http://localhost:8069/get/slide/view?login=sachin@gmail.com&password=admin&db=Test-api&slide=5
    
    @http.route('''/get/slide/view''', type='http', auth="public", website=True, sitemap=True)
    def action_view_certificate(self, **kwargs):
        token = self.decrypt(kwargs['token'].replace(' ', '+'))
        key =self.decrypt(kwargs['key'].replace(' ', '+'))
        uid = request.session.authenticate(kwargs['db'], key, token)
        return request.redirect('/slides/'+str(kwargs['slide']))
    #http://localhost:8069/get/certificate/exam/view?login=sachin@gmail.com&password=admin&db=Test-api&slide_id=38
        
    @http.route('''/get/certificate/exam/view''', type='http', auth="public", website=True, sitemap=True)
    def action_view_exam(self, **kwargs):
        token = self.decrypt(kwargs['token'].replace(' ', '+'))
        key =self.decrypt(kwargs['key'].replace(' ', '+'))
        uid = request.session.authenticate(kwargs['db'], key, token)
        return request.redirect('/slides_survey/slide/get_certification_url?slide_id='+str(kwargs['slide_id']))
    

    
