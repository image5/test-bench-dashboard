'use client';

import { TestBench, STATUS_COLORS, STATUS_LABELS } from '@/types';
import { formatTime, getTimeAgo } from '@/lib/utils';
import { useState } from 'react';

interface Props {
  bench: TestBench;
  isSelected: boolean;
  isEditMode: boolean;
  onEdit: () => void;
  onDelete: () => void;
  onSetMaintenance: (data: { isUnderMaintenance: boolean; reason?: string; operator?: string }) => void;
}

export default function BenchCard({
  bench,
  isSelected,
  isEditMode,
  onEdit,
  onDelete,
  onSetMaintenance,
}: Props) {
  const [showMenu, setShowMenu] = useState(false);
  const [showMaintenanceDialog, setShowMaintenanceDialog] = useState(false);
  const [maintenanceReason, setMaintenanceReason] = useState('');
  const [maintenanceOperator, setMaintenanceOperator] = useState('');
  
  const statusColor = STATUS_COLORS[bench.status.state];
  const statusLabel = STATUS_LABELS[bench.status.state];
  const typeInfo = bench.typeInfo;
  
  const handleSetMaintenance = () => {
    if (bench.maintenance.isUnderMaintenance) {
      // 退出维护
      onSetMaintenance({ isUnderMaintenance: false });
    } else {
      // 进入维护
      setShowMaintenanceDialog(true);
    }
    setShowMenu(false);
  };
  
  const confirmMaintenance = () => {
    onSetMaintenance({
      isUnderMaintenance: true,
      reason: maintenanceReason || '例行维护',
      operator: maintenanceOperator || '管理员',
    });
    setShowMaintenanceDialog(false);
    setMaintenanceReason('');
    setMaintenanceOperator('');
  };

  return (
    <>
      <div
        className={`bench-card relative overflow-hidden ${isSelected ? 'selected' : ''} ${
          bench.alarm.hasAlarm ? 'ring-2 ring-red-500 animate-pulse' : ''
        }`}
        style={{
          borderLeft: `3px solid ${statusColor}`,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(240,249,255,0.9) 100%)',
          boxShadow: isSelected 
            ? `0 0 0 1px ${statusColor}40, 0 4px 12px ${statusColor}20, inset 0 1px 0 rgba(255,255,255,0.8)`
            : '0 2px 8px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.8)',
        }}
      >
        {/* 科技感装饰线条 */}
        <div className="absolute top-0 right-0 w-16 h-16 opacity-5">
          <div className="absolute top-2 right-2 w-12 h-0.5 bg-current rotate-45"></div>
          <div className="absolute top-4 right-4 w-8 h-0.5 bg-current rotate-45"></div>
          <div className="absolute top-6 right-6 w-4 h-0.5 bg-current rotate-45"></div>
        </div>
        
        {/* 头部 - 类型图标和名称 */}
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5">
            <span className="text-lg">{typeInfo?.icon || '📦'}</span>
            <span className="font-semibold text-gray-800 text-sm">{bench.name}</span>
          </div>
          
          {/* 状态指示器 - 科技感设计 */}
          <div
            className="px-2 py-0.5 rounded text-[10px] font-medium text-white relative overflow-hidden"
            style={{ 
              backgroundColor: statusColor,
              boxShadow: `0 0 8px ${statusColor}60`
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
            {statusLabel}
          </div>
        </div>
        
        {/* 网络信息 */}
        <div className="text-[10px] text-gray-500 mb-0.5 flex items-center gap-1">
          <span className="opacity-60">🌐</span>
          <span className="font-mono">{bench.network.ip}:{bench.network.port}</span>
        </div>
        
        {/* 当前任务 */}
        {bench.status.currentTask && (
          <div className="text-[10px] text-gray-600 mb-0.5 truncate flex items-center gap-1">
            <span className="opacity-60">📋</span>
            <span>{bench.status.currentTask}</span>
          </div>
        )}
        
        {/* 心跳时间 */}
        <div className="text-[10px] text-gray-400 flex items-center gap-1">
          <span className="opacity-60">💓</span>
          <span>{getTimeAgo(bench.status.lastHeartbeat)}</span>
        </div>
        
        {/* 告警信息 */}
        {bench.alarm.hasAlarm && (
          <div className="mt-1.5 p-1 bg-red-50 border border-red-200 rounded text-[10px] text-red-600 flex items-start gap-1">
            <span>⚠️</span>
            <span>{bench.alarm.message}</span>
          </div>
        )}
        
        {/* 维护信息 */}
        {bench.maintenance.isUnderMaintenance && (
          <div className="mt-1.5 p-1 bg-yellow-50 border border-yellow-200 rounded text-[10px] text-yellow-700 flex items-start gap-1">
            <span>🔧</span>
            <span>维护中: {bench.maintenance.reason}</span>
          </div>
        )}
        
        {/* 编辑模式下的菜单按钮 */}
        {isEditMode && (
          <div className="mt-2 pt-2 border-t flex justify-end">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="text-gray-400 hover:text-gray-600 px-2"
            >
              ⋯
            </button>
            
            {showMenu && (
              <div className="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border py-1 z-50 min-w-[120px]">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit();
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-3 py-1.5 text-sm hover:bg-gray-100"
                >
                  ✏️ 编辑
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSetMaintenance();
                  }}
                  className="w-full text-left px-3 py-1.5 text-sm hover:bg-gray-100"
                >
                  🔧 {bench.maintenance.isUnderMaintenance ? '退出维护' : '设为维护'}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
                >
                  🗑️ 删除
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* 维护对话框 */}
      {showMaintenanceDialog && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowMaintenanceDialog(false)}
        >
          <div
            className="bg-white rounded-lg p-6 w-80"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="font-bold text-lg mb-4">设置维护状态</h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-600 mb-1">维护原因</label>
                <input
                  type="text"
                  value={maintenanceReason}
                  onChange={(e) => setMaintenanceReason(e.target.value)}
                  placeholder="例: 设备检修"
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-600 mb-1">维护人员</label>
                <input
                  type="text"
                  value={maintenanceOperator}
                  onChange={(e) => setMaintenanceOperator(e.target.value)}
                  placeholder="例: 张工"
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>
            </div>
            
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowMaintenanceDialog(false)}
                className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
              >
                取消
              </button>
              <button
                onClick={confirmMaintenance}
                className="px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600"
              >
                确认
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
