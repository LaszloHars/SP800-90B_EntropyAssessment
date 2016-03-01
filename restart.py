# DRAFT NIST SP 800-90B (January 2016) Section 3.1.4 
#
# Estimating the Min-Entropy of non-IID Sources
#
#
# NOTE: this software is made available with no guarantee - implied or otherwise -
# of correctness or completeness.
#
# Updated by Kerry McKay
# kerry.mckay@nist.gov


import sys
import time
import math

from util90b import get_parser, to_dataset, get_z
from mostCommonValue import most_common_restart


##################
# main program
##################
if __name__ == '__main__':

    # get command line arguments
    args = get_parser('restart').parse_args()
    datafile = args.datafile
    bits_per_symbol = int(args.bits_per_symbol)
    verbose = bool(args.verbose)
    H_I = float(args.H_I)

    with open(datafile, 'rb') as file:
        # Read in raw bytes and convert to list of output symbols
        bytes_in = bytearray(file.read())
        dataset = to_dataset(bytes_in, bits_per_symbol)
        k = len(set(dataset))
        if verbose:
            # print file and dataset details
            print ("Read in file %s, %d bytes long." % (datafile, len(bytes_in)))
            print ("Dataset: %d %d-bit symbols, %d symbols in alphabet." % (len(dataset), bits_per_symbol, k))
            print ("Output symbol values: min = %d, max = %d" % (min(dataset), max(dataset)))

        # max min-entropy is -log_2(1/k)
        minEntropy = float(math.log(k,2))


        assert len(dataset) == 1000000

    
        # 1. Let alpha be 0.01/(2000k), where k is the sample size
        alpha = 0.01/(2000*k)
        print "alpha:", alpha
        print "Z at alpha/2:", alpha/2
        print "looking for %f  CI" % (1-alpha)

        # 2. For each row of the matrix, find the frequency of the most
        #    common sample value. Let F_R be the maximum.
        if verbose:
            print "\nRunning sanity check on row dataset:"
        f = [0 for i in range(1000)]
        for i in range(1000):
            f[i] = most_common_restart(dataset[i*1000:(i+1)*1000])
        F_R = max(f)
        print "F_R:", F_R
            
        # 3. repeat the sample process for the column matrix. Let F_C be the
        #    maximum.
        if verbose:
            print "Running sanity check on column dataset:"
        f = [0 for i in range(1000)]
        for i in range(1000):
            column = []
            for j in range(1000):
                column.append(dataset[j*1000+i])
            f[i] = most_common_restart(column)
        F_C = max(f)
        print "F_C:", F_C

        # 4. Let F = max(F_R, F_C)
        F = max(F_R, F_C)

        # 5. Let p = 2**-H_I. Find the upper bound U of the (1-alpha)% confidence
        #    interval
        p = math.pow(2, -H_I)
        Z = get_z(alpha) #TO DO: find z
        print "z:",Z
        U = 1000*p + Z*math.sqrt(1000*p*(1-p))
        print "U:",U

        # 6. If F is greater than U, the test fails
        if F > U:
            print "Failed the restart tests"
            print "*** Validation failed. No entropy estimate awarded."
        else:
            print "Passed the restart tests"
            print "*** Final entropy estimate:", H_I

        

