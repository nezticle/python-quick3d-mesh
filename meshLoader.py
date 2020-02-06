import sys
import struct

class Mesh:
    class MeshDataHeader:
        fileId = 0
        fileVersion = 0
        headerFlags = 0
        sizeInBytes = 0
        #def loadMeshDataHeader(self, inputFile, offset):
        def isValid(self):
            return self.fileId == 3365961549 and self.fileVersion == 3
        def save(self):
            outputBuffer = struct.pack("<I", self.fileId)
            outputBuffer += struct.pack("<H", self.fileVersion)
            outputBuffer += struct.pack("<H", self.headerFlags)
            outputBuffer += struct.pack("<I", self.sizeInBytes)
            return outputBuffer, 12

    class MeshOffsetTracker:
        startOffset = 0
        byteCounter = 0
        def __init__(self, startOffset):
            self.startOffset = startOffset
        def offset(self):
            return self.startOffset + self.byteCounter
        def alignedAdvance(self, advanceAmount):
            self.advance(advanceAmount);
            alignmentAmount = 4 - (self.byteCounter % 4)
            self.byteCounter += alignmentAmount
        def advance(self, advanceAmount):
            self.byteCounter += advanceAmount

    class VertexBufferEntry:
        componentType = 0
        numComponents = 0
        firstItemOffset = 0
        name = ""

    class VertexBuffer:
        stride = 0
        entires = []
        data = []  

    class IndexBuffer:
        componentType = 0
        data = []

    class MeshSubset:
        class MeshBounds:
            minimum = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            maximum = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        count = 0
        offset = 0
        bounds = MeshBounds()
        name = ""

    class Joint:
        jointId = 0
        parentId = 0
        invBindPos = [1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1]
        localToGlobalBoneSpace = [1, 0, 0, 0,
                                0, 1, 0, 0,
                                0, 0, 1, 0,
                                0, 0, 0, 1]

    meshInfo = MeshDataHeader()
    vertexBuffer = VertexBuffer()
    indexBuffer = IndexBuffer()
    subsets = []
    joints = []  
    def loadMesh(self, inputFile, offset):
        try:
            with open(inputFile, "rb") as meshFile:
                meshFile.seek(offset)
                # Read the mesh file header
                self.meshInfo.fileId, = struct.unpack("<I", meshFile.read(4))
                self.meshInfo.fileVersion, = struct.unpack("<H", meshFile.read(2))
                self.meshInfo.headerFlags, = struct.unpack("<H", meshFile.read(2))
                self.meshInfo.sizeInBytes, = struct.unpack("<I", meshFile.read(4))

                if not self.meshInfo.isValid():
                    # not valid mesh data
                    meshFile.close()
                    print("File does not contain valid mesh data:", inputFile)
                    return
                # Offset Tracker starts after MeshHeaderData
                offsetTracker = self.MeshOffsetTracker(offset + 12)
                meshFile.seek(offsetTracker.offset())
                # Vertex Buffer
                vertexBufferEntriesOffset, = struct.unpack("<I", meshFile.read(4))
                vertexBufferEntriesSize, = struct.unpack("<I", meshFile.read(4))
                self.vertexBuffer.stride, = struct.unpack("<I", meshFile.read(4))
                vertexBufferDataOffset, = struct.unpack("<I", meshFile.read(4))
                vertexBufferDataSize, = struct.unpack("<I", meshFile.read(4))
                # Index Buffer
                self.indexBuffer.componentType, = struct.unpack("<I", meshFile.read(4))
                indexBufferDataOffset, = struct.unpack("<I", meshFile.read(4))
                indexBufferDataSize, = struct.unpack("<I", meshFile.read(4))
                # Subsets
                subsetsOffsets, = struct.unpack("<I", meshFile.read(4))
                subsetsSize, = struct.unpack("<I", meshFile.read(4))
                # Joints
                jointsOffsets, = struct.unpack("<I", meshFile.read(4))
                jointsSize, = struct.unpack("<I", meshFile.read(4))

                self.drawMode, = struct.unpack("<I", meshFile.read(4))
                self.winding, = struct.unpack("<I", meshFile.read(4))
                # advance offset tracker by sizeof Mesh struct
                offsetTracker.advance(56)
                # Vertex Buffer entries
                entriesByteSize = 0
                for entryIndex in range(vertexBufferEntriesSize):
                    vertexBufferEntry = self.VertexBufferEntry()
                    nameOffset, = struct.unpack("<I", meshFile.read(4))
                    vertexBufferEntry.componentType, = struct.unpack("<I", meshFile.read(4))
                    vertexBufferEntry.numComponents, = struct.unpack("<I", meshFile.read(4))
                    vertexBufferEntry.firstItemOffset, = struct.unpack("<I", meshFile.read(4));
                    entriesByteSize += 16
                    self.vertexBuffer.entires.append(vertexBufferEntry)
                # align after reading entires
                offsetTracker.alignedAdvance(entriesByteSize);
                meshFile.seek(offsetTracker.offset())
                for entry in self.vertexBuffer.entires:
                    nameLength, = struct.unpack("<I", meshFile.read(4))
                    offsetTracker.advance(4);
                    unpackFormat = "<" + str(nameLength) + "s"
                    entry.name = struct.unpack(unpackFormat, meshFile.read(nameLength))[0].decode('utf-8')
                    # get things aligned again if needed
                    offsetTracker.alignedAdvance(nameLength)
                    meshFile.seek(offsetTracker.offset())
                
                # Vertex Buffer Data
                self.vertexBuffer.data = meshFile.read(vertexBufferDataSize)
                offsetTracker.alignedAdvance(vertexBufferDataSize)
                meshFile.seek(offsetTracker.offset())

                # Index Buffer Data
                self.indexBuffer.data = meshFile.read(indexBufferDataSize)
                offsetTracker.alignedAdvance(indexBufferDataSize)
                meshFile.seek(offsetTracker.offset())

                # Subsets
                for subsetIndex in range(subsetsSize):
                    subset = self.MeshSubset()
                    subset.count, = struct.unpack("<I", meshFile.read(4))
                    subset.offset, = struct.unpack("<I", meshFile.read(4))
                    subset.bounds.minimum["x"], = struct.unpack("<f", meshFile.read(4))
                    subset.bounds.minimum["y"], = struct.unpack("<f", meshFile.read(4))
                    subset.bounds.minimum["z"], = struct.unpack("<f", meshFile.read(4))
                    subset.bounds.maximum["x"], = struct.unpack("<f", meshFile.read(4))
                    subset.bounds.maximum["y"], = struct.unpack("<f", meshFile.read(4))
                    subset.bounds.maximum["z"], = struct.unpack("<f", meshFile.read(4))
                    nameOffset, = struct.unpack("<I", meshFile.read(4))
                    nameLength, = struct.unpack("<I", meshFile.read(4))
                    offsetTracker.alignedAdvance(40)
                    meshFile.seek(offsetTracker.offset())
                    # then read subset name as char16_t
                    subset.name = meshFile.read(nameLength * 2).decode("utf_16_le")
                    offsetTracker.alignedAdvance(nameLength * 2)
                    meshFile.seek(offsetTracker.offset())
                    self.subsets.append(subset)

                # Joints
                for jointIndex in range(jointsSize):
                    joint = self.Joint()
                    joint.jointId, = struct.unpack("<I", meshFile.read(4))
                    joint.parentId, = struct.unpack("<I", meshFile.read(4))
                    for x in range(16):
                        joint.invBindPos[x], = struct.unpack("<f", meshFile.read(4))
                    for x in range(16):
                        joint.localToGlobalBoneSpace[x], = struct.unpack("<f", meshFile.read(4))
                    offsetTracker.alignedAdvance(136)
                    meshFile.seek(offsetTracker.offset())

                meshFile.close()
        except OSError:
            print("Could not open/read file:", inputFile)
        except: #handle other exceptions such as attribute errors
            print("Unexpected error:", sys.exc_info()[0])
    def writeMesh(self, outputFile):
        try:
            with open(outputFile, "wb") as meshFile:
                # write header placeholder
                header,headerSize = self.meshInfo.save()
                meshFile.write(header)
                offsetTracker = self.MeshOffsetTracker(headerSize)
                # write Mesh metadata
                meshMetaData = bytearray()
                meshMetaData += struct.pack("<I", 0)
                meshMetaData += struct.pack("<I", len(self.vertexBuffer.entires))
                meshMetaData += struct.pack("<I", self.vertexBuffer.stride)
                meshMetaData += struct.pack("<I", 0)
                meshMetaData += struct.pack("<I", len(self.vertexBuffer.data))

                meshMetaData += struct.pack("<I", self.indexBuffer.componentType)
                meshMetaData += struct.pack("<I", 0)
                meshMetaData += struct.pack("<I", len(self.indexBuffer.data))

                meshMetaData += struct.pack("<I", 0)
                meshMetaData += struct.pack("<I", len(self.subsets))

                meshMetaData += struct.pack("<I", 0)
                meshMetaData += struct.pack("<I", len(self.joints))

                meshMetaData += struct.pack("<I", self.drawMode)
                meshMetaData += struct.pack("<I", self.winding)

                meshFile.write(meshMetaData)
                offsetTracker.advance(56)

                # Vertex Buffer Entries
                entriesData = bytearray()
                for entry in self.vertexBuffer.entires:
                    entriesData += struct.pack("<I", 0)
                    entriesData += struct.pack("<I", entry.componentType)
                    entriesData += struct.pack("<I", entry.numComponents)
                    entriesData += struct.pack("<I", entry.firstItemOffset)
                entriesData += bytearray(4) # alignment
                offsetTracker.advance(len(entriesData))
                meshFile.write(entriesData)

                # Vertex Buffer Entry Names
                entryNameData = bytearray()
                for entry in self.vertexBuffer.entires:
                    entryNameData += struct.pack("<I", len(entry.name))
                    entryNameData += bytearray(entry.name, 'utf-8')
                    entryNameData += bytearray(4 - len(entry.name) % 4) # alignment
                meshFile.write(entryNameData)
                offsetTracker.advance(len(entryNameData))
                meshFile.close()
        except OSError:
            print("Could not open/create file:", outputFile)
        except: #handle other exceptions such as attribute errors
            print("Unexpected error:", sys.exc_info()[0])

