# -*- coding: utf-8 -*-

{
    'name': 'Website Slider Link',
    'summary': 'This will open a Ifram',
    'version': '18.0.1.0.0',
    'author': 'Sachin/sachin.odoo@gmail.com',
    "license": "LGPL-3",
    'depends': ['website_slides_survey', 'website'],
    'data': [  
                
                'views/website_slide_template_inherit.xml',
                'views/website_slides_template_min_screen.xml',
                'views/survey_answer_view.xml',
                'views/survey_template_view.xml',
                'views/survey_templates_inherit.xml'
                
    		 ],

    'demo': [],
    'assets': {
        
        'web.assets_frontend': [
            'webside_slide_link/static/src/js/website_quizz_js.js',
            'webside_slide_link/static/src/js/website_slider_js.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
