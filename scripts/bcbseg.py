#!/usr/bin/env python3
# -*-coding:Utf-8 -*

import sys
import argparse

import tools.constants as cst
import tools.segment as seg

if len(sys.argv) < 3:
    print("You must provide at least the dimension of the image")
    print("and the anatomical image.")

dim = sys.argv[1]
anat = sys.argv[2]
# opt
mask = sys.argv[3]
nb_class = sys.argv[4]
out_pref = sys.argv[5]
priors = sys.argv[6]


def build_argparser():
    DESCRIPTION = "Convert tractograms (TCK -> TRK)."
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('anatomy', help='reference anatomy (.nii|.nii.gz.')
    p.add_argument('tractograms', metavar='tractogram', nargs="+",
                   help='list of tractograms (.tck).')
    p.add_argument('-f', '--force', action="store_true",
                   help='overwrite existing output files.')
    return p