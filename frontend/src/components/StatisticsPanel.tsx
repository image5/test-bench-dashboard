'use client';

import { useStore } from '@/store';
import { STATUS_COLORS, STATUS_LABELS, BenchStatus } from '@/types';

export default function StatisticsPanel() {
  const { statistics } = useStore();
  
  if (!statistics) return null;

  const stats = [
    {
      label: '台架总数',
      value: statistics.totalBenches,
      color: 'bg-blue-500',
      icon: '📊',
    },
    {
      label: '运行中',
      value: statistics.runningCount,
      color: 'bg-green-500',
      icon: '🟢',
    },
    {
      label: '离线',
      value: statistics.offlineCount,
      color: 'bg-gray-500',
      icon: '⚪',
    },
    {
      label: '维护中',
      value: statistics.maintenanceCount,
      color: 'bg-yellow-500',
      icon: '🟡',
    },
    {
      label: '告警',
      value: statistics.alarmCount,
      color: 'bg-red-500',
      icon: '🔴',
    },
    {
      label: '空闲',
      value: statistics.idleCount,
      color: 'bg-blue-400',
      icon: '🔵',
    },
  ];

  return (
    <div className="bg-white shadow px-4 py-3">
      <div className="flex items-center justify-between">
        {/* 统计卡片 */}
        <div className="flex gap-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="flex items-center gap-3 px-4 py-2 rounded-lg bg-gray-50"
            >
              <span className="text-xl">{stat.icon}</span>
              <div>
                <div className="text-xs text-gray-500">{stat.label}</div>
                <div className={`text-xl font-bold ${stat.color.replace('bg-', 'text-')}`}>
                  {stat.value}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {/* 在线率 */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs text-gray-500">在线率</div>
            <div className={`text-2xl font-bold ${
              statistics.onlineRate >= 80 ? 'text-green-600' :
              statistics.onlineRate >= 60 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {statistics.onlineRate}%
            </div>
          </div>
          
          {/* 在线率进度条 */}
          <div className="w-32">
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  statistics.onlineRate >= 80 ? 'bg-green-500' :
                  statistics.onlineRate >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${statistics.onlineRate}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
