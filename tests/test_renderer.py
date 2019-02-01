import pytest
from collections import namedtuple

from xkcd_display import Size


def mock_tuple(**kargs):
    MockTuple = namedtuple("MockTuple", list(kargs.keys()))
    return MockTuple(**kargs)


def test_eval_text_metrics(mocker):
    from xkcd_display.renderer import eval_text_metrics, FontMetrics
    from wand.drawing import Drawing

    mock_result = mock_tuple(
        text_width=1.2, text_height=2.3, character_height=3.4
    )
    mocker.patch.object(Drawing, "get_font_metrics", return_value=mock_result)

    result = eval_text_metrics(Drawing(), "image", "Hello!")

    assert isinstance(result, FontMetrics)
    assert result.width == 1
    assert result.height == 2
    assert result.character_height == 3


def test_unique_text_wraps():
    from xkcd_display.renderer import unique_text_wraps

    text = "Python! I learned it last night! Everything is so simple!"

    result = list(unique_text_wraps(text))

    expected = [
        [
            "Python!",
            "I",
            "learned",
            "it",
            "last",
            "night!",
            "Everything",
            "is",
            "so",
            "simple!",
        ],
        [
            "Python!",
            "I",
            "learned",
            "it",
            "last",
            "night!",
            "Everything",
            "is so",
            "simple!",
        ],
        [
            "Python!",
            "I",
            "learned",
            "it last",
            "night!",
            "Everything",
            "is so",
            "simple!",
        ],
        [
            "Python! I",
            "learned",
            "it last",
            "night!",
            "Everything",
            "is so",
            "simple!",
        ],
        [
            "Python! I",
            "learned it",
            "last night!",
            "Everything",
            "is so",
            "simple!",
        ],
        [
            "Python! I",
            "learned it",
            "last night!",
            "Everything is",
            "so simple!",
        ],
        ["Python! I learned", "it last night!", "Everything is so", "simple!"],
        ["Python! I learned it", "last night! Everything", "is so simple!"],
        ["Python! I learned it last", "night! Everything is so simple!"],
        ["Python! I learned it last night! Everything is so simple!"],
    ]
    assert result == expected


def test_find_best_fitting_text_wrap(mocker):
    from xkcd_display.renderer import find_best_fitting_text_wrap
    from wand.drawing import Drawing

    text = "Python! I learned it last night! Everything is so simple!"
    max_size = Size(width=1, height=1)
    effects = [Size(width=1, height=2) for i in range(0, 7)]
    effects.append(Size(1, 1))
    mocker.patch(
        "xkcd_display.renderer.eval_text_metrics", side_effect=effects
    )

    result = find_best_fitting_text_wrap(Drawing(), "image", max_size, text)

    assert result == [
        "Python! I learned it",
        "last night! Everything",
        "is so simple!",
    ]


@pytest.mark.parametrize(
    "start, stop, factor, expected",
    [
        (1, 10, 1, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (1, 15, 1.5, [1, 2, 3, 4, 6, 10]),
        (2, 20, 2, [2, 4, 8, 16]),
    ],
)
def test_font_sizes(start, stop, factor, expected):
    from xkcd_display.renderer import font_sizes

    result = list(font_sizes(start, stop, factor))

    assert list(result) == expected


def test_find_best_text_fit(mocker):
    from xkcd_display.renderer import (
        find_best_text_fit,
        FontMetrics,
        TextFitParameter,
    )

    lines = ["Python! I learned it", "last night! Everything", "is so simple!"]
    mocker.patch(
        "xkcd_display.renderer.find_best_fitting_text_wrap", return_value=lines
    )
    effects = [
        FontMetrics(width=1, height=1, character_height=1),
        FontMetrics(width=2, height=2, character_height=2),
        FontMetrics(width=3, height=3, character_height=3),
        FontMetrics(width=9, height=9, character_height=4),
    ]
    mocker.patch(
        "xkcd_display.renderer.eval_text_metrics", side_effect=effects
    )

    class MockSketch:
        def __init__(self):
            self.font_size = 1

    sketch = MockSketch()
    image = Size(width=20, height=20)

    result = find_best_text_fit(sketch, image, Size(width=4, height=4), "")

    assert isinstance(result, TextFitParameter)
    assert result.lines == lines
    assert result.font_size == 3
    assert result.width == 3
    assert result.height == 3
    assert result.character_height == 3


def test_find_best_raises_value_error(mocker):
    from xkcd_display.renderer import (
        find_best_text_fit,
        FontMetrics,
        TextFitParameter,
    )

    mocker.patch("xkcd_display.renderer.find_best_fitting_text_wrap")
    mocker.patch("xkcd_display.renderer.font_sizes", return_value=[])
    sketch = mock_tuple(font_size=1)
    image = mock_tuple(height=1)

    with pytest.raises(ValueError):
        find_best_text_fit(sketch, image, "size", "text")


def test_render_text(mocker):
    from xkcd_display.renderer import (
        render_text,
        TextFitParameter,
        RenderingFit,
    )

    lines = ["Python! I learned it", "last night! Everything", "is so simple!"]
    mock_result = TextFitParameter(
        lines=lines, font_size=2, width=8, height=8, character_height=4
    )
    mocker.patch(
        "xkcd_display.renderer.find_best_text_fit", return_value=mock_result
    )
    mocker.patch("wand.drawing.Drawing.text")
    mocker.patch("wand.drawing.Drawing.draw")

    image = Size(width=20, height=20)
    result = render_text(image, "text", "font", padding=1)

    assert isinstance(result, RenderingFit)
    assert result.lines == lines
    assert result.font_size == 2
    assert result.x == 5
    assert result.y == 9
    assert result.character_height == 4


def test_create_image_blob(mocker):
    from xkcd_display.renderer import create_image_blob

    mocker.patch("xkcd_display.renderer.render_text")
    mocker.patch("wand.image.Image.make_blob", return_value="some blob")

    result = create_image_blob("text", "font", Size(width=1, height=1))

    assert result == "some blob"


def test_render_xkcd_image(mocker):
    from xkcd_display.renderer import render_xkcd_image

    mocker.patch(
        "xkcd_display.renderer.create_image_blob", return_value="xkcd image"
    )

    result = render_xkcd_image("text")

    assert result == "xkcd image"
