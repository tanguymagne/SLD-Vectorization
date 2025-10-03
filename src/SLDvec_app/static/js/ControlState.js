export class ControlState {
    constructor(state) {
        this.state = state;

        this.body = document.getElementsByTagName('body')[0];

        // Control fieldset
        this.visualizatonControlFieldset = document.getElementById('visualizaton-control-fieldset');
        this.algorithmControlFieldset = document.getElementById('algorithm-control-fieldset');
        this.imageProcessingControlFieldset = document.getElementById('image-processing-fieldset');
        this.medialAxisControlFieldset = document.getElementById('medial-axis-fieldset');


        // All the buttons and UX elements
        this.resetButton = document.getElementById('reset-button');
        this.sigmaRange = document.getElementById('scale-range');
        this.sigmaLabel = document.getElementById('scale-label');
        this.threshRange = document.getElementById('thresh-range');
        this.threshLabel = document.getElementById('thresh-label');
        this.automaticButton = document.getElementById('automatic-button');
        this.medialAxisButton = document.getElementById('medial-axis-button');
        this.mergeBranchButton = document.getElementById('merge-branch-button');
        this.splitNodeButton = document.getElementById('split-node-button');
        this.orderGraphButton = document.getElementById('order-graph-button');
        this.multipleLines = document.getElementById('multiple-lines');
        this.exportSVGButton = document.getElementById('export-button');
        this.radioBase = document.getElementById('show-base');
        this.radioBlur = document.getElementById('show-blur');
        this.radioBinary = document.getElementById('show-binary');

        // Visualization controls
        this.showImageCheckbox = document.getElementById('show-image');
        this.showSVGContourCheckbox = document.getElementById('show-svg-contour');
        this.showBaseGraphCheckbox = document.getElementById('show-base-graph');
        this.showGraphCheckbox = document.getElementById('show-graph');
        this.showVectorizationCheckbox = document.getElementById('show-vector');
        this.showIntersectionCheckbox = document.getElementById('show-intersection');
        this.repeatGradientRange = document.getElementById('repeat-range');
        this.repeatGradientLabel = document.getElementById('repeat-label');
    }

    checkImageCheckbox() {
        this.showImageCheckbox.checked = true;
        this.radioBase.disabled = false;
        this.radioBlur.disabled = false;
        this.radioBinary.disabled = false;
    }

    uncheckImageCheckbox() {
        this.showImageCheckbox.checked = false;
        this.radioBase.disabled = true;
        this.radioBlur.disabled = true;
        this.radioBinary.disabled = true;
    }

    waitingState() {
        this.visualizatonControlFieldset.disabled = true;
        this.algorithmControlFieldset.disabled = true;
        this.state.canvasState.loader.style.display = 'block';
        this.state.canvasState.interactionCanvas.classList.add('waiting');
    }

    readyState() {
        this.visualizatonControlFieldset.disabled = false;
        this.algorithmControlFieldset.disabled = false;
        this.state.canvasState.loader.style.display = 'none';
        this.state.canvasState.interactionCanvas.classList.remove('waiting');
    }

    // Reset all states to default
    initialize() {
        this.algorithmControlFieldset.disabled = true;
        this.uncheckImageCheckbox();
    }

    resetAll() {
        this.checkImageCheckbox();
        this.radioBase.checked = true;
        this.radioBlur.checked = false;
        this.radioBinary.checked = false;
        this.showSVGContourCheckbox.checked = false;
        this.showBaseGraphCheckbox.checked = false;
        this.showGraphCheckbox.checked = false;
        this.showIntersectionCheckbox.checked = false;
        this.showVectorizationCheckbox.checked = false;

        this.algorithmControlFieldset.disabled = false;
        this.imageProcessingControlFieldset.disabled = false;
        this.multipleLines.disabled = false;
        this.medialAxisControlFieldset.disabled = false;
        this.mergeBranchButton.disabled = true;
        this.splitNodeButton.disabled = true;
        this.orderGraphButton.disabled = true;
        this.exportSVGButton.disabled = true;

        this.sigmaRange.value = 0;
        this.sigmaLabel.textContent = `Scale: 0.0`;
        this.threshRange.value = 0;
        this.threshLabel.textContent = `Threshold: 0.0`;
    }
}
