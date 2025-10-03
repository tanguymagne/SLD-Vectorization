// ImageProcessor.js
export class ImagePreprocessor {
    constructor(appState) {
        this.appState = appState;
    }

    loadBaseImage(imgData) {
        this.appState.imageState.baseImage = new Image();
        this.appState.imageState.baseImage.src = 'data:image/png;base64,' + imgData;
        this.appState.imageState.displayedImage = this.appState.imageState.baseImage;
    }

    setDefaultView() {
        const { imageCanvas } = this.appState.canvasState;
        const { baseImage } = this.appState.imageState;

        const ratioHorizontal = imageCanvas.width / baseImage.naturalWidth;
        const ratioVertical = imageCanvas.height / baseImage.naturalHeight;

        if (ratioHorizontal < ratioVertical) {
            this.appState.viewState.defaultScale = ratioHorizontal;
            this.appState.viewState.defaultOffsetX = 0;
            this.appState.viewState.defaultOffsetY = (imageCanvas.height - baseImage.naturalHeight * this.appState.viewState.defaultScale) / 2;
        } else {
            this.appState.viewState.defaultScale = ratioVertical;
            this.appState.viewState.defaultOffsetX = (imageCanvas.width - baseImage.naturalWidth * this.appState.viewState.defaultScale) / 2;
            this.appState.viewState.defaultOffsetY = 0;
        }
    }


    updateParameters(sigma, thresh) {
        this.appState.imageState.sigma = sigma;
        this.appState.imageState.thresh = thresh;
    }

    async preprocessImage() {
        const response = await fetch('/preprocess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sigma: this.appState.imageState.sigma,
                thresh: this.appState.imageState.thresh
            })
        });

        const data = await response.json();
        this.updateImages(data);
        return data;
    }

    updateImages(data) {
        this.appState.imageState.blurImage = new Image();
        this.appState.imageState.blurImage.src = 'data:image/png;base64,' + data.blur_image;

        this.appState.imageState.binaryImage = new Image();
        this.appState.imageState.binaryImage.src = 'data:image/png;base64,' + data.binary_image;

        this.appState.imageState.thresh = data.thresh;
    }

    drawImage() {
        const { ctx } = this.appState.canvasState.contexts;
        const { displayedImage } = this.appState.imageState;

        if (displayedImage) {

            ctx.drawImage(
                displayedImage,
                0, 0,
                displayedImage.width,
                displayedImage.height
            );
        }
    }

    setImage(type) {
        switch (type) {
            case 'base':
                this.appState.imageState.displayedImage = this.appState.imageState.baseImage;
                break;
            case 'blur':
                this.appState.imageState.displayedImage = this.appState.imageState.blurImage;
                break;
            case 'binary':
                this.appState.imageState.displayedImage = this.appState.imageState.binaryImage;
                break;
        }
    }

}

// ImageControls.js
export class ImageControls {
    constructor(imageProcessor, controlState, onUpdate) {
        this.imageProcessor = imageProcessor;
        this.onUpdate = onUpdate;
        this.controlState = controlState;
        this.setupControls();
    }

    setupControls() {
        this.setupSigmaControl();
        this.setupThresholdControl();
        this.setupAutomaticButton();
        this.setupRadioButtons();
    }

    checkRadioButton(type) {
        switch (type) {
            case 'base':
                this.controlState.radioBase.checked = true;
                this.controlState.radioBlur.checked = false;
                this.controlState.radioBinary.checked = false;
                break;
            case 'blur':
                this.controlState.radioBase.checked = false;
                this.controlState.radioBlur.checked = true;
                this.controlState.radioBinary.checked = false;
                break;
            case 'binary':
                this.controlState.radioBase.checked = false;
                this.controlState.radioBlur.checked = false;
                this.controlState.radioBinary.checked = true;
                break;
        }
    }

    setupSigmaControl() {
        const { sigmaRange, sigmaLabel } = this.controlState;

        sigmaRange.addEventListener('input', async () => {
            const sigma = parseFloat(sigmaRange.value);
            sigmaLabel.textContent = `Scale: ${sigma.toFixed(1)}`;

            this.imageProcessor.updateParameters(sigma, this.imageProcessor.appState.imageState.thresh);
            await this.imageProcessor.preprocessImage();

            this.checkRadioButton("blur");
            this.imageProcessor.setImage('blur');
            this.onUpdate();
        });
    }

    setupThresholdControl() {
        const { threshRange, threshLabel } = this.controlState;

        threshRange.addEventListener('input', async () => {
            const thresh = parseFloat(threshRange.value);
            threshLabel.textContent = `Threshold: ${thresh.toFixed(2)}`;

            this.imageProcessor.updateParameters(this.imageProcessor.appState.imageState.sigma, thresh);
            await this.imageProcessor.preprocessImage();

            this.checkRadioButton("binary");
            this.imageProcessor.setImage('binary');
            this.onUpdate();
        });
    }

    setupAutomaticButton() {
        const { automaticButton, threshRange, threshLabel } = this.controlState;

        automaticButton.addEventListener('click', async () => {

            this.imageProcessor.updateParameters(
                this.imageProcessor.appState.imageState.sigma,
                2.0     // Special value to trigger automatic thresholding
            );
            const result = await this.imageProcessor.preprocessImage();

            threshRange.value = result.thresh;
            threshLabel.textContent = `Threshold: ${result.thresh.toFixed(2)}`;

            this.checkRadioButton("binary");
            this.imageProcessor.setImage('binary');
            this.onUpdate();
        });
    }

    setupRadioButtons() {
        const { radioBase, radioBlur, radioBinary } = this.controlState;

        radioBase.addEventListener('click', () => {
            this.imageProcessor.setImage('base');
            this.checkRadioButton("base");
            this.onUpdate();
        });

        radioBlur.addEventListener('click', () => {
            this.imageProcessor.setImage('blur');
            this.checkRadioButton("blur");
            this.onUpdate();
        });

        radioBinary.addEventListener('click', () => {
            this.imageProcessor.setImage('binary');
            this.checkRadioButton("binary");
            this.onUpdate();
        });
    }
}