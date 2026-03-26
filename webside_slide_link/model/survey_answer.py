# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import url_for



class SurveyQuestion(models.Model):

    _inherit = "survey.question"
    
    image_publish = fields.Boolean("Publish Image")

    image = fields.Binary('Image')



class SlideAnswer(models.Model):

    _inherit = "slide.question"
    
    image_publish = fields.Boolean("Publish Image")

    image = fields.Binary('Image')


    
