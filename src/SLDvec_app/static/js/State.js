class ApplicationState {
    constructor() {
        this.sampleName = null;

        // Canvas states
        this.canvasState = {
            imageCanvas: null,
            graphCanvas: null,
            vectorCanvas: null,
            intersectionCanvas: null,
            interactionCanvas: null,
            canvasOverlay: null,
            loader: null,
            contexts: {
                ctx: null,
                gl: null,
                gl2: null,
                ctx2: null
            }
        };

        // View state for pan/zoom
        this.viewState = {
            defaultScale: 1,
            defaultOffsetX: 0,
            defaultOffsetY: 0,
            scale: 1,
            offsetX: 0,
            offsetY: 0,
            isDragging: false,
            lastX: 0,
            lastY: 0,
            mouseX: 0,
            mouseY: 0,
            hoveredNode: -1
        };

        // Image processing state
        this.imageState = {
            displayedImage: null,
            baseImage: null,
            blurImage: null,
            binaryImage: null,
            thresh: 0.0,
            sigma: 0.0
        };

        // Graph state
        this.graphState = {
            curves: [],
            curveColor: null,
            numNodes: 0,
            graph: { nodes: [], edges: [], branch_idx: [] },
            isSelected: null,
            numNodesBase: 0,
            graphBase: { nodes: [], edges: [], branch_idx: [] },
            isSelectedBase: null
        };

        // Intersection state
        this.intersectionState = {
            intersectionPoints: [],
            hoveredPoint: -1,
            selected: -1
        };

        // Vectorization state
        this.vectorizationState = {
            pointsVectorize: [],
            cDrawers: []
        };

        // UI Controls state
        this.controlState = {
            showImage: true,
            showSVGContour: false,
            showBaseGraph: false,
            showGraph: false,
            showIntersection: false,
            showVectorization: false
        };

    }

    // Reset all states to default
    resetAll() {
        this.graphState.curves = [];
        this.graphState.numNodes = 0;
        this.graphState.graph = { nodes: [], edges: [], branch_idx: [] };
        this.graphState.isSelected = new Float32Array(this.graphState.numNodes).fill(0);
        this.graphState.numNodesBase = 0;
        this.graphState.graphBase = { nodes: [], edges: [], branch_idx: [] };
        this.graphState.isSelectedBase = new Float32Array(this.graphState.numNodesBase).fill(0);

        this.intersectionState.intersectionPoints = [];
        this.intersectionState.hoveredPoint = -1;
        this.intersectionState.selected = -1;

        this.vectorizationState.pointsVectorize = [];
        this.vectorizationState.cDrawers = [];

        this.canvasState.canvasOverlay.style.display = 'none';
    }

    resetView() {
        this.viewState.scale = this.viewState.defaultScale;
        this.viewState.offsetX = this.viewState.defaultOffsetX;
        this.viewState.offsetY = this.viewState.defaultOffsetY;
    }

    resetIntersectionVectorizationState() {
        this.intersectionState.intersectionPoints = [];
        this.intersectionState.hoveredPoint = -1;
        this.intersectionState.selected = -1;

        this.vectorizationState.pointsVectorize = [];
        this.vectorizationState.cDrawers = [];
    }

    // Update view state
    updateViewState(updates) {
        Object.assign(this.viewState, updates);
    }

    // Update control state
    updateControlState(updates) {
        Object.assign(this.controlState, updates);
    }
}

export const appState = new ApplicationState();