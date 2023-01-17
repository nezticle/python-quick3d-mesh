# Qt Quick 3D Mesh Format Specification

Qt Quick 3D Mesh files are a binary format for storing 3D geometry. Mesh files can contain multiple Meshes, each of which has their own vertex and index buffers, as well as subset views into each.  The container format is specified by the MultiMeshFooter which can be accessed by reading the last 16 bytes of the .mesh file.  With this you can get the number of Meshes contained in the file, which by reading back 16 bytes before the MultiMeshFooter for each mesh available you can get the offsets for each mesh in the file.  Then each mesh can be parsed at those offsets by reading the first 12 bytes at that offset containing the MeshDataHeader.

An important note to remember is that most of the values with offset in the name are misleading.  MultiMeshEntry::meshOffset is the only field you can trust, all other offset fields are garbage values that would get filled in later by the parser, and is an implementation detail that leaked into the file format.  So rather than using any data that might be in those offsets, either skip them, or ignore any value after reading them in.  The *real* offset of the value will be specified by this spec.  The offsets will be at certain locations in the file based on the order of the structs below.

Another important point is expected padding.  Everything needs to be 4 byte aligned, and for the most part it is already (with the exception of some string data). But also do to some weird implementation details (READ: Bugs) sometimes you just need to throw in an extra 4 bytes for good measurer.  So note after reading all VertexBufferEntries (not between each one though), you need to add 4 bytes of padding before parsing/writing the name strings.  The same thing is true when reading the subset data.  Read all subsets together (they will be 4 byte aligned already) then after reading all of them, add 4 bytes of padding before reading/writing the subset names.  

Endianess is little endian for everything.  Floating point values are all single precision 32bit floats.  Some strings are UTF-8, some are UTF_16_LE... not sure why, but it is what is.

## Versions

There are two levels of versioning in the Mesh file format.  The container format is separate from the mesh files contained within that container.  The container only has 1 version which is 1.

For the Mesh files appearing in the MultiMesh container, version is significant.  Here is an overview:

### Version 1
Unsupported version unique to Nvidia Drive Design, Not documented

### Version 2
Unsupported version unique to Nvidia Drive Design and early releases of Qt 3D Studio, Not documented

### Version 3
This is the minimum supported version of the Mesh file format with Qt Quick 3D, and the last compatible version that Qt 3D Studio can produce.

### Version 4
All of the dataOffset fields should now contain 0

### Version 5
Added lightmapWidth and lightmapHeight to Subsets

### Version 6
Added LOD levels to subsets


## MeshDataHeader (12 bytes)
- UInt32 fileId | 3365961549U
- UInt16 fileVersion | 3
- UInt16 headerFlags 
- UInt32 sizeInBytes

## Mesh (56 bytes)
- VertexBuffer vertexBuffer
    - UInt32 entriesOffset // ignore this value
    - UInt32 entriesSize
    - UInt32 stride
    - UInt32 dataOffset // ignore this value
    - UInt32 dataSize
- IndexBuffer indexBuffer
    - UInt32 componentType
    - UInt32 dataOffset // ignore this value
    - UInt32 dataSize
- UInt32 subsetsOffset // ignore this value
- UInt32 subsetsSize
- UInt32 jointsOffset // ignore this value
- UInt32 jointsSize
- UInt32 drawMode
- UInt32 winding

## Vertex Buffer Entries [VertexBuffer::entriesSize]
- UInt32 nameOffset // ignore this value
- UInt32 componentType
- UInt32 numComponents
- UInt32 firstItemOffset
- ...
- 4bytes of alignment padding

## Vertex Buffer Entry Names [VertexBuffer::entriesSize]
- UInt32 nameLength
- char[nameLength] name
- optional padding (so we are 4 byte aligned)
- ...

## Vertex Buffer Data
- UInt8[VertexBuffer::dataSize]
- optional padding (so we are 4 byte aligned)

## Index Buffer Data
- UInt8[IndexBuffer::dataSize]
- optional padding (so we are 4 byte aligned)

## Subsets [Mesh::subsetsSize] (40 bytes)
- UInt32 count
- UInt32 offset
- Bounds3 bounds
   - vec3<float32> minimum
   - vec3<float32> maximum
- UInt32 nameOffset // ignore this value
- UInt32 nameSize // char16_t letter count, not byte count so multiply x2
...
- 4bytes of alignment padding

## Subsets_V5[Mesh::subsetsSize] (48 bytes)
- UInt32 count
- UInt32 offset
- Bounds3 bounds
   - vec3<float32> minimum
   - vec3<float32> maximum
- UInt32 nameOffset // ignore this value
- UInt32 nameSize // char16_t letter count, not byte count so multiply x2
- UInt32 lightmapSizeHintWidth
- UInt32 lightmapSizeHintHeight
...
- 4bytes of alignment padding

## Subsets_V6[Mesh::subsetsSize] (52 bytes)
- UInt32 count
- UInt32 offset
- Bounds3 bounds
   - vec3<float32> minimum
   - vec3<float32> maximum
- UInt32 nameOffset // ignore this value
- UInt32 nameSize // char16_t letter count, not byte count so multiply x2
- UInt32 lightmapSizeHintWidth
- UInt32 lightmapSizeHintHeight
- UInt32 lodCount
...
- 4bytes of alignment padding

## Subset Names [Mesh::subsetSize]
Names are stored after subsets array in order of subset based on padded length
- sizeof(char16_t) * subset.nameSize
- optional padding (so we are 4 byte aligned)

## LODs  (12 bytes)
Lods are stored after subset names in order of subsets
- UInt32 count // length of lod indexes
- UInt32 offset // start of lod indexes
- float32 distance // ideal distance metric for usage

## Joint [Mesh::joinsSize] (136 bytes)
- UInt32 jointID
- UInt32 parentID
- float32[16] invBindPose
- float32[16] localToGlobalBoneSpace
- optional padding (so we are 4 byte aligned)
- ...


## MeshMultiEntry (16 bytes) [MultiMeshFooter::entriesSize]
- UInt64 meshOffset // only offset you can trust (seek to this to get the mesh data)
- UInt32 meshId
- UInt32 padding // not used (literally padding)

## MultiMeshFooter (16 bytes)
- UInt32 fileId | 555777497U
- UInt32 version | 1
- UInt32 entriesOffset // ignore this value
- UInt32 entriesSize


# Enum values

## drawMode
1. Points
2. LineStrip
3. LineLoop
4. Lines
5. TriangleStrip
6. TriangleFan
7. Triangles
8. Patches

## componentType
1. Unsigned 8bit Int (size: 1)
2. Signed 8bit Int (size: 1)
3. Unsigned 16bit Int (size: 2)
4. Signed 16bit Int (size: 2)
5. Unsigned 32bit Int (size: 4)
6. Signed 32bit Int (size: 4)
7. Unsigned 64bit Int (size: 8)
8. Signed 64bit Int (size: 8)
9. 16bit Float (size: 2)
10. 32bit Float (size: 4)
11. 64bit Float (size: 8)

## winding
1. Clockwise
2. CounterClockwise

## vertex entry names
- attr_pos
- attr_norm
- attr_uv0
- attr_uv1
- attr_textan
- attr_binormal
- attr_joints
- attr_weights
- attr_colors

## semantic sizes
- Index 1
- Position 3
- Normal 3 
- TexCoord 2 
- Tangent 3
- Binormal 3
- Joint 4
- Weight 4
- Color 4
