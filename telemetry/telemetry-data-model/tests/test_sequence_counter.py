from sequence_counter import SequenceCounter


def test_sequence_wraparound():
    counter = SequenceCounter(start=65535)

    assert counter.next() == 65535
    assert counter.next() == 0
    assert counter.next() == 1