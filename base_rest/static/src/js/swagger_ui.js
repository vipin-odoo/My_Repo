/** @odoo-module **/

/* global SwaggerUIBundle, SwaggerUIStandalonePreset */

export class SwaggerUI {
    constructor(selector) {
        this.selector = selector;
        this.el = document.querySelector(selector);
    }

    _swaggerBundleSettings() {
        const defaults = {
            dom_id: this.selector,
            deepLinking: true,
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
            plugins: [SwaggerUIBundle.plugins.DownloadUrl],
            layout: "StandaloneLayout",
            operationsSorter(a, b) {
                const methodsOrder = ["get", "post", "put", "delete", "patch", "options", "trace"];
                let result = methodsOrder.indexOf(a.get("method")) - methodsOrder.indexOf(b.get("method"));
                if (result === 0) {
                    result = a.get("path").localeCompare(b.get("path"));
                }
                return result;
            },
            tagsSorter: "alpha",
            onComplete() {
                if (!this.web_btn) {
                    this.web_btn = $("<a class='fa fa-th swg-odoo-web-btn' href='/web' accesskey='h'></a>");
                    $(".topbar").prepend(this.web_btn);
                }
            },
        };
        const config = this.el?.dataset?.settings ? JSON.parse(this.el.dataset.settings) : {};
        return Object.assign({}, defaults, config);
    }

    start() {
        if (!this.el) {
            return;
        }
        this.ui = SwaggerUIBundle(this._swaggerBundleSettings());
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const swagger = new SwaggerUI("#swagger-ui");
    swagger.start();
});
