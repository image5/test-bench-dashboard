'use client';

import { useStore } from '@/store';
import { laboratoriesApi } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import { useState, useEffect } from 'react';
import ConfigManager from './ConfigManager';
import DashboardSelector from './DashboardSelector';
import { DashboardType } from '@/types/dashboard';

interface HeaderProps {
  currentDashboard?: DashboardType;
  onDashboardChange?: (type: DashboardType) => void;
}

export default function Header({ 
  currentDashboard = 'test-bench',
  onDashboardChange 
}: HeaderProps) {
  const {
    laboratories,
    currentLaboratoryId,
    setCurrentLaboratory,
    isEditMode,
    setEditMode,
    showGrid,
    setShowGrid,
    gridSnap,
    setGridSnap,
    statistics,
    zoom,
    setZoom,
  } = useStore();
  
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  
  useEffect(() => {
    setCurrentTime(new Date());
    
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const isTestBenchDashboard = currentDashboard === 'test-bench';

  return (
    <header className="bg-slate-800 text-white px-4 py-3 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-4">
        <DashboardSelector 
          currentDashboard={currentDashboard}
          onDashboardChange={onDashboardChange || (() => {})}
        />
        
        {isTestBenchDashboard && (
          <select
            value={currentLaboratoryId || ''}
            onChange={(e) => setCurrentLaboratory(e.target.value || null)}
            className="bg-slate-700 text-white px-3 py-1.5 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">全部实验室</option>
            {laboratories.map((lab) => (
              <option key={lab.id} value={lab.id}>
                {lab.name}
              </option>
            ))}
          </select>
        )}
      </div>
      
      {isTestBenchDashboard && statistics && (
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-gray-400">在线率:</span>
            <span className={`font-bold ${statistics.onlineRate >= 80 ? 'text-green-400' : 'text-yellow-400'}`}>
              {statistics.onlineRate}%
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              运行: {statistics.runningCount}
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-gray-500"></span>
              离线: {statistics.offlineCount}
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
              维护: {statistics.maintenanceCount}
            </span>
            {statistics.alarmCount > 0 && (
              <span className="flex items-center gap-1 text-red-400">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                告警: {statistics.alarmCount}
              </span>
            )}
          </div>
        </div>
      )}
      
      <div className="flex items-center gap-3">
        {isTestBenchDashboard && (
          <>
            <div className="flex items-center gap-2 bg-slate-700 px-2 py-1 rounded">
              <button
                onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                className="w-6 h-6 flex items-center justify-center hover:bg-slate-600 rounded"
                title="缩小"
              >
                −
              </button>
              <span className="text-sm w-12 text-center">{Math.round(zoom * 100)}%</span>
              <button
                onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                className="w-6 h-6 flex items-center justify-center hover:bg-slate-600 rounded"
                title="放大"
              >
                +
              </button>
              <button
                onClick={() => setZoom(1)}
                className="px-2 py-0.5 text-xs hover:bg-slate-600 rounded"
                title="重置"
              >
                重置
              </button>
            </div>
            
            <button
              onClick={() => setShowGrid(!showGrid)}
              className={`px-3 py-1.5 rounded text-sm ${
                showGrid ? 'bg-blue-600' : 'bg-slate-700'
              }`}
            >
              {showGrid ? '📐 隐藏网格' : '📐 显示网格'}
            </button>
            
            <button
              onClick={() => setGridSnap(!gridSnap)}
              className={`px-3 py-1.5 rounded text-sm ${
                gridSnap ? 'bg-purple-600' : 'bg-slate-700'
              }`}
              title="开启后台架位置自动对齐网格"
            >
              {gridSnap ? '🧲 吸附' : '🧲 自由'}
            </button>
            
            <button
              onClick={() => setEditMode(!isEditMode)}
              className={`px-3 py-1.5 rounded text-sm ${
                isEditMode ? 'bg-green-600' : 'bg-slate-700'
              }`}
            >
              {isEditMode ? '✏️ 编辑中' : '✏️ 编辑模式'}
            </button>
          </>
        )}
        
        <button
          onClick={() => setShowConfig(true)}
          className="px-3 py-1.5 rounded text-sm bg-slate-700 hover:bg-slate-600"
          title="系统配置"
        >
          ⚙️ 设置
        </button>
        
        <div className="text-sm text-gray-300 ml-2" suppressHydrationWarning>
          {currentTime ? formatDateTime(currentTime.toISOString()) : '--'}
        </div>
      </div>
      
      <ConfigManager isOpen={showConfig} onClose={() => setShowConfig(false)} />
    </header>
  );
}
