def inject_single_bit_error(codeword, position):
    """
    Flip exactly one bit in a Hamming codeword.

    position is 1-based:
    position 1 = first bit
    position 2 = second bit
    ...
    """

    corrupted = codeword.copy()

    index = position - 1

    if index < 0 or index >= len(corrupted):
        raise ValueError("Invalid bit position")

    # Flip 0 -> 1 or 1 -> 0
    corrupted[index] ^= 1

    return corrupted


def print_comparison(original, corrupted):
    print("Original : ", original)
    print("Corrupted: ", corrupted)

    for i, (a, b) in enumerate(zip(original, corrupted), start=1):
        if a != b:
            print(f"Error injected at bit position: {i}")


# --------------------------------------------------
# TEST
# --------------------------------------------------

original = [0, 1, 1, 0, 1, 1, 1]

error_position = 5

corrupted = inject_single_bit_error(
    original,
    error_position
)

print_comparison(original, corrupted)