#! /usr/bin/python

import bisect

def match(x, seqy, y_idx_lo=0, match_low_only=False):
    '''Find y closest to the value of a given x in a given set of y values.

    Returns (y, index of y in seqy)
    
    '''

    # Find closest match 
    idx = bisect.bisect_left(seqy, x, y_idx_lo)
    if idx == 0: # Corner case: lower bound 
        y_idx = idx

    elif idx > 0 and idx < len(seqy): # Common case: between
        if not match_low_only:
            y_idx_lo = idx - 1
            error = abs(seqy[idx] - x)
            error_lo = abs(seqy[y_idx_lo] - x)
            if error_lo < error:
                y_idx = y_idx_lo
            else:
                y_idx = idx
        else:
            y_idx = idx - 1

    else: # Corner case: upper bound
        y_idx = idx - 1

    y = seqy[y_idx]

    return (y, y_idx)

