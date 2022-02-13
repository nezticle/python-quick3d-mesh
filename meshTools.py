#############################################################################
##
## Copyright (C) 2022 Andy Nichols <nezticle@gmail.com>
##
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
##
#############################################################################

import sys
from QtQuick3DMesh import MeshFile
from argparse import ArgumentParser

def main():

    parser = ArgumentParser(description='Utilities for Qt Quick 3D .mesh Files')
    modeGroup = parser.add_mutually_exclusive_group()
    parser.add_argument('inputFile', metavar='INPUT', help='Mesh file to load')
    parser.add_argument('outputFile', metavar='OUTPUT', help='Output mesh file')
    modeGroup.add_argument('--points', help='Convert Mesh to Points', action='store_true')
    modeGroup.add_argument('--lines', help='Convert Mesh to Lines', action='store_true')
    args = parser.parse_args()

    inputfile = args.inputFile
    outputFile = args.outputFile

    print ('Input file is ', inputfile)

    meshFile = MeshFile()
    meshFile.loadMeshFile(inputfile)

    # Preform actions
    if args.points:
        meshFile.convertToPointsPrimitive()
    elif args.lines:
        meshFile.convertToLinesPrimitive()


    # Save new File
    meshFile.saveMeshFile(outputFile)

    return 0

if __name__ == "__main__":
   sys.exit(main())