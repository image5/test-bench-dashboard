'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useStore } from '@/store';
import { benchesApi } from '@/lib/api';
import BenchCard from './BenchCard';
import AddBenchDialog from './AddBenchDialog';
import EditBenchDialog from './EditBenchDialog';
import ZoomControl from './ZoomControl';
import { TestBench, BenchType, BENCH_TYPE_CONFIGS } from '@/types';

const GRID_SIZE = 40;

export default function Dashboard() {
  const {
    benches,
    currentLaboratoryId,
    isEditMode,
    showGrid,
    zoom,
    gridSnap,
    selectedBenchId,
    selectBench,
    updateBench,
    updateBenchPosition,
    addBench,
    removeBench,
    setZoom,
  } = useStore();

  const canvasRef = useRef<HTMLDivElement>(null);
  const [draggedBenchId, setDraggedBenchId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newBenchType, setNewBenchType] = useState<BenchType | null>(null);
  const [newBenchPosition, setNewBenchPosition] = useState({ x: 0, y: 0 });
  const [editingBench, setEditingBench] = useState<TestBench | null>(null);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  const filteredBenches = currentLaboratoryId
    ? benches.filter((b) => b.laboratoryId === currentLaboratoryId)
    : benches;

  const snapToGrid = useCallback(
    (value: number): number => {
      if (!gridSnap) return value;
      return Math.round(value / GRID_SIZE) * GRID_SIZE;
    },
    [gridSnap]
  );

  const handleWheel = useCallback(
    (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        setZoom(zoom + delta);
      }
    },
    [zoom, setZoom]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.addEventListener('wheel', handleWheel, { passive: false });
      return () => canvas.removeEventListener('wheel', handleWheel);
    }
  }, [handleWheel]);

  const handleDragStart = useCallback(
    (e: React.DragEvent, benchId: string) => {
      if (!isEditMode) return;

      const bench = benches.find((b) => b.id === benchId);
      if (!bench) return;

      setDraggedBenchId(benchId);
      setDragOffset({
        x: e.clientX - (bench.position.x * zoom + pan.x),
        y: e.clientY - (bench.position.y * zoom + pan.y),
      });

      e.dataTransfer.effectAllowed = 'move';
    },
    [isEditMode, benches, zoom, pan]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();

      if (!draggedBenchId || !canvasRef.current) return;

      const rect = canvasRef.current.getBoundingClientRect();
      let x = (e.clientX - rect.left - dragOffset.x - pan.x) / zoom;
      let y = (e.clientY - rect.top - dragOffset.y - pan.y) / zoom;

      x = snapToGrid(Math.max(0, x));
      y = snapToGrid(Math.max(0, y));

      updateBenchPosition(draggedBenchId, { x, y });
    },
    [draggedBenchId, dragOffset, zoom, pan, snapToGrid, updateBenchPosition]
  );

  const handleDragEnd = useCallback(async () => {
    if (!draggedBenchId) return;

    const bench = benches.find((b) => b.id === draggedBenchId);
    if (bench) {
      try {
        await benchesApi.updatePosition(
          draggedBenchId,
          bench.position.x,
          bench.position.y,
          bench.position.rotation
        );
      } catch (error) {
        console.error('保存位置失败:', error);
      }
    }

    setDraggedBenchId(null);
  }, [draggedBenchId, benches]);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();

      const benchType = e.dataTransfer.getData('benchType') as BenchType;
      if (!benchType || !canvasRef.current) return;

      const rect = canvasRef.current.getBoundingClientRect();
      let x = (e.clientX - rect.left - pan.x) / zoom;
      let y = (e.clientY - rect.top - pan.y) / zoom;

      x = snapToGrid(x);
      y = snapToGrid(y);

      setNewBenchType(benchType);
      setNewBenchPosition({ x, y });
      setShowAddDialog(true);
    },
    [zoom, pan, snapToGrid]
  );

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button === 1 || (e.button === 0 && e.altKey)) {
        setIsPanning(true);
        setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      }
    },
    [pan]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isPanning) {
        setPan({
          x: e.clientX - panStart.x,
          y: e.clientY - panStart.y,
        });
      }
    },
    [isPanning, panStart]
  );

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  const handleAddBench = async (data: { name: string; ipAddress: string; port: number }) => {
    if (!newBenchType) return;

    try {
      const newBench = await benchesApi.create({
        name: data.name,
        type: newBenchType,
        ipAddress: data.ipAddress,
        port: data.port,
        laboratoryId: currentLaboratoryId || undefined,
        positionX: newBenchPosition.x,
        positionY: newBenchPosition.y,
      });

      addBench(newBench);
      setShowAddDialog(false);
      setNewBenchType(null);
    } catch (error) {
      console.error('添加台架失败:', error);
      throw error;
    }
  };

  const handleDeleteBench = async (benchId: string) => {
    if (!confirm('确定要删除此台架吗？')) return;

    try {
      await benchesApi.delete(benchId);
      removeBench(benchId);
    } catch (error) {
      console.error('删除台架失败:', error);
    }
  };

  const handleSetMaintenance = async (
    benchId: string,
    data: { isUnderMaintenance: boolean; reason?: string; operator?: string }
  ) => {
    try {
      const updated = await benchesApi.setMaintenance(benchId, data);
      updateBench(benchId, updated);
    } catch (error) {
      console.error('设置维护状态失败:', error);
    }
  };

  return (
    <div
      ref={canvasRef}
      className={`flex-1 relative overflow-hidden cursor-grab ${
        isPanning ? 'cursor-grabbing' : ''
      } ${showGrid ? 'dashboard-canvas' : 'bg-gray-200'}`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => selectBench(null)}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{
        backgroundImage: showGrid
          ? `linear-gradient(to right, #e5e7eb 1px, transparent 1px),
             linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)`
          : 'none',
        backgroundSize: `${GRID_SIZE * zoom}px ${GRID_SIZE * zoom}px`,
        backgroundPosition: `${pan.x}px ${pan.y}px`,
      }}
    >
      <div
        className="absolute"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px)`,
        }}
      >
        {filteredBenches.map((bench) => (
          <div
            key={bench.id}
            draggable={isEditMode}
            onDragStart={(e) => handleDragStart(e, bench.id)}
            onDragEnd={handleDragEnd}
            onClick={(e) => {
              e.stopPropagation();
              selectBench(bench.id);
            }}
            onDoubleClick={() => setEditingBench(bench)}
            onContextMenu={(e) => {
              e.preventDefault();
              if (isEditMode) {
                handleDeleteBench(bench.id);
              }
            }}
            className="absolute"
            style={{
              left: bench.position.x * zoom,
              top: bench.position.y * zoom,
              transform: `scale(${zoom})`,
              transformOrigin: 'top left',
            }}
          >
            <BenchCard
              bench={bench}
              isSelected={selectedBenchId === bench.id}
              isEditMode={isEditMode}
              onEdit={() => setEditingBench(bench)}
              onDelete={() => handleDeleteBench(bench.id)}
              onSetMaintenance={(data) => handleSetMaintenance(bench.id, data)}
            />
          </div>
        ))}
      </div>

      {filteredBenches.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center text-gray-400">
            <div className="text-6xl mb-4">🏭</div>
            <div className="text-xl">暂无台架</div>
            {isEditMode && <div className="text-sm mt-2">从左侧拖拽台架到此处添加</div>}
          </div>
        </div>
      )}

      <ZoomControl />

      {showAddDialog && newBenchType && (
        <AddBenchDialog
          type={newBenchType}
          position={newBenchPosition}
          onAdd={handleAddBench}
          onClose={() => {
            setShowAddDialog(false);
            setNewBenchType(null);
          }}
        />
      )}

      {editingBench && (
        <EditBenchDialog
          bench={editingBench}
          onSave={async (data) => {
            try {
              const updated = await benchesApi.update(editingBench.id, data);
              updateBench(editingBench.id, updated);
              setEditingBench(null);
            } catch (error) {
              console.error('更新台架失败:', error);
              throw error;
            }
          }}
          onClose={() => setEditingBench(null)}
        />
      )}
    </div>
  );
}
