""" process xkcd transcripts stored in text files """

from collections import namedtuple


SpokenText = namedtuple("NarratedText", ["speaker", "text"])


def parse_dialog(raw_text):
    """ parses a raw dialog text

    raw_text: text of the dialog
    resturns: list of SpokenText named tuples
    """
    stripped = raw_text.strip()
    raw_split = (line.split(":", 1) for line in stripped.split("\n"))
    return [
        SpokenText(speaker=speaker.strip(), text=text.strip())
        for speaker, text in raw_split
    ]


def adjust_narrators(transcript):
    """ adjusts the names of the speakers to be "cueball" or "megan"

    transcript: list of SpokenText named tuples
    returns: list of SpokenText named tuples with adjusted speakers
    """
    speakers = {spoken_line.speaker.lower() for spoken_line in transcript}
    if len(speakers) != 2:
        raise ValueError(f"Wrong number of speakers: {len(speakers)}")

    speaker_1, speaker_2 = speakers
    if "cueball" in speaker_1 and "cueball" in speaker_2:
        # both are related to cueball? Just make up something
        speaker_map = {speaker_1: "cueball", speaker_2: "megan"}
    elif "cueball" in speaker_1:
        speaker_map = {speaker_1: "cueball", speaker_2: "megan"}
    elif "cueball" in speaker_2:
        speaker_map = {speaker_1: "megan", speaker_2: "cueball"}
    else:
        # no mention of cueball, Just make up something
        speaker_map = {speaker_1: "cueball", speaker_2: "megan"}

    adjusted_names = [
        SpokenText(
            speaker=speaker_map[spoken_line.speaker.lower()],
            text=spoken_line.text,
        )
        for spoken_line in transcript
    ]
    return adjusted_names
