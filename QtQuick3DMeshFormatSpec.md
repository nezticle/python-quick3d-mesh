# Qt Quick 3D Mesh Format Specification

## MeshDataHeader (12 bytes)
- UInt32 fileId | 3365961549U
- UInt16 fileVersion | 3
- UInt16 headerFlags 
- UInt32 sizeInBytes

## Mesh (56 bytes)
- VertexBuffer vertexBuffer
    - UInt32 entriesOffset // internal use really
    - UInt32 entriesSize
    - UInt32 stride
    - UInt32 dataOffset // internal use really
    - UInt32 dataSize
- IndexBuffer indexBuffer
    - UInt32 componentType
    - UInt32 dataOffset // internal use really
    - UInt32 dataSize
- UInt32 subsetsOffset // internal use really
- UInt32 subsetsSize
- UInt32 jointsOffset // internal use really
- UInt32 jointsSize
- UInt32 drawMode
- UInt32 winding

## Vertex Buffer Entries [VertexBuffer::entriesSize]
- UInt32 nameOffset // not used...
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

## Subsets [Mesh::subsetsSize]
- UInt32 count
- UInt32 offset
- Bounds3 bounds
   - vec3<float32> minimum
   - vec3<float32> maximum
- UInt32 nameOffset
- UInt32 nameSize // char16_t
- optional padding (so we are 4 byte aligned)
- char16[nameSize]
- optional padding (so we are 4 byte aligned)
- ...

## Joint [Mesh::joinsSize] (136 bytes)
- UInt32 jointID
- UInt32 parentID
- float32[16] invBindPose
- float32[16] localToGlobalBoneSpace
- optional padding (so we are 4 byte aligned)
- ...


## MeshMultiEntry (16 bytes) [MultiMeshFooter::entriesSize]
- UInt64 meshOffset
- UInt32 meshId
- UInt32 padding // not used (literally padding)

## MultiMeshFooter (16 bytes)
- UInt32 fileId | 555777497U
- UInt32 version | 1
- UInt32 entriesOffset // internal use really
- UInt32 entriesSize
