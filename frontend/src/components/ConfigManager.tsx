'use client';

import { useState, useEffect } from 'react';
import { loadConfig, clearConfigCache } from '@/lib/config';

interface ConfigManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ConfigManager({ isOpen, onClose }: ConfigManagerProps) {
  const [apiUrl, setApiUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadCurrentConfig();
    }
  }, [isOpen]);

  const loadCurrentConfig = async () => {
    try {
      const config = await loadConfig();
      setApiUrl(config.apiUrl);
    } catch (error) {
      console.error('Failed to load config:', error);
      setMessage({ type: 'error', text: '加载配置失败' });
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    setMessage(null);

    try {
      // 验证 URL 格式
      new URL(apiUrl);
      
      // 获取当前配置
      const currentConfig = await loadConfig();
      
      // 构建完整的 API URL
      const configApiUrl = apiUrl.replace('/api/v1', '') + '/api/v1/config';
      
      // 更新配置文件
      const response = await fetch(configApiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          apiUrl,
          version: "1.0.0",
          lastUpdate: new Date().toISOString().split('T')[0]
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '保存失败');
      }

      // 清除缓存并重新加载
      clearConfigCache();
      
      setMessage({ type: 'success', text: '配置已保存，将在刷新页面后生效' });
      
      setTimeout(() => {
        onClose();
        window.location.reload();
      }, 1500);
      
    } catch (error: any) {
      console.error('Save config error:', error);
      setMessage({ 
        type: 'error', 
        text: error.message || '保存失败，请检查 URL 格式是否正确' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setApiUrl('http://localhost:8000/api/v1');
    setMessage(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-800">⚙️ 系统配置</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          {/* API 地址配置 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              服务器 API 地址
            </label>
            <input
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://192.168.1.100:8000/api/v1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm font-mono"
            />
            <p className="text-xs text-gray-500 mt-1">
              💡 提示：修改为服务器 IP 后，局域网内其他设备可访问本系统
            </p>
          </div>

          {/* 示例配置 */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs font-medium text-gray-700 mb-2">快速配置：</p>
            <div className="space-y-1">
              <button
                onClick={() => setApiUrl('http://localhost:8000/api/v1')}
                className="text-xs text-blue-600 hover:text-blue-800 block"
              >
                • 本地开发：http://localhost:8000/api/v1
              </button>
              <button
                onClick={() => setApiUrl('http://192.168.1.100:8000/api/v1')}
                className="text-xs text-blue-600 hover:text-blue-800 block"
              >
                • 局域网访问：http://192.168.1.100:8000/api/v1
              </button>
            </div>
          </div>

          {/* 消息提示 */}
          {message && (
            <div
              className={`p-3 rounded-lg text-sm ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {message.text}
            </div>
          )}
        </div>

        {/* 按钮组 */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={handleReset}
            disabled={isLoading}
            className="flex-1 px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
          >
            恢复默认
          </button>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="flex-1 px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading || !apiUrl}
            className="flex-1 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
}
