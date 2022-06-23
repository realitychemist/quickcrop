from typing import List, Tuple


def __cw_sort(points: List[Tuple[float, float]]):
    """
    Parameters
    ----------
    points : List[Tuple[float, float]]
        A list of 2D points which describe a roughly-rectabgular region.  If the region is too far
        from rectangular, this sort may fail!  Handling this kind of case is not yet implemented.

    Returns
    -------
    List[Tuple[float, float]]
        The list of points, sorted into CW order, starting from the top left-most point.

    """
    # x-sort the points
    points.sort(key=lambda x: x[0])
    lpoints, rpoints = points[:2], points[2:]
    # Image origin at top left, so y-sort must be reversed to get the expected ordering
    lpoints.sort(key=lambda y: y[0], reverse=True)
    rpoints.sort(key=lambda y: y[0], reverse=True)
    return [lpoints[1], rpoints[0], rpoints[1], lpoints[0]]


def __squarify(points: List[Tuple[float, float]], bias: str):
    """
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
    # The square must a side length equal to the smallest
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

    # Turn the points back into immutable tuples; overwrites original list
    points = [tuple(point) for point in _points]
    return points


def minimal_square(points: List[Tuple[float, float]], bias: str = "tl"):
    """
    Parameters
    ----------
    points : List[Tuple[float, float]]
        A list of points, as returned from matplotlib.pyplot.ginput.  Note that if these points
        descirbe a region too different from a rectangle, this funcion MAY SILENTLY FAIL.  Be
        very careful with such inputs.
    bias : str, optional
        A string containing exactly one of ["t", "b"] and exactly one of ["l", "r"] which defines
        the bias direction (which sides we prefer to keep). The default is "tl".

    Raises
    ------
    NotImplementedError
        Non-quadrilateral regions are not yet implemented, so this error will be raised if the list
        of distinct points is not exactly length 4.
    ValueError
        This error will be raised if an invalid bias string is passed.

    Returns
    -------
    List[Tuple[float, float]]
        A list of points describing the minimal square crop solution.  The points will be sorted in
        clockwise order, starting from the top-leftmost point.

    """
    # List of tuple is the default returned from matplotlib.pyplot.ginput,
    #  but in our case we want to make sure we have exactly 4 points.  They
    #  should also be distinct
    if len(set(points)) != 4:
        raise NotImplementedError("Exactly four (distinct) points must be passed: "
                                  "current implementation only supports quadrilateral regions.")

    # Sanity check bias str: must contain exactly one of ["t", "b"], and exactly one of ["l", "r"]
    if ["t" in bias, "b" in bias].count(True) != 1:
        raise ValueError("Invalidly formatted bias string; "
                         "bias string must contain exactly one of 't' or 'b'.")
    if ["l" in bias, "r" in bias].count(True) != 1:
        raise ValueError("Invalidly formatted bias string; "
                         "bias string must contain exactly one of 'l' or 'r'.")

    points = __cw_sort(points)
    max_ty = max([points[0][1], points[1][1]])
    min_rx = min([points[1][0], points[2][0]])
    min_by = min([points[2][1], points[3][1]])
    max_lx = max([points[3][0], points[0][0]])

    minimal_rect = [(max_lx, max_ty),
                    (min_rx, max_ty),
                    (min_rx, min_by),
                    (max_lx, min_by)]
    minsq = __squarify(minimal_rect, bias)
    return minsq


# TODO: Use scipy.optimize.minimize to implement a maximal square, with the minimal square as the
#  starting guess
