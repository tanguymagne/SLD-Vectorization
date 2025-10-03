import { createProgram, curveVertexShaderSource, curveFragmentShaderSource } from './renderer/Shader.js';
import { CurveRenderer } from './renderer/CurveRenderer.js';

function fetchUpdateGraph(app, selectionType) {
    fetch('/update_graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nodes: Array.from(app.graphRenderer.isSelected),
            selectionType: selectionType,
        }),
    })
        .then(response => response.json())
        .then(data => {

            // Create the graph
            let { graph, numNodes, isSelected } = app.state.graphState;
            graph.nodes = [];
            graph.edges = [];
            for (let node of data.graph_data.nodes) {
                graph.nodes.push(node.x, node.y);
            }
            for (let edge of data.graph_data.edges) {
                const source = data.graph_data.nodes[edge.source];
                const target = data.graph_data.nodes[edge.target];
                graph.edges.push(source.x, source.y, target.x, target.y);
            }
            graph.branch_idx = data.graph_data.branch_idx;
            numNodes = graph.nodes.length / 2;
            app.state.graphState.numNodes = numNodes;
            console.log(
                `Loaded the graph with :  
                    ${graph.nodes.length / 2} nodes and 
                    ${graph.edges.length / 4} edges.
                `);

            isSelected = new Float32Array(numNodes).fill(0);
            app.graphRenderer.setGraph(graph, isSelected);
            app.draw();
        });
}

export class EventHandlers {
    constructor(app) {
        this.app = app;
        this.setupControlHandlers();
    }

    setupControlHandlers() {
        // Setup handlers for UI controls
        this.setupImageControls();
        this.setupGraphControls();
        this.setupVisualizationControls();
        this.setupVectorizationControls();
        this.setupExportControls();
    }

    setupVisualizationControls() {
        let { showGraphCheckbox, showBaseGraphCheckbox, showSVGContourCheckbox, showIntersectionCheckbox, showVectorizationCheckbox } = this.app.controlState;

        [showGraphCheckbox, showBaseGraphCheckbox, showSVGContourCheckbox, showIntersectionCheckbox, showVectorizationCheckbox].forEach(element => {
            element.addEventListener('change', () => {
                this.app.draw();
            });
        });

        this.app.controlState.resetButton.addEventListener('click', () => {
            this.app.state.resetView();
            this.app.draw();
        });

    }

    setupImageControls() {
        let { showImageCheckbox } = this.app.controlState;

        showImageCheckbox.addEventListener(
            'change',
            () => {
                if (showImageCheckbox.checked) {
                    this.app.controlState.checkImageCheckbox();
                }
                else {
                    this.app.controlState.uncheckImageCheckbox();
                }
                this.app.draw();
            }
        );
    }

