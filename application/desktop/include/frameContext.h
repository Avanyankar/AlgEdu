#pragma once
#include <d3d12.h>

class FrameContext
{
 public:
     ID3D12CommandAllocator* CommandAllocator;
     UINT64 FenceValue;
     FrameContext();
};
