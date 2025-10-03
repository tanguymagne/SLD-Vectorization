export const color = {
    purple: hexToRgb('#903498'),
    darkBlue: hexToRgb('#4040a0'),
    blue: hexToRgb('#1f64ad'),
    turquoise: hexToRgb('#0095ac'),
    green: hexToRgb('#3bb273'),
    lightGreen: hexToRgb('#90bc1a'),
    yellow: hexToRgb('#fad12d'),
    orange: hexToRgb('#f07c12'),
    red: hexToRgb('#e15554'),
    black: hexToRgb('#000000'),
};

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16) / 255,
        g: parseInt(result[2], 16) / 255,
        b: parseInt(result[3], 16) / 255
    } : null;
}

export function lowerIntensity(color, divisor) {
    return { r: color.r / divisor, g: color.g / divisor, b: color.b / divisor };
}

export function toString(color, opacity = 1.0) {
    return `rgba(${Math.floor(color.r * 255)}, ${Math.floor(color.g * 255)}, ${Math.floor(color.b * 255)}, ${opacity})`;
}