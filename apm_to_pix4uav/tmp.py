#! /usr/bin/python

import bisect

def spread_duplicates(seq):
    '''Spread duplicate seqtamps so that they have different values.'''

    dup = dict()
    seen = set()
    for t in seq:
        if t in seen:
            if not dup.has_key(t):
                dup[t] = 1
            else:
                dup[t] += 1
        else:
            seen.add(t)
    unique = list(seen)
    new_seq = list(seq)
    for d in sorted(dup.keys()):
        n = dup[d] + 1
        i0 = seq.index(d)
        t0 = seq[i0]
        i1 = i0 + n
        if i1 >= len(seq):
            t1 = seq[-1] + 1
        else:
            t1 = seq[i1]
        delta = 1.0 * (t1 - t0) / n
        for i in range(n - 1):
            new_seq[i0 + i + 1] = seq[i0 + i + 1] + delta * (i + 1)

    return new_seq

if __name__ == '__main__':

    with open('tmp.txt', 'rt') as fp:
        times = [int(t) for t in fp.readlines()]
        times = spread_duplicates(times)



