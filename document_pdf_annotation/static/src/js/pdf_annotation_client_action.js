/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class PdfAnnotationClientAction extends Component {
    static template = "document_pdf_annotation.PdfAnnotationClientAction";

    setup() {
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            documentId: this.props.action.params.document_id,
            currentVersionId: this.props.action.params.version_id || null,
            currentVersionNumber: 0,
            versions: [],
            zoom: 1,
            selectedTool: "highlight",
            selectedColor: "#ffeb3b",
            fontSize: 14,
            historyActionType: "annotation_updated",
            annotationPayload: { items: [] },
        });

        this.canvasRef = useRef("annotationCanvas");

        onMounted(async () => {
            await this.loadContext();
        });

        onWillUnmount(() => {
            this.logAction("annotation_updated", { reason: "close_annotator" }).catch(() => {});
        });
    }

    async loadContext() {
        this.state.loading = true;
        const payload = await rpc("/document_pdf_annotation/load", {
            document_id: this.state.documentId,
            version_id: this.state.currentVersionId,
        });
        if (payload.error) {
            this.notification.add(payload.error, { type: "danger" });
            this.state.loading = false;
            return;
        }
        this.state.currentVersionId = payload.active_version_id;
        this.state.currentVersionNumber = payload.active_version_number;
        this.state.versions = payload.versions || [];
        this.state.annotationPayload = this.normalizeAnnotationPayload(payload.annotation_payload);

        const iframe = this.canvasRef.el;
        const fileSrc = payload.file_url || (payload.file_b64 ? `data:application/pdf;base64,${payload.file_b64}` : "about:blank");
        iframe.onload = null;
        iframe.onerror = null;
        iframe.src = fileSrc;
        iframe.onload = () => {
            this.state.loading = false;
        };
        iframe.onerror = () => {
            this.state.loading = false;
            this.notification.add("Unable to load PDF preview.", { type: "danger" });
        };
    }

    normalizeAnnotationPayload(rawPayload) {
        const normalizedPayload = rawPayload && typeof rawPayload === "object" && !Array.isArray(rawPayload)
            ? { ...rawPayload }
            : {};
        normalizedPayload.items = Array.isArray(normalizedPayload.items) ? normalizedPayload.items : [];
        return normalizedPayload;
    }

    selectTool(tool) {
        this.state.selectedTool = tool;
        this.logAction("annotation_updated", { tool });
    }

    async selectVersion(ev) {
        const versionId = parseInt(ev.target.value, 10);
        this.state.currentVersionId = Number.isNaN(versionId) ? null : versionId;
        await this.loadContext();
    }

    addSimpleAnnotation() {
        this.state.annotationPayload = this.normalizeAnnotationPayload(this.state.annotationPayload);
        const entry = {
            tool: this.state.selectedTool,
            color: this.state.selectedColor,
            font_size: this.state.fontSize,
            timestamp: new Date().toISOString(),
            user_note: `Applied ${this.state.selectedTool}`,
        };
        this.state.annotationPayload.items.push(entry);
        this.logAction("annotation_added", entry);
    }

    undo() {
        this.state.annotationPayload = this.normalizeAnnotationPayload(this.state.annotationPayload);
        if (this.state.annotationPayload.items.length) {
            const removed = this.state.annotationPayload.items.pop();
            this.logAction("annotation_deleted", removed);
        }
    }

    redo() {
        this.notification.add("Redo is UI-ready and should be wired with a full canvas implementation.", {
            type: "warning",
        });
    }

    zoomIn() {
        this.state.zoom = Math.min(this.state.zoom + 0.1, 3);
    }

    zoomOut() {
        this.state.zoom = Math.max(this.state.zoom - 0.1, 0.5);
    }

    async saveVersion() {
        const response = await rpc("/document_pdf_annotation/save", {
            document_id: this.state.documentId,
            annotation_payload: this.state.annotationPayload,
        });
        if (response.ok) {
            this.notification.add(`Saved as version v${response.version_number}`, { type: "success" });
            this.state.currentVersionId = response.version_id;
            await this.loadContext();
        }
    }

    async logAction(actionType, details = {}) {
        await rpc("/document_pdf_annotation/log_action", {
            document_id: this.state.documentId,
            action_type: actionType,
            version_id: this.state.currentVersionId,
            details,
        });
    }
}

registry.category("actions").add("document_pdf_annotation.client_action", PdfAnnotationClientAction);
