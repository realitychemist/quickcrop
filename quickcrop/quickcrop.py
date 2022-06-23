import warnings
import matplotlib.pyplot as plt
import quickcrop.utils as qcu
from numpy.typing import ArrayLike
from numpy import asarray


def gui_crop(uncropped: ArrayLike,
             cmap: str = "bone",
             crop_timeout: int = 300,
             conf_timeout: int = 60,
             dpi: int = 200,
             bias: str = "tl"):
    """Quickly crop an image to a square using matplotlib by specifying four corners within which
    to crop.

    Parameters
    ----------
    uncropped : ArrayLike
        The uncropped image, as a numpy array or some format which can be converted to a numpy
        array (such as a list of lists).
    cmap : str, optional
        The colormap to be passed to matplotlib.  See the matplotlib documentation at
        https://matplotlib.org/stable/tutorials/colors/colormaps.html for details about the
        available options. The default is "bone".
    crop_timeout : int, optional
        How long to wait to get user input for the crop before giving up.  If cropping
        times out, the uncropped image will be returned. The default is 300 seconds (5 minutes).
        Set to -1 to disable timing out.
    conf_timeout : int, optional
        How long to wait for the user to confirm their crop before giving up.  If confirmation
        times out, cropping will be retried.  The default is 60 seconds (1 minute).  Set to -1
        to disable timing out.
    dpi : int, optional
        The DPI with which to show images for cropping and confirmation. The default is 200;
        the default matplotlib setting is 100.  Increasing this value can make precision cropping
        easier, while decreasing this value is better for low-resolution displays.
    bias : str, optional
        A string containing exactly one of ["t", "b"] and exactly one of ["l", "r"] which defines
        the bias direction for cropping (which sides of a non-square region we prefer to keep when
        cropping down to a square).  The default is "tl".

    Raises
    ------
    RuntimeWarning
        Raised if the user manually cancels cropping or if the cropping times out.
    UserWarning
        May be raised when attempting to crop from extremely non-square regions; matplotlib will
        also render a blank canvas.  Usually solvable by retrying the crop with a more square
        region.
    ValueError
        This error will be raised if an invalid bias string is passed.

    Returns
    -------
    ArrayLike
        Returns a numpy array representing an image.  If the crop is successful, the cropped image
        will be returned.  If the user manually cancels the crop or if cropping times out, the
        uncropped image will be returned and a RuntimeWarning will be raised.
    """

    # Crop-confirm loop
    while True:
        # Plot and show starting image
        with plt.rc_context({"figure.dpi": dpi}):
            fig, ax = plt.subplots()
            plt.axis("off")
            instructions = "Click on the four corners within which to crop\n" +\
                           "Right-click (or press Backspace/Delete) to remove last point\n" +\
                           "Middle-click or pressing Enter to cancel the crop"
            fig.text(0.5, 0.9, instructions, horizontalalignment="center", size="xx-small")
            ax.imshow(uncropped, cmap=cmap)
            # Get the user to click the four corners
            corner_points = plt.ginput(n=4, timeout=crop_timeout)
            plt.close(fig)

        # Sanity check and handle input errors
        if len(set(corner_points)) != 4:
            if len(corner_points) == 4:
                # User probably unintentionally clicked the same point twice
                warnings.warn("Identical points in input, please try again", RuntimeWarning)
                continue

            # Intentional exit or timeout: return uncropped
            warnings.warn("Cropping terminated early, returning uncropped image",
                          RuntimeWarning)
            return uncropped

        # If all is well, proceed with cropping
        msq = qcu.minimal_square(corner_points, bias=bias)
        # Convert from float to integers so we can slice
        msq = [(int(point[0]), int(point[1])) for point in msq]
        minx, maxx = msq[0][0], msq[1][0]
        miny, maxy = msq[0][1], msq[3][1]

        cropped = asarray(uncropped)[miny:maxy, minx:maxx]

        # Show the cropped image and confrim or retry
        with plt.rc_context({"figure.dpi": dpi}):
            fig, ax = plt.subplots()
            plt.axis("off")
            instructions = "To retry the crop press Del or Backspace, or middle-click anywhere\n" +\
                           "Otherwise to confrim hit any other button or click anywhere"
            fig.text(0.5, 0.9, instructions, horizontalalignment="center", size="xx-small")
            ax.imshow(cropped, cmap=cmap)
            # Wait for the user to click  to confirm
            conf_point = plt.ginput(n=1, timeout=conf_timeout)
            if len(conf_point) == 1:
                plt.close(fig)
                return cropped

            plt.close(fig)
            continue
