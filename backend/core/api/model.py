import json
from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field, NonNegativeFloat, NonNegativeInt, PositiveInt, StrictBool, model_validator
from typing_extensions import Annotated


class ConfigModel(
    BaseModel
):  # TODO: dynamic beat_res, beat_res_rest, chord_maps, chord_tokens_with_root_note, chord_unknown, time_signature_range
    tokenizer: Literal[
        "REMI", "REMIPlus", "MIDILike", "TSD", "Structured", "CPWord", "Octuple", "MuMIDI", "MMM", "PerTok"
    ]
    pitch_range: Annotated[list[Annotated[int, Field(ge=0, le=127)]], Field(min_length=2, max_length=2)]
    num_velocities: Annotated[int, Field(ge=0, le=127)]
    special_tokens: list[str]
    use_chords: StrictBool
    use_rests: StrictBool
    use_tempos: StrictBool
    use_time_signatures: StrictBool
    use_sustain_pedals: StrictBool
    use_pitch_bends: StrictBool
    nb_tempos: NonNegativeInt
    tempo_range: Annotated[list[NonNegativeInt], Field(min_length=2, max_length=2)]
    log_tempos: StrictBool
    delete_equal_successive_tempo_changes: StrictBool
    sustain_pedal_duration: StrictBool
    pitch_bend_range: Annotated[list[int], Field(min_length=3, max_length=3)]
    delete_equal_successive_time_sig_changes: StrictBool
    use_programs: StrictBool
    programs: Optional[Annotated[list[int], Field(min_length=2, max_length=2)]]
    one_token_stream_for_programs: Optional[StrictBool]
    program_changes: Optional[StrictBool]
    # added for pertok
    use_microtiming: StrictBool
    ticks_per_quarter: Annotated[int, Field(ge=24, le=960)]
    max_microtiming_shift: Annotated[float, Field(ge=0, le=1)]
    num_microtiming_bins: Annotated[int, Field(ge=1, le=64)]

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    @model_validator(mode="after")
    @classmethod
    def check_valid_ranges(cls, values):
        min_pitch = values.pitch_range[0]
        max_pitch = values.pitch_range[1]
        if min_pitch > max_pitch:
            raise ValueError("max_pitch must be greater or equal to min_pitch")

        min_tempo = values.tempo_range[0]
        max_tempo = values.tempo_range[1]
        if min_tempo > max_tempo:
            raise ValueError("max_tempo must be greater or equal to min_tempo")

        min_pitch_bend = values.pitch_bend_range[0]
        max_pitch_bend = values.pitch_bend_range[1]
        if min_pitch_bend > max_pitch_bend:
            raise ValueError("max_pitch_bend must be greater or to than min_pitch_bend")

        return values


class MusicInformationData(BaseModel):
    # Basic MIDI file information
    title: str
    resolution: PositiveInt
    tempos: list[tuple[NonNegativeInt, float]]
    key_signatures: list[tuple[NonNegativeInt, int, str]]
    time_signatures: list[tuple[NonNegativeInt, int, int]]

    # Additional metrics retrieved from the MIDI file
    pitch_range: NonNegativeInt
    n_pitches_used: NonNegativeInt
    polyphony: NonNegativeFloat

    empty_beat_rate: NonNegativeFloat
    drum_pattern_consistency: NonNegativeFloat


@dataclass
class BasicInfoData:
    title: str
    resolution: int
    tempos: list[tuple[int, float]]
    key_signatures: list[tuple[int, int, str]]
    time_signatures: list[tuple[int, int, int]]


@dataclass
class MetricsData:
    pitch_range: int
    n_pitches_used: int
    polyphony: float

    empty_beat_rate: float
    drum_pattern_consistency: float


@dataclass
class Note:
    pitch: int
    name: str
    start: int
    end: int
    velocity: int
