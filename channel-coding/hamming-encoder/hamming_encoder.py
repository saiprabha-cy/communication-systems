def hamming_encode(data):
    """
    Hamming(7,4) encoder

    Input:
        data = [D1, D2, D3, D4]

    Output:
        [P1, P2, D1, P4, D2, D3, D4]
    """

    if len(data) != 4:
        raise ValueError("Input must contain exactly 4 data bits")

    if any(bit not in (0, 1) for bit in data):
        raise ValueError("Data must contain only 0 or 1")

    d1, d2, d3, d4 = data

    # Calculate parity bits
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4

    codeword = [
        p1,
        p2,
        d1,
        p4,
        d2,
        d3,
        d4
    ]

    return codeword


# Test cases
test_data = [
    [1, 0, 1, 1],
    [1, 1, 0, 1],
    [0, 1, 1, 0]
]

for data in test_data:
    encoded = hamming_encode(data)

    print(f"Data:    {data}")
    print(f"Encoded: {encoded}")
    print()