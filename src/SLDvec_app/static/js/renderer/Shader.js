import { color } from "../Colors.js";

export const pointSize = "5.0";

export function getPointVertexShaderSource(hoverable = false) {

    const v_isHovered = hoverable ? `v_isHovered` : "0.0";

    const pointVertexShaderSource = `
        attribute vec2 a_position;
        attribute float a_index;
        attribute float a_branchIndex;
        attribute float a_isSelected;
        uniform vec2 u_resolution;
        uniform vec2 u_translation;
        uniform float u_scale;
        uniform float u_pointSize;
        uniform vec2 u_mouse;
        uniform float u_hoveredIndex;
        uniform float u_hoveredBranchIndex;

        varying float v_isHovered;
        varying float v_isSelected;

        void main() {
            vec2 scaledPosition = a_position * u_scale;
            vec2 translatedPosition = scaledPosition + u_translation;
            vec2 clipSpace = (translatedPosition / u_resolution) * 2.0 - 1.0;
            gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);

            float distToMouse = distance(translatedPosition, u_mouse);
            v_isHovered = a_index == u_hoveredIndex ? 1.0 :0.0;
            // v_isHovered = a_branchIndex == u_hoveredBranchIndex ? 1.0 :0.0;
            v_isHovered = a_branchIndex == u_hoveredBranchIndex ? 1.0 : (a_index == u_hoveredIndex ? 1.0 : 0.0);
            v_isHovered = ${v_isHovered};
            v_isSelected = a_isSelected;

            gl_PointSize = u_pointSize * (1.0 + v_isHovered / 4.0);
        }
    `;
    return pointVertexShaderSource;
}


export function getPointFragmentShaderSource(c) {
    const selected = color.red;
    const pointFragmentShaderSource = `
        precision highp float;
        varying float v_isHovered;
        varying float v_isSelected;

        void main() {
            vec2 centerToPoint = 2.0 * gl_PointCoord - 1.0;
            float distance = length(centerToPoint);
            float alpha = 1.0 - smoothstep(0.95, 1.0, distance);
            alpha = 1.0 - step(1.0, distance);
            vec3 color;
            if (v_isSelected > 0.5) {
                color = vec3(${selected.r}, ${selected.g}, ${selected.b});
            } else {
                color = vec3(${c.r}, ${c.g}, ${c.b});  
            }
            if (v_isHovered > 0.5) {
                color = 1.2*color;
            }
            gl_FragColor = vec4(color, alpha);
        }
    `;
    return pointFragmentShaderSource;
}

export const edgeVertexShaderSource = `
    attribute vec2 a_position;
    uniform vec2 u_resolution;
    uniform vec2 u_translation;
    uniform float u_scale;

    void main() {
        vec2 scaledPosition = a_position * u_scale;
        vec2 translatedPosition = scaledPosition + u_translation;
        vec2 clipSpace = (translatedPosition / u_resolution) * 2.0 - 1.0;
        gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
    }
`;

export function getEdgeFragmentShaderSource(c) {
    const edgeFragmentShaderSource = `
        precision highp float;

        void main() {
            gl_FragColor = vec4(${c.r}, ${c.g}, ${c.b}, 1.0);
        }
    `;

    return edgeFragmentShaderSource;
}

export const curveVertexShaderSource = `
    attribute vec2 a_position;
    attribute float a_index;
    uniform vec2 u_resolution;
    uniform vec2 u_translation;
    uniform float u_scale;
    uniform float u_color_scale;
    uniform float u_curve_index;

    varying float v_index;
    varying float v_color_scale;
    varying float v_curve_index;

    void main() {
        vec2 scaledPosition = a_position * u_scale;
        vec2 translatedPosition = scaledPosition + u_translation;
        vec2 clipSpace = (translatedPosition / u_resolution) * 2.0 - 1.0;
        gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);

        v_index = a_index;
        v_color_scale = u_color_scale;
        v_curve_index = u_curve_index;
    }
`;

export const curveFragmentShaderSource = `
    precision highp float;

    varying float v_index;
    varying float v_color_scale;
    varying float v_curve_index;

    vec3 TurboColormap(in float x) {
        const vec4 kRedVec4 = vec4(0.13572138, 4.61539260, -42.66032258, 132.13108234);
        const vec4 kGreenVec4 = vec4(0.09140261, 2.19418839, 4.84296658, -14.18503333);
        const vec4 kBlueVec4 = vec4(0.10667330, 12.64194608, -60.58204836, 110.36276771);
        const vec2 kRedVec2 = vec2(-152.94239396, 59.28637943);
        const vec2 kGreenVec2 = vec2(4.27729857, 2.82956604);
        const vec2 kBlueVec2 = vec2(-89.90310912, 27.34824973);
    
        x = clamp(x, 0.0, 1.0);
        vec4 v4 = vec4( 1.0, x, x * x, x * x * x);
        vec2 v2 = v4.zw * v4.z;
        return vec3(
            dot(v4, kRedVec4)   + dot(v2, kRedVec2),
            dot(v4, kGreenVec4) + dot(v2, kGreenVec2),
            dot(v4, kBlueVec4)  + dot(v2, kBlueVec2)
        );
    }

    vec3 IllustratorColorMap(in float x) {
        const vec3 light_blue = vec3(  0. / 255., 168. / 255., 222. / 255.);
        const vec3 dark_blue  = vec3( 51. / 255.,  51. / 255., 145. / 255.);
        const vec3 pink       = vec3(233. / 255.,  19. / 255., 136. / 255.);
        const vec3 red        = vec3(235. / 255.,  45. / 255.,  46. / 255.);
        const vec3 yellow     = vec3(253. / 255., 233. / 255.,  43. / 255.);
        const vec3 green      = vec3(  0. / 255., 158. / 255.,  84. / 255.);

        if (x < 0.2) {
            return mix(green, yellow, x / 0.2);
        }   
        if (x < 0.4) {
            return mix(yellow, red, (x - 0.2) / 0.2);
        }
        if (x < 0.6) {
            return mix(red, pink, (x - 0.4) / 0.2);
        }
        if (x < 0.8) {
            return mix(pink, dark_blue, (x - 0.6) / 0.2);
        }
        return mix(dark_blue, light_blue, (x - 0.8) / 0.2);

        // Reverse order
        // if (x < 0.2) {
        //     return mix(light_blue, dark_blue, x / 0.2);
        // }   
        // if (x < 0.4) {
        //     return mix(dark_blue, pink, (x - 0.2) / 0.2);
        // }
        // if (x < 0.6) {
        //     return mix(pink, red, (x - 0.4) / 0.2);
        // }
        // if (x < 0.8) {
        //     return mix(red, yellow, (x - 0.6) / 0.2);
        // }
        // return mix(yellow, green, (x - 0.8) / 0.2);
    
    }

    void main() {
        float value = abs(
            mod(
                v_color_scale * v_index + (1.3 + v_curve_index) * smoothstep(1.0, 0.0, v_color_scale),
                2.0
            ) - 1.0
        );
        // vec3 color = TurboColormap(value);
        vec3 color = IllustratorColorMap(value);
        gl_FragColor = vec4(color, 1.0);
    }
`;

function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('An error occurred compiling the shaders: ' + gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

export function createProgram(gl, vertexShaderSource, fragmentShaderSource) {
    const program = gl.createProgram();
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Unable to initialize the shader program: ' + gl.getProgramInfoLog(program));
        return null;
    }
    return program;
}