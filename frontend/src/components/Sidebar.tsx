'use client';

import { useState } from 'react';
import { useStore } from '@/store';
import { BENCH_TYPE_CONFIGS, BenchType } from '@/types';
import { benchesApi } from '@/lib/api';
import BatchImportDialog from './BatchImportDialog';

export default function Sidebar() {
  const { isEditMode, benches, currentLaboratoryId, addBench } = useStore();
  const [showImportDialog, setShowImportDialog] = useState(false);

  const typeStats = BENCH_TYPE_CONFIGS.map((config) => {
    const count = benches.filter((b) => b.type === config.type).length;
    return { ...config, count };
  });

  const handleBatchImport = async (
    benchesToImport: Array<{
      name: string;
      type: BenchType;
      ipAddress: string;
      port: number;
      laboratoryId?: string;
      positionX: number;
      positionY: number;
    }>
  ) => {
    const result = await benchesApi.import({
      laboratoryId: currentLaboratoryId || undefined,
      benches: benchesToImport.map(item => ({
        name: item.name,
        type: item.type,
        ip_address: item.ipAddress,
        port: item.port,
        position_x: item.positionX,
        position_y: item.positionY,
      })),
    });

    if (result.createdBenches) {
      result.createdBenches.forEach((bench: any) => addBench(bench));
    }

    if (result.failedCount > 0) {
      throw new Error(`${result.failedCount} 条导入失败`);
    }
  };

  if (!isEditMode) {
    return (
      <aside className="w-48 bg-white shadow-lg p-4">
        <h3 className="font-bold text-gray-700 mb-4">台架统计</h3>
        <div className="space-y-2">
          {typeStats.map((stat) => (
            <div
              key={stat.type}
              className="flex items-center justify-between p-2 rounded bg-gray-50"
            >
              <div className="flex items-center gap-2">
                <span>{stat.icon}</span>
                <span className="text-sm">{stat.label}</span>
              </div>
              <span className="font-bold text-gray-700">{stat.count}</span>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t">
          <div className="text-sm text-gray-500">
            总计: <span className="font-bold text-gray-700">{benches.length}</span> 台
          </div>
        </div>
      </aside>
    );
  }

  return (
    <>
      <aside className="w-56 bg-white shadow-lg p-4 flex flex-col">
        <h3 className="font-bold text-gray-700 mb-4">台架库</h3>
        <p className="text-xs text-gray-500 mb-4">拖拽台架到画布添加</p>

        <div className="space-y-2 flex-1">
          {BENCH_TYPE_CONFIGS.map((config) => (
            <div
              key={config.type}
              draggable
              onDragStart={(e) => {
                e.dataTransfer.setData('benchType', config.type);
              }}
              className="flex items-center gap-2 p-3 rounded-lg border-2 border-dashed border-gray-300 cursor-move hover:border-blue-500 hover:bg-blue-50 transition-all"
            >
              <span className="text-xl">{config.icon}</span>
              <span className="text-sm font-medium">{config.label}</span>
            </div>
          ))}
        </div>

        <button
          onClick={() => setShowImportDialog(true)}
          className="mt-4 w-full py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium"
        >
          📥 批量导入
        </button>

        <div className="mt-4 pt-4 border-t">
          <h4 className="font-medium text-gray-700 mb-2">操作说明</h4>
          <ul className="text-xs text-gray-500 space-y-1">
            <li>• 拖拽台架到画布添加</li>
            <li>• 点击台架可编辑</li>
            <li>• 拖动台架调整位置</li>
            <li>• 右键台架可删除</li>
            <li>• Ctrl+滚轮缩放</li>
            <li>• Alt+拖拽平移</li>
          </ul>
        </div>
      </aside>

      {showImportDialog && (
        <BatchImportDialog
          laboratoryId={currentLaboratoryId || undefined}
          onImport={handleBatchImport}
          onClose={() => setShowImportDialog(false)}
        />
      )}
    </>
  );
}
