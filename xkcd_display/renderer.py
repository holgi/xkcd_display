""" renders an text as big as possible in an image """

import textwrap

from collections import namedtuple
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from . import Size


FontMetrics = namedtuple(
    "FontMetrics", ["width", "height", "character_height"]
)
TextFitParameter = namedtuple(
    "TextFitParameter",
    ["lines", "font_size", "width", "height", "character_height"],
)
RenderingFit = namedtuple(
    "RenderingFit", ["lines", "font_size", "x", "y", "character_height"]
)


def eval_text_metrics(sketch, img, text):
    """ Quick helper function to calculate width/height of rendered text.

    sketch: a wand.drawing.Drawing instance
    img: a wand.image.Image instance
    text: the text to render
    returns: a "FontMetrics" named tuple

    note: this relies on font properties already set on the sketch
    """
    metrics = sketch.get_font_metrics(img, text, multiline=True)
    return FontMetrics(
        width=int(metrics.text_width),
        height=int(metrics.text_height),
        character_height=int(metrics.character_height),
    )


def unique_text_wraps(text):
    """ Find all unique wraps of a text

    text: text to wrap, words a preserved
    returns: iterator of uniquely wrapped lines
    """
    lines_checked = set()
    for wrap_at in range(1, len(text) + 1):
        wrapped_lines = textwrap.wrap(text, wrap_at, break_long_words=False)
        number_of_lines = len(wrapped_lines)
        if number_of_lines not in lines_checked:
            lines_checked.add(number_of_lines)
            yield wrapped_lines


def find_best_fitting_text_wrap(sketch, img, max_size, text):
    """ returns the best fitting way to wrap a text inside a box

    sketch: a wand.drawing.Drawing instance
    img: a wand.image.Image instance
    max_size: the largest size a text should have, a FontMetrics named tuple
    text: the text fit
    returns: the wrapped text lines for the best possible fit

    note: this relies on font properties already set on the sketch
    """
    expected_ratio = max_size.width / max_size.height
    for wrapped_lines in unique_text_wraps(text):
        wrapped_text = "\n".join(wrapped_lines)
        rendered_size = eval_text_metrics(sketch, img, wrapped_text)
        rendered_ratio = rendered_size.width / rendered_size.height
        fit_ratio = rendered_ratio / expected_ratio
        if fit_ratio >= 1:
            break
    return wrapped_lines


def font_sizes(start, stop, factor=1.2):
    """ iterator for gently increasing font sizes

    start: start value, ineger
    stop: upper limit of font size, integer
    factor: factor for increasing the font size
    returns: integer
    """
    font_size = int(start)
    while font_size < stop:
        yield int(font_size)
        new_font_size = font_size * factor
        if int(new_font_size) == int(font_size):
            new_font_size = font_size + 1
        font_size = new_font_size


def find_best_text_fit(sketch, img, max_size, text):
    """ returns the best way for a text to still fit in a area


    sketch: a wand.drawing.Drawing instance
    img: a wand.image.Image instance
    max_size: the largest size a text should have, a FontMetrics named tuple
    text: the text fit
    returns: a BestTextFit named tuple with the needed parameters

    note: this relies on font properties already set on the sketch
    """

    # wrap the text in a best fitting style
    lines = find_best_fitting_text_wrap(sketch, img, max_size, text)
    wrapped_text = "\n".join(lines)
    best_fit = None
    # increase the font size and check if it still fits in max_size
    for font_size in font_sizes(start=sketch.font_size, stop=img.height):
        sketch.font_size = font_size
        size = eval_text_metrics(sketch, img, wrapped_text)
        if max_size.width < size.width or max_size.height < size.height:
            break
        else:
            best_fit = TextFitParameter(
                lines=lines,
                font_size=font_size,
                width=size.width,
                height=size.height,
                character_height=size.character_height,
            )
    if best_fit is None:
        raise ValueError("Could not find fitting font size")
    return best_fit


def render_text(
    img,
    text,
    font,
    *,
    antialias=True,
    padding=0,
    color="black",
    font_size_hint=12
):
    """ renders a text as large as possible on a provided image

    img: a wand.image.Image instance
    text: the text to render
    font: font to use, path to a font file

    optional:
    antialias: use antialiasing, defaults to True
    padding: padding to apply to the image for the text rendering
    color: text color to use
    font_size_hint: font size used as a starting point for the search of the
        largest font size, also used for finding the best way to wrap a text.
    returns: parameters used to render the text on the image
    """

    box_size = Size(img.width - 2 * padding, img.height - 2 * padding)

    with Drawing() as sketch:
        # Set the basic font style
        sketch.fill_color = Color(color)
        sketch.font = font
        sketch.font_size = font_size_hint
        sketch.text_antialias = antialias

        # search for the largest font size to render the text inside the box
        best_fit = find_best_text_fit(sketch, img, box_size, text)
        sketch.font_size = best_fit.font_size

        # calculate the positioning of the text in the image
        # the y value used in sketch.text() method to render the text
        # specifies the baseline of the first line of text
        # this must be adjusted with the character height of the text
        x = (img.width - best_fit.width) // 2
        unadjusted_y = (img.height - img.height) // 2
        y = unadjusted_y + best_fit.character_height

        # render the text and  return the image
        sketch.text(x, int(y), "\n".join(best_fit.lines))
        sketch.draw(img)

        return RenderingFit(
            lines=best_fit.lines,
            font_size=best_fit.font_size,
            x=int(x),
            y=int(y),
            character_height=best_fit.character_height,
        )


def create_image_blob(
    text, font, image_size, *, background_color="white", format="png", **kwargs
):
    """ renders a text as an image and returns its binary representation

    text: the text to render
    font: the font to use, path to a font file
    image_size: image size, provided as a "Size" named tuple
    background_color: background color for the image, use None for a
        transparent background
    format: binary representation format of the image

    all other keyword parameters are passed to the render_text() function
    """
    if background_color is not None:
        background_color = Color(background_color)
    with Image(
        width=image_size.width,
        height=image_size.height,
        background=background_color,
    ) as img:
        render_text(img, text, font, **kwargs)
        return img.make_blob(format)


def render_xkcd_image(text):
    """ returns a image blob with text rendered as large as possible

    parameters are fitting the xkcd display
    """
    return create_image_blob(
        text,
        "xkcd-script.ttf",
        Size(width=400, height=300),
        background_color="white",
        format="png",
        antialias=True,
        padding=5,
        color="black",
        font_size_hint=12,
    )