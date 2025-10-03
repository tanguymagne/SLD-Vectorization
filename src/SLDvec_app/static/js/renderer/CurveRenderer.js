export class CurveRenderer {

    constructor(gl, program, points, curve_index, state) {
        this.gl = gl;
        this.program = program;
        this.pos = points;
        this.curve_index = curve_index;
        this.state = state;

        this.setLocations();
        this.createBuffers();
        this.bindBuffers();
    }
    setLocations() {
        this.posAttributeLocation = this.gl.getAttribLocation(this.program, "a_position");
        this.indexAttributeLocation = this.gl.getAttribLocation(this.program, "a_index");

        // Screen display related uniforms
        this.resolutionUniformLocation = this.gl.getUniformLocation(this.program, "u_resolution");
        this.translationUniformLocation = this.gl.getUniformLocation(this.program, "u_translation");
        this.scaleUniformLocation = this.gl.getUniformLocation(this.program, "u_scale");
        this.colorScaleUniformLocation = this.gl.getUniformLocation(this.program, "u_color_scale");
        this.curveIndexUniformLocation = this.gl.getUniformLocation(this.program, "u_curve_index");
    }

    createBuffers() {
        this.posBuffer = this.gl.createBuffer();
        this.indexBuffer = this.gl.createBuffer();
    }

    bindBuffers() {
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.posBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(this.pos), this.gl.STATIC_DRAW);

        const indices = new Float32Array(this.pos.length / 2);
        for (let i = 0; i < indices.length; i++) {
            indices[i] = i / (indices.length - 1);
        }
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.indexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, indices, this.gl.STATIC_DRAW);
    }

    draw(colorScale) {
        const { offsetX, offsetY, scale } = this.state.viewState;

        // Draw edges
        this.gl.useProgram(this.program);

        this.gl.enableVertexAttribArray(this.posAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.posBuffer);
        this.gl.vertexAttribPointer(this.posAttributeLocation, 2, this.gl.FLOAT, false, 0, 0);

        this.gl.enableVertexAttribArray(this.indexAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.indexBuffer);
        this.gl.vertexAttribPointer(this.indexAttributeLocation, 1, this.gl.FLOAT, false, 0, 0);

        this.gl.uniform2f(this.resolutionUniformLocation, this.gl.canvas.width, this.gl.canvas.height);
        this.gl.uniform2f(this.translationUniformLocation, offsetX, offsetY);
        this.gl.uniform1f(this.scaleUniformLocation, scale);
        this.gl.uniform1f(this.colorScaleUniformLocation, colorScale);
        this.gl.uniform1f(this.curveIndexUniformLocation, this.curve_index);

        this.gl.enable(this.gl.BLEND);
        this.gl.blendFunc(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA);

        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, this.pos.length / 2);
    }
}