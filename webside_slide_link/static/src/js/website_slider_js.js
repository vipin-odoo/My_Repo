/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { qweb } from "@web/core/qweb";
import FullscreenPlayer from "@website_slides/js/slides_course_fullscreen_player";

patch(FullscreenPlayer.prototype, {
    xmlDependencies: [
        ...(FullscreenPlayer.prototype.xmlDependencies || []),
        "/webside_slide_link/static/src/xml/website_full_screen_extend.xml",
    ],

    async _renderSlide(...args) {
        const def = await super._renderSlide(...args);
        const $content = this.$(".o_wslides_fs_content");

        if (this.get("slide").type === "certification") {
            $content.html(qweb.render("website.slides.fullscreen.certification.custom", { widget: this }));
        }

        const result = await this._rpc({
            model: "slide.slide",
            method: "get_linked_records_info",
            args: [this.get("slide").id],
        });

        if (result?.[0] === 1) {
            const iframe = document.createElement("iframe");
            iframe.setAttribute("title", "LINK");
            iframe.setAttribute("src", result[1]);
            iframe.setAttribute("width", "100%");
            $content.empty().append(iframe);
        }

        if (this.get("slide").type === "video") {
            const videoTag = $content[0]?.getElementsByTagName("iframe")[0];
            if (videoTag) {
                const sourceUrl = videoTag.src;
                videoTag.remove();
                const video = document.createElement("video");
                video.setAttribute("controls", "");
                video.setAttribute("autoplay", "");
                video.setAttribute("name", "media");
                video.setAttribute("controlsList", "nodownload");
                video.setAttribute("oncontextmenu", "return false;");
                video.setAttribute("width", "100%");
                video.setAttribute("height", "100%");

                const source = document.createElement("source");
                source.setAttribute("src", sourceUrl);
                source.setAttribute("type", "video/mp4");
                video.appendChild(source);

                $content.empty().append(video);
            }
        }

        return def;
    },
});
