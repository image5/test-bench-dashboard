'use client';

import { useState } from 'react';
import { TestBench, BenchType, BENCH_TYPE_CONFIGS } from '@/types';

interface Props {
  bench: TestBench;
  onSave: (data: {
    name?: string;
    type?: BenchType;
    ipAddress?: string;
    port?: number;
  }) => Promise<void>;
  onClose: () => void;
}

export default function EditBenchDialog({ bench, onSave, onClose }: Props) {
  const [name, setName] = useState(bench.name);
  const [type, setType] = useState<BenchType>(bench.type);
  const [ipAddress, setIpAddress] = useState(bench.network.ip);
  const [port, setPort] = useState(bench.network.port);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('请输入台架名称');
      return;
    }
    
    if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(ipAddress)) {
      setError('请输入有效的IP地址');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await onSave({ name, type, ipAddress, port });
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg p-6 w-96 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="font-bold text-lg mb-4">编辑台架</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">
              台架名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-600 mb-1">台架类型</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as BenchType)}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {BENCH_TYPE_CONFIGS.map((config) => (
                <option key={config.type} value={config.type}>
                  {config.icon} {config.label}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm text-gray-600 mb-1">
              IP地址 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={ipAddress}
              onChange={(e) => setIpAddress(e.target.value)}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-600 mb-1">端口</label>
            <input
              type="number"
              value={port}
              onChange={(e) => setPort(parseInt(e.target.value) || 8080)}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="text-sm text-gray-500">
            位置: ({Math.round(bench.position.x)}, {Math.round(bench.position.y)})
          </div>
          
          {error && (
            <div className="text-sm text-red-500 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}
          
          <div className="flex justify-end gap-2 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
              disabled={loading}
            >
              取消
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
