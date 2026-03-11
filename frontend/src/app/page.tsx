'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/store';
import { benchesApi, laboratoriesApi, statisticsApi } from '@/lib/api';
import Dashboard from '@/components/Dashboard';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import StatisticsPanel from '@/components/StatisticsPanel';
import AlarmPanel from '@/components/AlarmPanel';
import { TestBench, Laboratory, StatisticsOverview } from '@/types';

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const {
    setBenches,
    setLaboratories,
    setStatistics,
    currentLaboratoryId,
  } = useStore();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 并行加载数据
      const [benches, laboratories, stats] = await Promise.all([
        benchesApi.list(),
        laboratoriesApi.list(),
        statisticsApi.getOverview(),
      ]);
      
      setBenches(benches);
      setLaboratories(laboratories);
      setStatistics(stats);
      
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
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
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
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* 顶部导航 */}
      <Header />
      
      <div className="flex-1 flex">
        {/* 左侧边栏 - 台架类型 */}
        <Sidebar />
        
        {/* 主内容区 */}
        <main className="flex-1 flex flex-col">
          {/* 统计面板 */}
          <StatisticsPanel />
          
          {/* 看板画布 */}
          <Dashboard />
        </main>
        
        {/* 右侧告警面板 */}
        <AlarmPanel />
      </div>
    </div>
  );
}