    setupGraphControls() {
        // Setup graph-related control handlers
        const { medialAxisButton, mergeBranchButton, splitNodeButton } = this.app.controlState;

        medialAxisButton.addEventListener('click', () => {
            this.app.controlState.waitingState();

            fetch('/graph', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    state: this.app.controlState.multipleLines.checked,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    // Create the medial axis graph
                    let { graph, numNodes, isSelected } = this.app.state.graphState;

                    graph.nodes = [];
                    graph.edges = [];
                    for (let node of data.graph_data.nodes) {
                        graph.nodes.push(node.x, node.y);
                    }
                    for (let edge of data.graph_data.edges) {
                        const source = data.graph_data.nodes[edge.source];
                        const target = data.graph_data.nodes[edge.target];
                        graph.edges.push(source.x, source.y, target.x, target.y);
                    }
                    graph.branch_idx = data.graph_data.branch_idx;
                    numNodes = graph.nodes.length / 2;
                    this.app.state.graphState.numNodes = numNodes;
                    isSelected = new Float32Array(this.app.state.graphState.numNodes).fill(0);
                    this.app.graphRenderer.setGraph(graph, isSelected);

                    // Create the base graph
                    let { graphBase, numNodesBase, isSelectedBase } = this.app.state.graphState;

                    graphBase.nodes = [];
                    graphBase.edges = [];
                    for (let node of data.base_graph_data.nodes) {
                        graphBase.nodes.push(node.x, node.y);
                    }
                    for (let edge of data.base_graph_data.edges) {
                        const source = data.base_graph_data.nodes[edge.source];
                        const target = data.base_graph_data.nodes[edge.target];
                        graphBase.edges.push(source.x, source.y, target.x, target.y);
                    }
                    numNodesBase = graphBase.nodes.length / 2;
                    this.app.state.graphState.numNodesBase = numNodesBase;
                    graphBase.branch_idx = new Float32Array(numNodesBase).fill(0);
                    isSelectedBase = new Float32Array(numNodesBase).fill(0);
                    this.app.baseGraphRenderer.setGraph(graphBase, isSelectedBase)

                    // Get the bezier curves
                    this.app.state.graphState.curves = [];
                    let { curves } = this.app.state.graphState;
                    for (let curve of data.curves) {
                        curves.push(curve);
                    }

                    this.app.controlState.uncheckImageCheckbox();
                    this.app.controlState.showGraphCheckbox.checked = true;
                    this.app.controlState.showBaseGraphCheckbox.checked = false;
                    this.app.controlState.showSVGContourCheckbox.checked = true;
                    this.app.controlState.showIntersectionCheckbox.checked = false;
                    this.app.controlState.showVectorizationCheckbox.checked = false;
                    this.app.controlState.orderGraphButton.disabled = false;
                    this.app.state.resetIntersectionVectorizationState();

                    this.app.controlState.readyState();

                    this.app.draw();
                });
        });

        splitNodeButton.addEventListener('click', () => {
            fetchUpdateGraph(this.app, 'node');
            this.app.controlState.mergeBranchButton.disabled = true;
            this.app.controlState.splitNodeButton.disabled = true;
        });

        mergeBranchButton.addEventListener('click', () => {
            fetchUpdateGraph(this.app, 'branch');
            this.app.controlState.mergeBranchButton.disabled = true;
            this.app.controlState.splitNodeButton.disabled = true;
        });

    }

    setupVectorizationControls() {
        // Setup vectorization-related control handlers
        const { orderGraphButton, repeatGradientRange } = this.app.controlState;

        repeatGradientRange.addEventListener('input', () => {
            this.app.controlState.repeatGradientLabel.textContent = `Repeat gradient: ${parseFloat(repeatGradientRange.value).toFixed(1)}`;
            requestAnimationFrame(() => this.app.draw());
        });

        orderGraphButton.addEventListener('click', () => {
            this.app.controlState.waitingState();

            fetch('/vectorize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    state: this.app.controlState.multipleLines.checked,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    this.app.state.intersectionState.intersectionPoints = data.intersections_pos;

                    this.app.state.vectorizationState.pointsVectorize = data.vectorize_points;
                    this.app.state.vectorizationState.cDrawers = [];
                    for (let i = 0; i < this.app.state.vectorizationState.pointsVectorize.length; i++) {
                        const curveProgram = createProgram(this.app.state.canvasState.contexts.gl2, curveVertexShaderSource, curveFragmentShaderSource);
                        let ind = i / this.app.state.vectorizationState.pointsVectorize.length
                        this.app.state.vectorizationState.cDrawers.push(new CurveRenderer(
                            this.app.state.canvasState.contexts.gl2,
                            curveProgram,
                            this.app.state.vectorizationState.pointsVectorize[i], ind <= 0.7 ? ind : ind - 1,
                            this.app.state
                        ));
                    }
                })
                .then(() => {
                    this.app.controlState.showGraphCheckbox.checked = false;
                    this.app.controlState.showBaseGraphCheckbox.checked = false;
                    this.app.controlState.showVectorizationCheckbox.checked = true;
                    this.app.controlState.exportSVGButton.disabled = false;
                    this.app.controlState.readyState();
                    this.app.draw();
                })
        });
    }

    setupExportControls() {
        this.app.controlState.exportSVGButton.addEventListener('click', () => {

            fetch('/export_svg')
                .then(response => response.text())
                .then(content => {
                    const blob = new Blob([content], { type: 'image/svg+xml' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `${this.app.state.sampleName}.svg`;
                    a.click();
                    URL.revokeObjectURL(url);
                });
        });
    }

}