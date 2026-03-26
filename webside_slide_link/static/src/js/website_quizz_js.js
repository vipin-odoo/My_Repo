/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Quiz } from "@website_slides/js/slides_course_quiz";

patch(Quiz.prototype, {
    xmlDependencies: [
        ...(Quiz.prototype.xmlDependencies || []),
        "/webside_slide_link/static/src/xml/website_full_quizz.xml",
    ],

    async willStart(...args) {
        const defs = [super.willStart(...args)];
        if (!this.quiz) {
            defs.push(this._fetchQuiz());
        }
        return Promise.all(defs);
    },
});
