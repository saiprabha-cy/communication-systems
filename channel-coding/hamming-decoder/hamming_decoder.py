def hamming_decode(bits):
    if len(bits) != 7:
        raise ValueError("Hamming(7,4) requires exactly 7 bits")

    # Convert to 1-based indexing
    b = [0] + bits

    # Parity checks
    s1 = b[1] ^ b[3] ^ b[5] ^ b[7]
    s2 = b[2] ^ b[3] ^ b[6] ^ b[7]
    s4 = b[4] ^ b[5] ^ b[6] ^ b[7]

    syndrome = s1 + (s2 << 1) + (s4 << 2)

    print(f"Syndrome = {syndrome}")

    # Correct single-bit error
    if syndrome != 0:
        print(f"Error detected at bit position {syndrome}")

        b[syndrome] ^= 1

        print("Error corrected")

    else:
        print("No error detected")

    # Extract data bits
    data = [
        b[3],
        b[5],
        b[6],
        b[7]
    ]

    return data


received = [0, 1, 1, 0, 1, 1, 1]

decoded = hamming_decode(received)

print("Decoded data:", decoded)