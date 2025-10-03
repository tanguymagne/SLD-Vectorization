export class GraphRenderer {
    constructor(gl, vertexProgram, edgeProgram, state) {
        this.gl = gl;
        this.vertexProgram = vertexProgram;
        this.edgeProgram = edgeProgram;
        this.state = state;
        this.createBuffers();
        this.setLocations();
    }

    setGraph(graph, isSelected) {
        this.graph = graph;
        this.isSelected = isSelected;
        this.bindBuffers();
    }


    createBuffers() {
        this.vertexBuffer = this.gl.createBuffer();
        this.indexBuffer = this.gl.createBuffer();
        this.branchIndexBuffer = this.gl.createBuffer();
        this.edgeBuffer = this.gl.createBuffer();
        this.isSelectedBuffer = this.gl.createBuffer();
    }

    setLocations() {
        this.vertexPositionAttributeLocation = this.gl.getAttribLocation(this.vertexProgram, "a_position");
        this.vertexIndexAttributeLocation = this.gl.getAttribLocation(this.vertexProgram, "a_index");
        this.branchIndexAttributeLocation = this.gl.getAttribLocation(this.vertexProgram, "a_branchIndex");
        this.isSelectedAttributeLocation = this.gl.getAttribLocation(this.vertexProgram, "a_isSelected");
        this.vertexResolutionUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_resolution");
        this.vertexTranslationUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_translation");
        this.vertexScaleUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_scale");
        this.vertexSizeUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_pointSize");
        this.mouseUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_mouse");
        this.hoveredIndexUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_hoveredIndex");
        this.hoveredBranchIndexUniformLocation = this.gl.getUniformLocation(this.vertexProgram, "u_hoveredBranchIndex");

        this.edgePositionAttributeLocation = this.gl.getAttribLocation(this.edgeProgram, "a_position");
        this.edgeResolutionUniformLocation = this.gl.getUniformLocation(this.edgeProgram, "u_resolution");
        this.edgeTranslationUniformLocation = this.gl.getUniformLocation(this.edgeProgram, "u_translation");
        this.edgeScaleUniformLocation = this.gl.getUniformLocation(this.edgeProgram, "u_scale");
    }

    bindBuffers() {
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.vertexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(this.graph.nodes), this.gl.STATIC_DRAW);

        const indices = new Float32Array(this.graph.nodes.length / 2);
        for (let i = 0; i < indices.length; i++) {
            indices[i] = i;
        }
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.indexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, indices, this.gl.STATIC_DRAW);

        const indicesBranch = new Float32Array(this.graph.nodes.length / 2);
        for (let i = 0; i < this.graph.branch_idx.length; i++) {
            indicesBranch[i] = this.graph.branch_idx[i];
        }
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.branchIndexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, indicesBranch, this.gl.STATIC_DRAW);

        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.edgeBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(this.graph.edges), this.gl.STATIC_DRAW);

        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.isSelectedBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, this.isSelected, this.gl.DYNAMIC_DRAW);
    }

    draw(vertexSize, numNodes) {
        const { offsetX, offsetY, scale, mouseX, mouseY, hoveredNode } = this.state.viewState;

        // Draw edges
        this.gl.useProgram(this.edgeProgram);
        this.gl.enableVertexAttribArray(this.edgePositionAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.edgeBuffer);
        this.gl.vertexAttribPointer(this.edgePositionAttributeLocation, 2, this.gl.FLOAT, false, 0, 0);

        this.gl.uniform2f(this.edgeResolutionUniformLocation, this.gl.canvas.width, this.gl.canvas.height);
        this.gl.uniform2f(this.edgeTranslationUniformLocation, offsetX, offsetY);
        this.gl.uniform1f(this.edgeScaleUniformLocation, scale);

        this.gl.enable(this.gl.BLEND);
        this.gl.blendFunc(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA);
        // this.gl.enable(this.gl.LINE_SMOOTH);
        this.gl.lineWidth(2);  // Adjust this value for desired edge thickness

        this.gl.drawArrays(this.gl.LINES, 0, this.graph.edges.length / 2);

        // Draw vertex
        this.gl.useProgram(this.vertexProgram);

        this.gl.enableVertexAttribArray(this.vertexPositionAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.vertexBuffer);
        this.gl.vertexAttribPointer(this.vertexPositionAttributeLocation, 2, this.gl.FLOAT, false, 0, 0);

        this.gl.enableVertexAttribArray(this.vertexIndexAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.indexBuffer);
        this.gl.vertexAttribPointer(this.vertexIndexAttributeLocation, 1, this.gl.FLOAT, false, 0, 0);

        this.gl.enableVertexAttribArray(this.branchIndexAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.branchIndexBuffer);
        this.gl.vertexAttribPointer(this.branchIndexAttributeLocation, 1, this.gl.FLOAT, false, 0, 0);

        this.gl.enableVertexAttribArray(this.isSelectedAttributeLocation);
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.isSelectedBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, this.isSelected, this.gl.DYNAMIC_DRAW);
        this.gl.vertexAttribPointer(this.isSelectedAttributeLocation, 1, this.gl.FLOAT, false, 0, 0);

        this.gl.uniform2f(this.vertexResolutionUniformLocation, this.gl.canvas.width, this.gl.canvas.height);
        this.gl.uniform2f(this.vertexTranslationUniformLocation, offsetX, offsetY);
        this.gl.uniform1f(this.vertexScaleUniformLocation, scale);
        this.gl.uniform1f(this.vertexSizeUniformLocation, vertexSize * 2);  // Base vertex size
        this.gl.uniform2f(this.mouseUniformLocation, mouseX, mouseY);
        this.gl.uniform1f(this.hoveredIndexUniformLocation, hoveredNode);

        this.gl.uniform1f(this.hoveredBranchIndexUniformLocation, hoveredNode > -1 ?
            (this.graph.branch_idx[hoveredNode] == -1 ?
                -2 : this.graph.branch_idx[hoveredNode]) : -2);

        this.gl.enable(this.gl.BLEND);
        this.gl.blendFunc(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA);

        this.gl.drawArrays(this.gl.POINTS, 0, numNodes);
    }
}