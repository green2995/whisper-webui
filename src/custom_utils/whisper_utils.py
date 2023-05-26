from typing import List
from typing_extensions import TypedDict, NotRequired

class WhisperWord(TypedDict):
    word: str
    start: float
    end: float
    probability: float

class WhisperSegment(TypedDict):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    probability: NotRequired[float] # disfluency는 공백으로 표시됨
    words: NotRequired[List[WhisperWord]]

class WhisperJSON(TypedDict, total=False):  # 'total=False' to allow optional fields
    text: str
    segments: List[WhisperSegment]
    language: str

class TimeSpan:
    start: float
    end: float

    def __init__(self, start: float, end: float) -> None:
        self.start = start
        self.end = end

def find_gaps_between_segments(segments: List[WhisperSegment], threshold: float = 10) -> List[TimeSpan]:
    """
    Find gaps between segments for compensating unwanted omit

    Parameters
    ----------
    segments: List[WhisperSegment]
        The segments in the transcription result.
    threshold: float
        The threshold for gap. If gap between two segments is equal to or longer than {threshold} seconds, it is captured.

    Returns
    -------
    A list of start and end timestamps, in fractional seconds.
    """
    
    captured: List[TimeSpan] = []
    
    # Sort the segments by start time
    sorted_segments = sorted(segments, key=lambda seg: seg["start"])

    # Iterate over pairs of adjacent segments
    for i in range(len(sorted_segments) - 1):
        current_segment_end = sorted_segments[i]["end"]
        next_segment_start = sorted_segments[i+1]["start"]

        # If the gap between the current segment's end and the next segment's start is larger than threshold
        if next_segment_start - current_segment_end >= threshold:
            # Add the gap to the captured list
            captured.append(TimeSpan(current_segment_end, next_segment_start))

    return captured

def apply_offset_to_segment(segment: WhisperSegment, offset: float) -> WhisperSegment:
    segment['start'] += offset
    segment['end'] += offset
    
    for word in segment['words']:
        word['start'] += offset
        word['end'] += offset

    return segment
        

def merge_segments(segments: List[WhisperSegment]) -> List[WhisperSegment]:
    """
    Merge segments that potentially overlap each other. If two segments overlap each other, the one with the longer duration takes the place of the other.

    Parameters
    ----------
    segments: List[WhisperSegment]
        The segments in the transcription result.

    Returns
    -------
    A list of merged segments
    """

    if not segments:
        return []

    # Sort segments by start time
    sorted_segments = sorted(segments, key=lambda seg: seg["start"])

    # Initialize merged_segments with the first segment
    merged_segments = [sorted_segments[0]]

    for current in sorted_segments[1:]:
        # Get the last merged segment
        last = merged_segments[-1]

        # If the current segment overlaps with the last merged segment, correct timestamp
        if current["start"] <= last["end"]:
            last["end"] = current["start"]

        merged_segments.append(current)

    return merged_segments