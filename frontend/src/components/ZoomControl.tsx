'use client';

import { useStore } from '@/store';

export default function ZoomControl() {
  const { zoom, setZoom, showGrid, setShowGrid, gridSnap, setGridSnap } = useStore();

  const handleZoomIn = () => setZoom(zoom + 0.1);
  const handleZoomOut = () => setZoom(zoom - 0.1);
  const handleZoomReset = () => setZoom(1);

  return (
    <div className="absolute bottom-4 right-4 flex flex-col gap-2 bg-white rounded-lg shadow-lg p-2">
      <div className="flex items-center gap-1">
        <button
          onClick={handleZoomOut}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-100 text-lg font-bold"
          title="缩小"
        >
          −
        </button>
        <span className="w-12 text-center text-sm font-medium">
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={handleZoomIn}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-100 text-lg font-bold"
          title="放大"
        >
          +
        </button>
        <button
          onClick={handleZoomReset}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-gray-100 text-sm"
          title="重置缩放"
        >
          ⟲
        </button>
      </div>

      <div className="border-t pt-2 flex flex-col gap-1">
        <button
          onClick={() => setShowGrid(!showGrid)}
          className={`w-full px-2 py-1 text-xs rounded ${
            showGrid ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
          }`}
        >
          {showGrid ? '📐 隐藏网格' : '📐 显示网格'}
        </button>
        <button
          onClick={() => setGridSnap(!gridSnap)}
          className={`w-full px-2 py-1 text-xs rounded ${
            gridSnap ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
          }`}
        >
          {gridSnap ? '🧲 吸附开启' : '🧲 吸附关闭'}
        </button>
      </div>
    </div>
  );
}
