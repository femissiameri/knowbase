import numpy as np


def serialize_vector(
    vector: list[float],
) -> bytes:
    array = np.asarray(
        vector,
        dtype=np.float32,
    )

    return array.tobytes()


def deserialize_vector(
    data: bytes,
) -> np.ndarray:
    return np.frombuffer(
        data,
        dtype=np.float32,
    )