'use client';

import { useEffect, useState } from 'react';
import { benchesApi } from '@/lib/api';

interface MaintenanceRecord {
  id: string;
  benchId: string;
  reason: string;
  operator: string;
  notes: string | null;
  startTime: string;
  endTime: string | null;
  duration: string | null;
  createdAt: string;
}

interface Props {
  benchId: string;
  benchName: string;
  onClose: () => void;
}

export default function MaintenanceHistoryDialog({ benchId, benchName, onClose }: Props) {
  const [records, setRecords] = useState<MaintenanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, [benchId]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/benches/${benchId}/maintenance-history`);
      if (!response.ok) throw new Error('加载失败');
      const data = await response.json();
      setRecords(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '--';
    return new Date(dateStr).toLocaleString('zh-CN');
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl w-[600px] max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="font-bold text-lg">维护历史 - {benchName}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="text-center py-8 text-gray-500">加载中...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-500">{error}</div>
          ) : records.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">📋</div>
              <div>暂无维护记录</div>
            </div>
          ) : (
            <div className="space-y-3">
              {records.map((record) => (
                <div
                  key={record.id}
                  className="border rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">🔧</span>
                      <span className="font-medium">{record.reason || '例行维护'}</span>
                    </div>
                    {record.endTime ? (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        已完成
                      </span>
                    ) : (
                      <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                        进行中
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div>
                      <span className="text-gray-400">维护人员：</span>
                      {record.operator || '--'}
                    </div>
                    <div>
                      <span className="text-gray-400">维护时长：</span>
                      {record.duration || '--'}
                    </div>
                    <div>
                      <span className="text-gray-400">开始时间：</span>
                      {formatDate(record.startTime)}
                    </div>
                    <div>
                      <span className="text-gray-400">结束时间：</span>
                      {formatDate(record.endTime)}
                    </div>
                  </div>

                  {record.notes && (
                    <div className="mt-2 text-sm text-gray-600">
                      <span className="text-gray-400">备注：</span>
                      {record.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}
