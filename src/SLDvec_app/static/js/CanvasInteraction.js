import { pointSize, curveFragmentShaderSource, curveVertexShaderSource, createProgram } from "./renderer/Shader.js";
import { CurveRenderer } from "./renderer/CurveRenderer.js";

// CanvasInteraction.js
export class CanvasInteraction {
    constructor(app) {
        this.app = app;
        this.canvas = this.app.state.canvasState.interactionCanvas;
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.setupZoom();
        this.setupPan();
        this.setupDragDrop();
        this.setupHover();
        this.setupClick();
    }

    setupZoom() {
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomIntensity = 0.1;
            const wheel = e.deltaY < 0 ? 1 : -1;
            const zoom = Math.exp(wheel * zoomIntensity);

            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            this.app.state.viewState.offsetX = mouseX - (mouseX - this.app.state.viewState.offsetX) * zoom;
            this.app.state.viewState.offsetY = mouseY - (mouseY - this.app.state.viewState.offsetY) * zoom;
            this.app.state.viewState.scale *= zoom;

            this.app.draw();
        });
    }

    setupPan() {
        this.canvas.addEventListener('mousedown', (e) => {
            this.app.state.viewState.isDragging = true;
            this.app.state.viewState.lastX = e.clientX;
            this.app.state.viewState.lastY = e.clientY;
        });

        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.app.state.viewState.mouseX = e.clientX - rect.left;
            this.app.state.viewState.mouseY = e.clientY - rect.top;

            if (this.app.state.viewState.isDragging) {
                this.app.state.viewState.offsetX += e.clientX - this.app.state.viewState.lastX;
                this.app.state.viewState.offsetY += e.clientY - this.app.state.viewState.lastY;
                this.app.state.viewState.lastX = e.clientX;
                this.app.state.viewState.lastY = e.clientY;
            }

            requestAnimationFrame(() => { this.app.draw(); });
        });

        this.canvas.addEventListener('mouseup', () => {
            this.app.state.viewState.isDragging = false;
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.app.state.viewState.isDragging = false;
        });
    }

    setupDragDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.canvas.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.canvas.addEventListener(
                eventName,
                (e) => { this.canvas.classList.add('dragover'); },
                false
            );
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.canvas.addEventListener(
                eventName,
                (e) => { this.canvas.classList.remove('dragover'); },
                false
            );
        });

        this.canvas.addEventListener('drop', this.imageDrop.bind(this), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    imageDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;

        if (files.length > 1) {
            alert('Please drop only one file');
            return;
        }
        const file = files[0];
        this.app.state.sampleName = file.name.replace(/\.[^/.]+$/, "");


        if (file) {
            if (file.type.startsWith('image/png') || file.type.startsWith('image/jpeg')) {

                const formData = new FormData();
                formData.append('file', file);
                fetch('/upload_image', {
                    method: 'POST',
                    body: formData,
                })
                    .then(response => response.json())
                    .then((data) => {
                        this.app.imagePreprocessor.loadBaseImage(data)
                    })
                    .then(() => {
                        this.app.imagePreprocessor.setDefaultView();
                        this.app.imagePreprocessor.appState.resetView();
                        this.app.imagePreprocessor.appState.resetAll();
                        this.app.controlState.resetAll();
                        this.app.controlState.automaticButton.click();
                        this.app.draw();
                    });
            }
            else {
                alert('Please drop a valid image file\nOnly PNG or JPG are supported');
                return;
            }

        }
    }

    setupHover() {

        this.canvas.addEventListener('mouseleave', () => {
            this.app.state.viewState.hoveredNode = -1;
            this.app.draw();
        });

        this.canvas.addEventListener('mousemove', (e) => {

            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            let dist;
            let minDist;

            // Hover interection for graph nodes
            this.app.state.viewState.hoveredNode = -1;
            if (this.app.controlState.showGraphCheckbox.checked) {

                const mouse_x = (mouseX - this.app.state.viewState.offsetX) / this.app.state.viewState.scale;
                const mouse_y = (mouseY - this.app.state.viewState.offsetY) / this.app.state.viewState.scale;

                minDist = (pointSize / this.app.state.viewState.scale) + 1;
                for (let i = 0; i < this.app.state.graphState.numNodes; i++) {
                    const dx = this.app.state.graphState.graph.nodes[i * 2] - mouse_x;
                    const dy = this.app.state.graphState.graph.nodes[i * 2 + 1] - mouse_y;
                    dist = dx * dx + dy * dy;
                    if (dist < (10 / this.app.state.viewState.scale) ** 2 && dist < minDist) {
                        minDist = dx * dx + dy * dy;
                        this.app.state.viewState.hoveredNode = i;
                    }
                }
            }

            // Hover intersection points
            this.app.state.intersectionState.hoveredPoint = -1;
            if (this.app.controlState.showIntersectionCheckbox.checked) {

                const mouse_x = (mouseX - this.app.state.viewState.offsetX) / this.app.state.viewState.scale;
                const mouse_y = (mouseY - this.app.state.viewState.offsetY) / this.app.state.viewState.scale;

                minDist = 16;
                const { intersectionState } = this.app.state;
                for (let i = 0; i < intersectionState.intersectionPoints.length; i++) {
                    const dx = intersectionState.intersectionPoints[i][0] - mouse_x;
                    const dy = intersectionState.intersectionPoints[i][1] - mouse_y;
                    dist = dx * dx + dy * dy;
                    if (dist < minDist) {
                        minDist = dist;
                        intersectionState.hoveredPoint = i;
                    }

                }
            }

            requestAnimationFrame(() => { this.app.draw(); });
        });
    }

    setupClick() {
        this.canvas.addEventListener('click', () => {

            // Select graph nodes
            if (this.app.state.viewState.hoveredNode >= 0) {
                let selectedBranchIdx = this.app.state.graphState.graph.branch_idx[this.app.state.viewState.hoveredNode];

                if (selectedBranchIdx != -1) {
                    let someNodeSelected = false;
                    for (let i = 0; i < this.app.state.graphState.graph.nodes.length / 2; i++) {
                        if (this.app.state.graphState.graph.branch_idx[i] == selectedBranchIdx || this.app.graphRenderer.isSelected[i] == 1) {
                            this.app.graphRenderer.isSelected[i] = 1 - this.app.graphRenderer.isSelected[i];
                            if (this.app.graphRenderer.isSelected[i] == 1) {
                                someNodeSelected = true;
                            }
                        }
                    }
                    if (someNodeSelected) {
                        this.app.controlState.mergeBranchButton.disabled = false;
                        this.app.controlState.splitNodeButton.disabled = true;
                    }
                    else {
                        this.app.controlState.mergeBranchButton.disabled = true;
                        this.app.controlState.splitNodeButton.disabled = true;
                    }
                }

                else {
                    for (let i = 0; i < this.app.state.graphState.graph.nodes.length / 2; i++) {
                        if (this.app.graphRenderer.isSelected[i] == 1 && i != this.app.state.viewState.hoveredNode) {
                            this.app.graphRenderer.isSelected[i] = 1 - this.app.graphRenderer.isSelected[i];
                        }
                    }
                    this.app.graphRenderer.isSelected[this.app.state.viewState.hoveredNode] = 1 - this.app.graphRenderer.isSelected[this.app.state.viewState.hoveredNode];

                    if (this.app.graphRenderer.isSelected[this.app.state.viewState.hoveredNode] == 1) {
                        this.app.controlState.mergeBranchButton.disabled = true;
                        this.app.controlState.splitNodeButton.disabled = false;
                    }
                    else {
                        this.app.controlState.mergeBranchButton.disabled = true;
                        this.app.controlState.splitNodeButton.disabled = true;
                    }

                }
            }

            // Change intersection type
            const { intersectionState } = this.app.state;
            if (intersectionState.hoveredPoint >= 0) {
                this.app.controlState.body.style.cursor = "wait";
                intersectionState.selected = intersectionState.hoveredPoint;
                this.update_vectorize();
            }

            this.app.draw()
        });
    }

    update_vectorize() {
        const { intersectionState, vectorizationState } = this.app.state;
        fetch('/update_vectorize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                intersection: intersectionState.selected,
            }),
        })
            .then(response => response.json())
            .then(data => {
                intersectionState.intersectionPoints = data.intersections_pos;

                vectorizationState.pointsVectorize = data.vectorize_points;
                vectorizationState.cDrawers = [];
                for (let i = 0; i < vectorizationState.pointsVectorize.length; i++) {
                    const curveProgram = createProgram(this.app.state.canvasState.contexts.gl2, curveVertexShaderSource, curveFragmentShaderSource);
                    let ind = i / vectorizationState.pointsVectorize.length
                    vectorizationState.cDrawers.push(new CurveRenderer(
                        this.app.state.canvasState.contexts.gl2,
                        curveProgram,
                        vectorizationState.pointsVectorize[i],
                        ind <= 0.7 ? ind : ind - 1,
                        this.app.state
                    ));
                }

                intersectionState.selected = -1;
            })
            .then(() => {
                this.app.draw();
                this.app.controlState.body.style.cursor = "default";
            });
    }
}