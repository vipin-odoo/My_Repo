/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, onMounted, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class PdfAnnotatorAction extends Component {
    static template = "pdf_document_annotator.PdfAnnotatorAction";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        this.canvasRef = useRef("canvas");
        this.state = useState({
            documentId: this.props.action.context.active_id,
            attachmentUrl: "",
            activeTool: "draw",
            annotations: [],
            undoStack: [],
            drawing: false,
            startPoint: null,
        });

        onMounted(async () => {
            const [payload] = await this.orm.call(
                "documents.document",
                "get_pdf_annotation_payload",
                [[this.state.documentId]],
            );
            this.state.attachmentUrl = payload.attachment_url;
            this.state.annotations = this._parseExisting(payload.latest_annotation_json);
            this._resizeCanvas();
            this._redraw();
            window.addEventListener("resize", () => this._resizeCanvas());
        });
    }

    _parseExisting(raw) {
        if (!raw) {
            return [];
        }
        try {
            const payload = JSON.parse(raw);
            return payload.annotations || [];
        } catch {
            return [];
        }
    }

    _resizeCanvas() {
        const canvas = this.canvasRef.el;
        if (!canvas) {
            return;
        }
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
        this._redraw();
    }

    get ctx() {
        return this.canvasRef.el.getContext("2d");
    }

    setTool(tool) {
        this.state.activeTool = tool;
    }

    onPointerDown(ev) {
        this.state.drawing = true;
        const point = this._point(ev);
        this.state.startPoint = point;
        if (["draw", "highlight"].includes(this.state.activeTool)) {
            this.state.annotations.push({
                type: this.state.activeTool,
                points: [point],
            });
        }
    }

    onPointerMove(ev) {
        if (!this.state.drawing) {
            return;
        }

        const point = this._point(ev);
        const current = this.state.annotations[this.state.annotations.length - 1];
        if (current && ["draw", "highlight"].includes(current.type)) {
            current.points.push(point);
        }
        this._redraw(point);
    }

    onPointerUp(ev) {
        if (!this.state.drawing) {
            return;
        }
        this.state.drawing = false;
        const end = this._point(ev);
        const start = this.state.startPoint;
        const shapeTools = ["rectangle", "ellipse", "arrow", "text"];
        if (shapeTools.includes(this.state.activeTool)) {
            this.state.annotations.push({
                type: this.state.activeTool,
                start,
                end,
                text: this.state.activeTool === "text" ? "Note" : null,
            });
        }
        this.state.undoStack = [];
        this._redraw();
    }

    undo() {
        const last = this.state.annotations.pop();
        if (last) {
            this.state.undoStack.push(last);
            this._redraw();
        }
    }

    redo() {
        const last = this.state.undoStack.pop();
        if (last) {
            this.state.annotations.push(last);
            this._redraw();
        }
    }

    _point(ev) {
        const rect = this.canvasRef.el.getBoundingClientRect();
        return {
            x: ev.clientX - rect.left,
            y: ev.clientY - rect.top,
        };
    }

    _redraw() {
        const ctx = this.ctx;
        const canvas = this.canvasRef.el;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (const annotation of this.state.annotations) {
            this._drawAnnotation(ctx, annotation);
        }
    }

    _drawAnnotation(ctx, annotation) {
        ctx.save();
        ctx.strokeStyle = annotation.type === "highlight" ? "rgba(255, 235, 59, 0.7)" : "#ef4444";
        ctx.lineWidth = annotation.type === "highlight" ? 8 : 2;

        if (["draw", "highlight"].includes(annotation.type)) {
            ctx.beginPath();
            for (let i = 0; i < annotation.points.length; i++) {
                const p = annotation.points[i];
                if (i === 0) {
                    ctx.moveTo(p.x, p.y);
                } else {
                    ctx.lineTo(p.x, p.y);
                }
            }
            ctx.stroke();
        }

        if (["rectangle", "ellipse", "arrow", "text"].includes(annotation.type)) {
            const { start, end } = annotation;
            const w = end.x - start.x;
            const h = end.y - start.y;

            if (annotation.type === "rectangle") {
                ctx.strokeRect(start.x, start.y, w, h);
            } else if (annotation.type === "ellipse") {
                ctx.beginPath();
                ctx.ellipse(start.x + w / 2, start.y + h / 2, Math.abs(w / 2), Math.abs(h / 2), 0, 0, Math.PI * 2);
                ctx.stroke();
            } else if (annotation.type === "arrow") {
                ctx.beginPath();
                ctx.moveTo(start.x, start.y);
                ctx.lineTo(end.x, end.y);
                ctx.stroke();
            } else if (annotation.type === "text") {
                ctx.fillStyle = "#111827";
                ctx.font = "14px sans-serif";
                ctx.fillText(annotation.text || "Note", end.x, end.y);
            }
        }

        ctx.restore();
    }

    async save() {
        const payload = {
            annotations: this.state.annotations,
            saved_at: new Date().toISOString(),
        };
        const tools = [...new Set(this.state.annotations.map((a) => a.type))];
        await this.orm.call(
            "documents.document",
            "save_pdf_annotation",
            [[this.state.documentId], JSON.stringify(payload), "Saved from annotator", tools, false],
        );
        this.notification.add("PDF annotations saved as a new version.", { type: "success" });
        this.action.doAction({ type: "ir.actions.act_window_close" });
    }
}

registry.category("actions").add("pdf_document_annotator.annotator", PdfAnnotatorAction);
