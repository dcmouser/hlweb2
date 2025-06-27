# functions for stable random number hashing


# thanks to chatgpt for this
# give me a python function that takes an inclusive range, and a key string, and uses a Feistel network to give a pseudo random number within the range,  even when the domain size is not a power of two and the salt/key is not coprime.

import hashlib
import struct




def feistel_prp(index, domain_size, key, rounds=4):
    """Feistel-based PRP over non-power-of-two domain."""
    assert 0 <= index < domain_size
    n = domain_size.bit_length()
    half_bits = n // 2
    mask = (1 << half_bits) - 1

    l = index >> half_bits
    r = index & mask

    for round in range(rounds):
        round_key = hashlib.sha256(f"{key}-{round}".encode()).digest()
        r_bytes = struct.pack(">I", r)
        f = int.from_bytes(hashlib.sha256(round_key + r_bytes).digest()[:4], 'big') & mask
        l, r = r, l ^ f

    return ((l << half_bits) | r) % domain_size



def feistelScramble(value, min_val, max_val, key, rounds=4):
    """Maps value in [min_val, max_val] to a pseudo-random permutation using a Feistel network."""
    assert min_val <= value <= max_val
    domain_size = max_val - min_val + 1
    index = value - min_val
    scrambled = feistel_prp(index, domain_size, key, rounds)
    return scrambled + min_val



def stringToFeistelRange(s, min_val, max_val, key, rounds=4):
    """
    Maps an arbitrary string `s` to a pseudo-random number in [min_val, max_val]
    using a Feistel permutation.
    """
    domain_size = max_val - min_val + 1
    # Hash the input string to a repeatable integer in a wide space
    if (True):
        hashed_bytes = hashlib.sha256((s + ':' + key).encode()).digest()
    else:
        hashed_bytes = hashlib.sha256((key + ':' + s).encode()).digest()
    #
    base_int = int.from_bytes(hashed_bytes, 'big') % domain_size
    scrambled = feistel_prp(base_int, domain_size, key, rounds)
    return scrambled + min_val
