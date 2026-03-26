# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from collections import defaultdict

import base64
import json
import logging
import math
import werkzeug

from odoo import http, tools, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class WebsiteSlidesInherit(WebsiteProfile):
    _slides_per_page = 12
    _slides_per_aside = 20
    _slides_per_category = 4
    _channel_order_by_criterion = {
        'vote': 'total_votes desc',
        'view': 'total_views desc',
        'date': 'create_date desc',
    }


    def _get_slide_quiz_partner_info(self, slide, quiz_done=False):
        return slide._compute_quiz_info(request.env.user.partner_id, quiz_done=quiz_done)[slide.id]



    def _get_slide_quiz_data(self, slide):
        slide_completed = slide.user_membership_id.sudo().completed
        values = {
            'slide_questions': [{
                'id': question.id,
                'question': question.question,
                'image_publish':question.image_publish,
                'image':question.image,
                'answer_ids': [{
                    'id': answer.id,
                    'text_value': answer.text_value,
                    'is_correct': answer.is_correct if slide_completed or request.website.is_publisher() else None,
                    'comment': answer.comment if request.website.is_publisher else None
                } for answer in question.sudo().answer_ids],
            } for question in slide.question_ids]
        }
        if 'slide_answer_quiz' in request.session:
            slide_answer_quiz = json.loads(request.session['slide_answer_quiz'])
            if str(slide.id) in slide_answer_quiz:
                values['session_answers'] = slide_answer_quiz[str(slide.id)]
        values.update(self._get_slide_quiz_partner_info(slide))
        return values



    @http.route('/slides/slide/quiz/get', type="json", auth="public", website=True)
    def slide_quiz_get(self, slide_id):
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        slide = fetch_res['slide']
        return self._get_slide_quiz_data(slide)
