'use client';

import { useState, useRef, useCallback } from 'react';
import { useStore } from '@/store';
import { benchesApi } from '@/lib/api';
import BenchCard from './BenchCard';
import AddBenchDialog from './AddBenchDialog';
import EditBenchDialog from './EditBenchDialog';
import { TestBench, BenchType, BENCH_TYPE_CONFIGS } from '@/types';

export default function Dashboard() {
  const {
    benches,
    currentLaboratoryId,
    isEditMode,
    showGrid,
    zoom,
    selectedBenchId,
    selectBench,
    updateBench,
    addBench,
    removeBench,
  } = useStore();
  
  const canvasRef = useRef<HTMLDivElement>(null);
  const [draggedBenchId, setDraggedBenchId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newBenchType, setNewBenchType] = useState<BenchType | null>(null);
  const [newBenchPosition, setNewBenchPosition] = useState({ x: 0, y: 0 });
  const [editingBench, setEditingBench] = useState<TestBench | null>(null);
  
  // 过滤当前实验室的台架
  const filteredBenches = currentLaboratoryId
    ? benches.filter((b) => b.laboratoryId === currentLaboratoryId)
    : benches;
  
  // 处理拖拽开始
  const handleDragStart = useCallback((e: React.DragEvent, benchId: string) => {
    if (!isEditMode) return;
    
    const bench = benches.find((b) => b.id === benchId);
    if (!bench) return;
    
    setDraggedBenchId(benchId);
    setDragOffset({
      x: e.clientX - bench.position.x * zoom,
      y: e.clientY - bench.position.y * zoom,
    });
    
    e.dataTransfer.effectAllowed = 'move';
  }, [isEditMode, benches, zoom]);
  
  // 处理拖拽移动
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    
    if (!draggedBenchId || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - dragOffset.x) / zoom;
    const y = (e.clientY - rect.top - dragOffset.y) / zoom;
    
    // 更新本地状态（实时反馈）
    updateBench(draggedBenchId, {
      position: { x: Math.max(0, x), y: Math.max(0, y) },
    });
  }, [draggedBenchId, dragOffset, zoom, updateBench]);
  
  // 处理拖拽结束
  const handleDragEnd = useCallback(async () => {
    if (!draggedBenchId) return;
    
    const bench = benches.find((b) => b.id === draggedBenchId);
    if (bench) {
      // 保存到服务器
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
  
  // 处理从侧边栏拖入新台架
  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    
    const benchType = e.dataTransfer.getData('benchType') as BenchType;
    if (!benchType || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom;
    const y = (e.clientY - rect.top) / zoom;
    
    // 打开添加对话框
    setNewBenchType(benchType);
    setNewBenchPosition({ x, y });
    setShowAddDialog(true);
  }, [zoom]);
  
  // 处理添加台架
  const handleAddBench = async (data: {
    name: string;
    ipAddress: string;
    port: number;
  }) => {
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
  
  // 处理删除台架
  const handleDeleteBench = async (benchId: string) => {
    if (!confirm('确定要删除此台架吗？')) return;
    
    try {
      await benchesApi.delete(benchId);
      removeBench(benchId);
    } catch (error) {
      console.error('删除台架失败:', error);
    }
  };
  
  // 处理设置维护
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
      className={`flex-1 relative overflow-hidden ${
        showGrid ? 'dashboard-canvas' : 'bg-gray-200'
      }`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => selectBench(null)}
      style={{
        backgroundImage: showGrid ? undefined : 'none',
        backgroundSize: `${40 * zoom}px ${40 * zoom}px`,
      }}
    >
      {/* 台架卡片 */}
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
      
      {/* 空状态提示 */}
      {filteredBenches.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <div className="text-6xl mb-4">🏭</div>
            <div className="text-xl">暂无台架</div>
            {isEditMode && (
              <div className="text-sm mt-2">
                从左侧拖拽台架到此处添加
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* 添加台架对话框 */}
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
      
      {/* 编辑台架对话框 */}
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