class MultiMeshInfo:
    fileId = 0
    fileVersion = 0
    meshEntries = {}

    def loadMultiMeshInfo(self, inputFile):
        try:
            with open(inputFile, "rb") as meshFile:
                # Look for a valid MultiMesh footer
                meshFile.seek(-16, 2) #16 bytes from the end of the file
                self.fileId, = struct.unpack("<I", meshFile.read(4))
                self.fileVersion, = struct.unpack("<I", meshFile.read(4))
                meshFile.seek(4, 1)
                #entriesOffset, = struct.unpack("<I", meshFile.read(4))
                entriesSize, = struct.unpack("<I", meshFile.read(4))

                if self.isValid():
                    # Look for entries
                    for i in range(entriesSize):
                        meshFile.seek(-16 + (-16 * entriesSize) + (16 * i), 2)
                        meshOffset, = struct.unpack("<Q", meshFile.read(8))
                        meshId, = struct.unpack("<I", meshFile.read(4))
                        self.meshEntries[meshId] = meshOffset
                
                meshFile.close()
        except OSError:
            print("Could not open/read file:", inputFile)
        except: #handle other exceptions such as attribute errors
            print("Unexpected error:", sys.exc_info()[0])

    def isValid(self):
        return self.fileId == 555777497 and self.fileVersion == 1

def main(argv):
    inputfile = ''

    if len(argv) == 0:
        print ("meshLoader.py <inputfile>")
        sys.exit(2)

    inputfile = argv[0]
    print ('Input file is ', inputfile)

    # Get the Multmesh Data for the inputfile
    multiMeshInfo = MultiMeshInfo()
    multiMeshInfo.loadMultiMeshInfo(inputfile);

    meshes = {}
    if multiMeshInfo.isValid() and len(multiMeshInfo.meshEntries) > 0:
        # This is indeed a MultiMesh file
        for entryId in multiMeshInfo.meshEntries.keys():
            offset = multiMeshInfo.meshEntries[entryId]
            mesh = Mesh()
            mesh.loadMesh(inputfile, offset)
            mesh.writeMesh("./test.mesh")
            meshes[entryId] = mesh
    else:
        # This still may be a regular mesh file
        mesh = Mesh()
        mesh.loadMesh(inputfile, 0)
        meshes[0] = mesh

if __name__ == "__main__":
   main(sys.argv[1:])