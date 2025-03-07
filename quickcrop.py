import warnings
import matplotlib.pyplot as plt
import quickcrop.utils as qcu
from numpy.typing import ArrayLike
from numpy import asarray, ndarray


def gui_crop(uncropped: ArrayLike,
             square: bool = False,
             bias: str = "tl",
             cmap: str = "bone",
             crop_timeout: int = 300,
             conf_timeout: int = 60,
             dpi: int = 200) -> ndarray:
    """Quickly crop an image to a square using matplotlib by specifying four corners within which
    to crop.

    Parameters
    ----------
    uncropped : ArrayLike
        The uncropped image, as a numpy array or some format which can be cast to a numpy array.
    square : bool, optional
        Whether to return a rectangular (False) or square (True) region. Defult is False (rectangular).
    bias : str, optional
        A string containing exactly one of ["t", "b"] and exactly one of ["l", "r"] which defines
        the bias direction for cropping (which sides of a non-square region we prefer to keep when
        cropping down to a square).  Default is "tl".
    cmap : str, optional
        The colormap to be passed to matplotlib.  See the matplotlib documentation at
        https://matplotlib.org/stable/tutorials/colors/colormaps.html for available options.
        Default is "bone".
    crop_timeout : int, optional
        How long to wait to get user input for the crop before giving up.  If cropping
        times out, the uncropped image will be returned. Default is 300 seconds (5 minutes).
        Set to -1 to disable timing out.
    conf_timeout : int, optional
        How long to wait for the user to confirm their crop before giving up.  If confirmation
        times out, cropping will be retried.  Default is 60 seconds (1 minute).  Set to -1
        to disable timing out.
    dpi : int, optional
        The DPI with which to show images for cropping and confirmation. Default is 200;
        the default matplotlib setting is 100.  Increasing this value can make precision cropping
        easier, while decreasing this value is better for low-resolution displays.

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
            corner_points = plt.ginput(n=4, timeout=crop_timeout)  # TODO: Rework to support non-quad inputs
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
            return asarray(uncropped)

        # If all is well, proceed with cropping
        rect = qcu.minimal_rect(corner_points, bias=bias, square=square)

        minx, maxx = rect[0][0], rect[1][0]
        miny, maxy = rect[0][1], rect[3][1]

        cropped = asarray(uncropped)[miny:maxy, minx:maxx]

        # Show the cropped image and confirm or retry
        with plt.rc_context({"figure.dpi": dpi}):
            fig, ax = plt.subplots()
            plt.axis("off")
            instructions = "To retry the crop click any mouse button\n" +\
                           "Otherwise to confrim hit any keyboard button"
            fig.text(0.5, 0.9, instructions, horizontalalignment="center", size="xx-small")
            ax.imshow(cropped, cmap=cmap)
            # Wait for the user to click  to confirm
            if plt.waitforbuttonpress(timeout=conf_timeout):
                plt.close(fig)
                return cropped

            plt.close(fig)
            continue
