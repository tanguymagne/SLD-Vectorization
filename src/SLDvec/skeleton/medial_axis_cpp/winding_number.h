// winding_number.h
#ifndef WINDING_NUMBER_H
#define WINDING_NUMBER_H

#include <vector>
#include <cmath>

/**
 * @brief Computes the winding number of a closed curve around a point in 2D space.
 *
 * The winding number represents the number of times a closed curve travels
 * counterclockwise around a given point. For a simple closed curve, it will be
 * either +1 (counterclockwise) or -1 (clockwise) if the point is inside the curve,
 * and 0 if the point is outside the curve.
 *
 * @param curvePoints A vector of (x,y) coordinates representing points sampled on the curve.
 *                     The curve should be closed (i.e., the last point connects back to the first).
 * @param targetPoint The (x,y) coordinates of the point to test.
 *
 * @return The winding number as a double.
 *         Positive values indicate counterclockwise winding,
 *         negative values indicate clockwise winding,
 *         and zero indicates the point is outside the curve.
 *
 * @note The function assumes the curve is closed. If not, the behavior is undefined.
 * @note The winding number is normalized by 2π.
 *
 * @example
 *     std::vector<std::pair<double, double>> curve = {
 *         {0.0, 0.0}, {1.0, 0.0}, {1.0, 1.0}, {0.0, 1.0}, {0.0, 0.0}
 *     };
 *     std::pair<double, double> test_point = {0.5, 0.5};
 *     double result = windingNumber(curve, test_point); // Will return ~1.0
 */
double windingNumber(
    const std::vector<std::pair<double, double>> &curvePoints,
    const std::pair<double, double> &targetPoint)
{
    double w = 0.0;

    for (std::size_t j = 0; j < curvePoints.size() - 1; ++j)
    {
        const std::pair<double, double> &point1 = curvePoints[j];
        const std::pair<double, double> &point2 = curvePoints[j + 1];

        // Vectors from the targetPoint to the curve points
        double x1 = point1.first - targetPoint.first;
        double y1 = point1.second - targetPoint.second;
        double x2 = point2.first - targetPoint.first;
        double y2 = point2.second - targetPoint.second;

        // Determinant and dot product
        double det = x1 * y2 - y1 * x2;
        double dotProduct = x1 * x2 + y1 * y2;

        // Calculate angle using atan2
        w += std::atan2(det, dotProduct);
    }

    // Normalize by 2 * PI
    w = w / (2 * M_PI);

    return w;
}

#endif // WINDING_NUMBER_H