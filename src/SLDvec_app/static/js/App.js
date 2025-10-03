// App.js
import { appState } from './State.js';
import { ControlState } from './ControlState.js';
import { ImageControls, ImagePreprocessor } from './Image.js';
import { CanvasInteraction } from './CanvasInteraction.js';
import { EventHandlers } from './EventHandler.js';
import { color, toString, lowerIntensity } from './Colors.js';
import { GraphRenderer } from './renderer/GraphRenderer.js';
import {
    pointSize,
    getPointVertexShaderSource,
    getPointFragmentShaderSource,
    edgeVertexShaderSource,
    getEdgeFragmentShaderSource,
    createProgram
} from './renderer/Shader.js';

class App {
    constructor() {
        this.state = appState;
        this.controlState = new ControlState(this.state);
        this.initializeCanvases();
        this.controlState.initialize();
        this.initializeImage();
        this.initializeInteraction();
        this.initializeRenderers();
        // this.initializeEventListeners();
    }

    initializeCanvases() {
        // Initialize all canvases and their contexts
        const canvases = {
            imageCanvas: document.getElementById('image-canvas'),
            graphCanvas: document.getElementById('graph-canvas'),
            vectorCanvas: document.getElementById('vector-canvas'),
            intersectionCanvas: document.getElementById('intersection-canvas'),
            interactionCanvas: document.getElementById('interaction-canvas'),
            canvasOverlay: document.getElementById('canvas-overlay'),
            loader: document.getElementById('loader')
        };

        // Store canvas references and initialize contexts
        Object.assign(this.state.canvasState, canvases);
        this.state.canvasState.contexts = {
            ctx: canvases.imageCanvas.getContext('2d'),
            gl: canvases.graphCanvas.getContext('webgl', { antialias: true }),
            gl2: canvases.vectorCanvas.getContext('webgl', { antialias: true }),
            ctx2: canvases.intersectionCanvas.getContext('2d')
        };
    }

    initializeImage() {
        this.imagePreprocessor = new ImagePreprocessor(this.state);
        this.imageControls = new ImageControls(this.imagePreprocessor, this.controlState, () => this.draw());
    }

    initializeRenderers() {
        const { gl } = this.state.canvasState.contexts;
        const pointProgram = createProgram(gl, getPointVertexShaderSource(true), getPointFragmentShaderSource(color.green));
        const edgeProgram = createProgram(gl, edgeVertexShaderSource, getEdgeFragmentShaderSource(lowerIntensity(color.green, 1.2)));
        const pointProgramBase = createProgram(gl, getPointVertexShaderSource(false), getPointFragmentShaderSource(color.yellow));
        const edgeProgramBase = createProgram(gl, edgeVertexShaderSource, getEdgeFragmentShaderSource(lowerIntensity(color.yellow, 1.2)));

        this.graphRenderer = new GraphRenderer(gl, pointProgram, edgeProgram, this.state);
        this.baseGraphRenderer = new GraphRenderer(gl, pointProgramBase, edgeProgramBase, this.state);
    }

    initializeInteraction() {
        this.canvasInteraction = new CanvasInteraction(this);
        this.EventHandlers = new EventHandlers(this);
    }


    draw() {
        // Clear all canvases
        this.clearCanvases();

        // Draw image if enabled
        if (this.controlState.showImageCheckbox.checked) {
            this.imagePreprocessor.drawImage();
        }

        if (this.controlState.showSVGContourCheckbox.checked) {
            const { curves } = this.state.graphState;
            const { ctx } = this.state.canvasState.contexts;
            for (let j = 0; j < curves.length; j++) {
                let curve = curves[j];
                ctx.beginPath();
                ctx.moveTo(curve[0][0][0], curve[0][0][1]);
                for (let i = 0; i < curve.length; i++) {
                    ctx.bezierCurveTo(
                        curve[i][1][0], curve[i][1][1],
                        curve[i][2][0], curve[i][2][1],
                        curve[i][3][0], curve[i][3][1]
                    );
                }
                ctx.strokeStyle = toString(color.red);
                ctx.lineWidth = 0.2;
                ctx.stroke();
            }
        }

        // Draw baseGraph elements if enabled
        if (this.controlState.showBaseGraphCheckbox.checked) {
            this.baseGraphRenderer.draw(pointSize, this.state.graphState.numNodesBase);
        }

        // Draw graph elements if enabled
        if (this.controlState.showGraphCheckbox.checked) {
            this.graphRenderer.draw(pointSize, this.state.graphState.numNodes);
        }

        // Draw curves if enabled
        if (this.controlState.showVectorizationCheckbox.checked) {
            for (const cDrawer of this.state.vectorizationState.cDrawers) {
                cDrawer.draw(
                    parseFloat(this.controlState.repeatGradientRange.value),
                );
            }
        }

        // Draw intersections if enabled
        if (this.controlState.showIntersectionCheckbox.checked) {
            const { ctx2 } = this.state.canvasState.contexts;
            const { intersectionState } = this.state;

            for (let i = 0; i < intersectionState.intersectionPoints.length; i++) {
                // Draw a circle 
                ctx2.beginPath();
                ctx2.arc(intersectionState.intersectionPoints[i][0], intersectionState.intersectionPoints[i][1], 4, 0, 2 * Math.PI);
                if (i == intersectionState.hoveredPoint) {
                    ctx2.fillStyle = toString(color.black, 0.2);
                    ctx2.fill();
                }
                if (i == intersectionState.selected) {
                    ctx2.fillStyle = toString(color.black, 0.5);
                    ctx2.fill();
                }
                ctx2.strokeStyle = "black";
                ctx2.lineWidth = 0.5;
                ctx2.stroke();
            }
        }

        // Restore context
        const { ctx, ctx2 } = this.state.canvasState.contexts;
        ctx.restore();
        ctx2.restore();
    }

    clearCanvases() {
        const { ctx, gl, gl2, ctx2 } = this.state.canvasState.contexts;
        const { imageCanvas, graphCanvas } = this.state.canvasState;

        ctx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
        ctx.imageSmoothingEnabled = false;
        ctx.save();
        ctx.translate(this.state.viewState.offsetX, this.state.viewState.offsetY);
        ctx.scale(this.state.viewState.scale, this.state.viewState.scale);

        ctx2.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
        ctx2.imageSmoothingEnabled = false;
        ctx2.save();
        ctx2.translate(this.state.viewState.offsetX, this.state.viewState.offsetY);
        ctx2.scale(this.state.viewState.scale, this.state.viewState.scale);


        gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl2.viewport(0, 0, gl2.canvas.width, gl2.canvas.height);
        gl2.clear(gl2.COLOR_BUFFER_BIT);
    }
}

// Initialize the application
const app = new App();
window.addEventListener("resize", () => {
    app.draw();
});