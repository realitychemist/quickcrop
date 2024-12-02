from typing import List, Tuple
import numpy as np
from scipy.spatial import ConvexHull


def _squarify(points: List[Tuple[float, float]], bias: str):
    """Make a rectangular region into a square region.

    Parameters
    ----------
    points : List[Tuple[float, float]]
        List of points as tuples; must be ordered clockwise, starting from the top left.  These
        must define a rectangle (e.g. points[0][0] == points[3][0], points[0][1] == points[1][1],
        etc.) else we'll get nonsense.
    bias : str
        A string containing exactly one of ["t", "b"] and exactly one of ["l", "r"] which defines
        the bias direction (which sides we prefer to keep).

    Returns
    -------
    List[Tuple[flost, float]]
        The list of points, cropped down to be a square.

    """
    # The square must have a side length equal to the smallest
    vlen = points[3][1] - points[0][1]  # Left side length == right side length
    hlen = points[1][0] - points[0][0]  # Top side length == bottom side length

    # Make the points mutable
    _points = [list(point) for point in points]

    if hlen < vlen:
        if "t" in bias:
            # Crop off the bottom
            _points[2][1] = points[1][1] + hlen
            _points[3][1] = points[0][1] + hlen
        elif "b" in bias:
            # Crop off the top
            _points[0][1] = points[3][1] - hlen
            _points[1][1] = points[2][1] - hlen
    else:  # vlen < hlen
        if "l" in bias:
            # Crop off the right
            _points[1][0] = points[0][0] + vlen
            _points[2][0] = points[3][0] + vlen
        if "r" in bias:
            # Crop off the left
            _points[0][0] = points[1][0] - vlen
            _points[3][0] = points[2][0] - vlen

    # Turn the points back into immutable tuples
    return [tuple(point) for point in _points]


def _interior_round(points: List[Tuple[float, float]]):
    """Round floats to integers, ensuring that rounding occurs toward the interior of a rectangular region.

    Parameters
    ----------
    points : List[Tuple[float, float]]
        List of points as (x, y) tuples, where xs and ys are floats; must be ordered clockwise,
        starting from the top left.

    Returns
    -------
    List[Tuple[int, int]]
        The list of points, rounded to integers in the interior of the above region.

    """
    # Make the data structure mutable
    _points = [list(point) for point in points]
    tl, tr, br, bl = _points[0], _points[1], _points[2], _points[3]

    # X - round up
    tl[0] = int(np.ceil(tl[0]))
    bl[0] = int(np.ceil(bl[0]))
    # X - round down
    tr[0] = int(np.floor(tr[0]))
    br[0] = int(np.floor(tr[0]))
    # Y - round up
    tl[1] = int(np.ceil(tl[1]))
    tr[1] = int(np.ceil(tr[1]))
    # Y - round down
    bl[1] = int(np.floor(bl[1]))
    br[1] = int(np.floor(br[1]))

    # Turn the points back into immutable tuples
    return [tuple(point) for point in [tl, tr, br, bl]]


def minimal_rect(points: List[Tuple[float, float]], bias: str = "tl", square: bool = False):
    """
    Parameters
    ----------
    points : List[Tuple[float, float]]
        A list of points, as returned from matplotlib.pyplot.ginput.  Note that if these points
        descirbe a region too different from a rectangle, this funcion MAY SILENTLY FAIL.  Be
        careful with such inputs.
    bias : str, optional
        A string containing exactly one of ["t", "b"] and exactly one of ["l", "r"] which defines
        the bias direction (which sides we prefer to keep). Default is "tl".
    square : bool, optional
        If False, a rectangular region will be returned. If True, the rectangular region will be further
        cropped to be square. Defualt is False.

    Raises
    ------
    NotImplementedError
        Non-quadrilateral regions are not yet implemented, so this error will be raised if the list
        of distinct points is not exactly length 4.
    ValueError
        This error will be raised if an invalid bias string is passed, or if the given points do
        not form a convex region.
    RuntimeError
        Rasied by failed sanity checking; may be raised if the passed points are highly non-square.

    Returns
    -------
    List[Tuple[int, int]]
        A list of points describing the minimal square crop solution.  The points will be sorted in
        clockwise order, starting from the top-leftmost point, and will be integer-valued.

    """
    # List of tuple is the default returned from matplotlib.pyplot.ginput,
    #  but in our case we want to make sure we have exactly 4 points.  They
    #  should also be distinct
    if len(set(points)) != 4:
        raise NotImplementedError("Exactly four (distinct) points must be passed: "
                                  "current implementation only supports quadrilateral regions.")

    # Bias string must contain exactly one of ["t", "b"], and exactly one of ["l", "r"]
    if ["t" in bias, "b" in bias].count(True) != 1:
        raise ValueError("Invalidly formatted bias string: "
                         "bias string must contain exactly one of 't' or 'b'.")
    if ["l" in bias, "r" in bias].count(True) != 1:
        raise ValueError("Invalidly formatted bias string: "
                         "bias string must contain exactly one of 'l' or 'r'.")

    # Form convex hull from points to ensure convexity
    # TODO: In the future I can probably use ConvexHull to solve this for non-quad point inputs
    hull = ConvexHull(np.asarray(points), incremental=True)
    verts = hull.vertices
    sorted_points = [list(points[i]) for i in verts]
    hull_vertices = [list(hull.points[i]) for i in verts]
    if not sorted_points == hull_vertices:
        raise ValueError("Passed points do not form a convex region: "
                         "minimal rectangular region is undefined on concave regions.")

    sorted_x, sorted_y = sorted([tup[0] for tup in points]), sorted([tup[1] for tup in points])
    # The following is only guaranteed to work for convex quadrilateral regions
    minimal_rect = [(sorted_x[1], sorted_y[1]),
                    (sorted_x[-2], sorted_y[1]),
                    (sorted_x[-2], sorted_y[-2]),
                    (sorted_x[1], sorted_y[-2])]
    if square:
        cropped = _squarify(minimal_rect, bias)
        # Convert indices to integers for slicing
        cropped = _interior_round(cropped)
    else:
        cropped = _interior_round(minimal_rect)

    # Sanity check: the rectangle should be entirely inside the hull, so adding the it's
    #  points to the hull should not change the vertex list
    hull.add_points(cropped)
    if not np.all(hull.vertices == verts):
        raise RuntimeError("Sanity check failed: cropped falls outside convex hull! "
                           "Was your region highly non-rectangular?")
    return cropped


# TODO: Use scipy.optimize.minimize to implement a maximal square, with the minimal square as the
#  starting guess
