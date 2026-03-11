'use client';

import { useStore } from '@/store';
import { alarmsApi } from '@/lib/api';
import { formatTime, getTimeAgo } from '@/lib/utils';
import { AlarmSeverity } from '@/types';
import { useState } from 'react';

export default function AlarmPanel() {
  const { alarms, activeAlarms, setAlarms } = useStore();
  const [acknowledging, setAcknowledging] = useState<string | null>(null);
  
  const handleAcknowledge = async (alarmId: string) => {
    try {
      setAcknowledging(alarmId);
      await alarmsApi.acknowledge(alarmId, '管理员');
      
      // 刷新告警列表
      const updated = await alarmsApi.list();
      setAlarms(updated);
    } catch (error) {
      console.error('确认告警失败:', error);
    } finally {
      setAcknowledging(null);
    }
  };

  const severityColors: Record<AlarmSeverity, string> = {
    [AlarmSeverity.LOW]: 'border-yellow-400 bg-yellow-50',
    [AlarmSeverity.MEDIUM]: 'border-orange-400 bg-orange-50',
    [AlarmSeverity.HIGH]: 'border-red-400 bg-red-50',
    [AlarmSeverity.CRITICAL]: 'border-red-600 bg-red-100',
  };

  return (
    <aside className="w-72 bg-white shadow-lg flex flex-col">
      <div className="p-4 border-b">
        <h3 className="font-bold text-gray-700 flex items-center gap-2">
          <span>🚨</span>
          告警中心
          {activeAlarms.length > 0 && (
            <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full animate-pulse">
              {activeAlarms.length}
            </span>
          )}
        </h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {activeAlarms.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            <div className="text-4xl mb-2">✅</div>
            <div>暂无活跃告警</div>
          </div>
        ) : (
          activeAlarms.map((alarm) => (
            <div
              key={alarm.id}
              className={`p-3 rounded-lg border-l-4 ${severityColors[alarm.severity]}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span>{alarm.typeInfo.icon}</span>
                  <span className="font-medium text-sm">{alarm.typeInfo.label}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {getTimeAgo(alarm.createdAt)}
                </span>
              </div>
              
              <p className="text-sm text-gray-700 mt-2">{alarm.message}</p>
              
              {alarm.value !== null && alarm.threshold !== null && (
                <div className="text-xs text-gray-500 mt-1">
                  当前值: {alarm.value} | 阈值: {alarm.threshold}
                </div>
              )}
              
              <button
                onClick={() => handleAcknowledge(alarm.id)}
                disabled={acknowledging === alarm.id}
                className="mt-2 w-full py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors disabled:opacity-50"
              >
                {acknowledging === alarm.id ? '确认中...' : '确认告警'}
              </button>
            </div>
          ))
        )}
      </div>
      
      {/* 历史告警 */}
      {alarms.filter(a => a.acknowledged).length > 0 && (
        <div className="border-t p-4">
          <h4 className="text-sm font-medium text-gray-500 mb-2">历史告警</h4>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {alarms.filter(a => a.acknowledged).slice(0, 5).map((alarm) => (
              <div key={alarm.id} className="text-xs text-gray-400 flex items-center gap-2">
                <span>{alarm.typeInfo.icon}</span>
                <span className="flex-1 truncate">{alarm.message}</span>
                <span>{getTimeAgo(alarm.createdAt)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}
