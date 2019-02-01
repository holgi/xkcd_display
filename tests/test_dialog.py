import pytest


def test_parse_dialog():
    from xkcd_display.dialog import parse_dialog

    dialog = """
        Friend: You're flying! How?
        Cueball: Python!
        Cueball: I learned it last night!
        """
    transcript = parse_dialog(dialog)

    assert len(transcript) == 3
    assert transcript[0].speaker == "Friend"
    assert transcript[0].text == "You're flying! How?"
    assert transcript[1].speaker == "Cueball"
    assert transcript[1].text == "Python!"
    assert transcript[2].speaker == "Cueball"
    assert transcript[2].text == "I learned it last night!"


def test_adjust_narrators_cueball_cueball():
    from xkcd_display.dialog import parse_dialog, adjust_narrators

    dialog = """
        Cueball 1: You're flying! How?
        Cueball 2: Python!
        Cueball 2: I learned it last night!
        """
    transcript = adjust_narrators(parse_dialog(dialog))
    speakers = {line.speaker for line in transcript}
    assert speakers == {"cueball", "megan"}


def test_adjust_narrators_cueball_other():
    from xkcd_display.dialog import parse_dialog, adjust_narrators

    dialog = """
        Cueball 1: You're flying! How?
        Other Person: Python!
        Other Person: I learned it last night!
        """
    transcript = adjust_narrators(parse_dialog(dialog))
    assert transcript[0].speaker == "cueball"
    assert transcript[0].text == "You're flying! How?"
    assert transcript[1].speaker == "megan"
    assert transcript[1].text == "Python!"
    assert transcript[2].speaker == "megan"
    assert transcript[2].text == "I learned it last night!"


def test_adjust_narrators_other_cueball():
    from xkcd_display.dialog import parse_dialog, adjust_narrators

    dialog = """
        Other Person: You're flying! How?
        Cueball 2: Python!
        Cueball 2: I learned it last night!
        """
    transcript = adjust_narrators(parse_dialog(dialog))
    assert transcript[0].speaker == "megan"
    assert transcript[0].text == "You're flying! How?"
    assert transcript[1].speaker == "cueball"
    assert transcript[1].text == "Python!"
    assert transcript[2].speaker == "cueball"
    assert transcript[2].text == "I learned it last night!"


def test_adjust_narrators_other_other():
    from xkcd_display.dialog import parse_dialog, adjust_narrators

    dialog = """
        That Person: You're flying! How?
        Other Person: Python!
        Other Person: I learned it last night!
        """
    transcript = adjust_narrators(parse_dialog(dialog))
    speakers = {line.speaker for line in transcript}
    assert speakers == {"cueball", "megan"}


def test_adjust_narrators_to_many_narrators():
    from xkcd_display.dialog import parse_dialog, adjust_narrators

    dialog = """
        First Person: You're flying! How?
        Second Person: Python!
        Third Person: I learned it last night!
        """
    with pytest.raises(ValueError):
        adjust_narrators(parse_dialog(dialog))
