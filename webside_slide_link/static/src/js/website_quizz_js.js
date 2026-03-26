odoo.define('webside_slide_link.QuizCustom', function (require) {
"use strict";


    var core = require('web.core');
    var publicwidget = require('web.public.widget').Quiz
    var QWeb = core.qweb;
    var { Quiz } = require('@website_slides/js/slides_course_quiz');

    Quiz.include({
    xmlDependencies: (Quiz.prototype.xmlDependencies || []).concat(
        ["/webside_slide_link/static/src/xml/website_full_quizz.xml"]
    ),
            /**
         * @override
         */
        willStart: async function () {
            
            var defs = [this._super.apply(this, arguments)];
            if (!this.quiz) {
                defs.push(this._fetchQuiz());
            }
            return Promise.all(defs);
        },

});
});


