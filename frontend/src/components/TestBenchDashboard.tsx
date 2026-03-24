'use client';

import { useEffect, useState, useCallback } from 'react';
import { useStore } from '@/store';
import { benchesApi, laboratoriesApi, statisticsApi, alarmsApi } from '@/lib/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import Dashboard from '@/components/Dashboard';
import Sidebar from '@/components/Sidebar';
import StatisticsPanel from '@/components/StatisticsPanel';
import AlarmPanel from '@/components/AlarmPanel';

export default function TestBenchDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    setBenches,
    setLaboratories,
    setStatistics,
    setAlarms,
  } = useStore();

  const { isConnected } = useWebSocket();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      const [benches, laboratories, stats, alarms] = await Promise.all([
        benchesApi.list(),
        laboratoriesApi.list(),
        statisticsApi.getOverview(),
        alarmsApi.list(),
      ]);

      setBenches(benches);
      setLaboratories(laboratories);
      setStatistics(stats);
      setAlarms(alarms);

      setError(null);
    } catch (err: any) {
      console.error('加载数据失败:', err);
      setError(err.message || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex">
      <Sidebar />

      <main className="flex-1 flex flex-col">
        <div className="bg-gray-100 px-4 py-1 flex items-center gap-2 text-sm">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          ></span>
          <span className="text-gray-600">
            {isConnected ? '实时连接' : '离线模式'}
          </span>
        </div>

        <StatisticsPanel />
        <Dashboard />
      </main>

      <AlarmPanel />
    </div>
  );
}
