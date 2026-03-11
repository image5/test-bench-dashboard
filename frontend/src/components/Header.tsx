'use client';

import { useStore } from '@/store';
import { laboratoriesApi } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import { useState, useEffect } from 'react';

export default function Header() {
  const {
    laboratories,
    currentLaboratoryId,
    setCurrentLaboratory,
    isEditMode,
    setEditMode,
    showGrid,
    setShowGrid,
    statistics,
  } = useStore();
  
  const [currentTime, setCurrentTime] = useState(new Date());
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-slate-800 text-white px-4 py-3 flex items-center justify-between shadow-lg">
      {/* 左侧 - 标题和实验室选择 */}
      <div className="flex items-center gap-6">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <span className="text-2xl">🏭</span>
          智能测试台架工厂数字孪生看板
        </h1>
        
        {/* 实验室选择 */}
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
      </div>
      
      {/* 中间 - 统计摘要 */}
      {statistics && (
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
      
      {/* 右侧 - 工具栏 */}
      <div className="flex items-center gap-4">
        {/* 网格开关 */}
        <button
          onClick={() => setShowGrid(!showGrid)}
          className={`px-3 py-1.5 rounded text-sm ${
            showGrid ? 'bg-blue-600' : 'bg-slate-700'
          }`}
        >
          {showGrid ? '📐 隐藏网格' : '📐 显示网格'}
        </button>
        
        {/* 编辑模式开关 */}
        <button
          onClick={() => setEditMode(!isEditMode)}
          className={`px-3 py-1.5 rounded text-sm ${
            isEditMode ? 'bg-green-600' : 'bg-slate-700'
          }`}
        >
          {isEditMode ? '✏️ 编辑中' : '✏️ 编辑模式'}
        </button>
        
        {/* 当前时间 */}
        <div className="text-sm text-gray-300">
          {formatDateTime(currentTime.toISOString())}
        </div>
      </div>
    </header>
  );
}
