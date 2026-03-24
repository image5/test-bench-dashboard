'use client';

import { useState, useRef } from 'react';
import { BenchType, BENCH_TYPE_CONFIGS } from '@/types';

interface ImportResult {
  success: number;
  failed: number;
  errors: string[];
}

interface Props {
  laboratoryId?: string;
  onImport: (benches: Array<{
    name: string;
    type: BenchType;
    ipAddress: string;
    port: number;
    laboratoryId?: string;
    positionX: number;
    positionY: number;
  }>) => Promise<void>;
  onClose: () => void;
}

export default function BatchImportDialog({ laboratoryId, onImport, onClose }: Props) {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [previewData, setPreviewData] = useState<Array<{
    name: string;
    type: BenchType;
    ipAddress: string;
    port: number;
  }> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const parseCSV = (text: string) => {
    const lines = text.trim().split('\n');
    if (lines.length < 2) {
      throw new Error('文件至少需要包含标题行和一行数据');
    }

    const header = lines[0].split(',').map(h => h.trim().toLowerCase());
    const nameIndex = header.findIndex(h => h === 'name' || h === '名称');
    const typeIndex = header.findIndex(h => h === 'type' || h === '类型');
    const ipIndex = header.findIndex(h => h === 'ip' || h === 'ip地址');
    const portIndex = header.findIndex(h => h === 'port' || h === '端口');

    if (nameIndex === -1 || ipIndex === -1) {
      throw new Error('CSV 文件必须包含 name(名称) 和 ip(IP地址) 列');
    }

    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      if (values.length < Math.max(nameIndex, ipIndex) + 1) continue;

      const typeValue = typeIndex !== -1 ? values[typeIndex].toLowerCase() : 'other';
      const benchType = Object.values(BenchType).includes(typeValue as BenchType)
        ? (typeValue as BenchType)
        : BenchType.OTHER;

      data.push({
        name: values[nameIndex],
        type: benchType,
        ipAddress: values[ipIndex],
        port: portIndex !== -1 ? parseInt(values[portIndex]) || 8080 : 8080,
      });
    }

    return data;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result as string;
        const data = parseCSV(text);
        setPreviewData(data);
      } catch (err: any) {
        setError(err.message);
        setPreviewData(null);
      }
    };
    reader.readAsText(file);
  };

  const handleImport = async () => {
    if (!previewData || previewData.length === 0) return;

    setImporting(true);
    setError(null);

    const importResult: ImportResult = {
      success: 0,
      failed: 0,
      errors: [],
    };

    try {
      const benchesToImport = previewData.map((item, index) => ({
        ...item,
        laboratoryId,
        positionX: 100 + (index % 10) * 200,
        positionY: 100 + Math.floor(index / 10) * 150,
      }));

      await onImport(benchesToImport);
      importResult.success = benchesToImport.length;
    } catch (err: any) {
      importResult.failed = previewData.length;
      importResult.errors.push(err.message);
    }

    setResult(importResult);
    setImporting(false);
  };

  const downloadTemplate = () => {
    const template = `name,type,ip,port
HIL-001,hil,192.168.1.101,8080
SYSTEM-001,system,192.168.1.102,8080
ASSEMBLY-001,assembly,192.168.1.103,8080`;
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bench_import_template.csv';
    a.click();
    URL.revokeObjectURL(url);
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
          <h3 className="font-bold text-lg">批量导入台架</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">
            ×
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4">
          <div className="mb-4">
            <button
              onClick={downloadTemplate}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              📥 下载 CSV 模板
            </button>
          </div>

          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            <div className="text-4xl mb-2">📁</div>
            <div className="text-gray-600">点击选择 CSV 文件</div>
            <div className="text-sm text-gray-400 mt-1">支持 .csv 格式</div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
              {error}
            </div>
          )}

          {previewData && previewData.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">预览数据 ({previewData.length} 条)</h4>
              <div className="max-h-48 overflow-auto border rounded">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left">名称</th>
                      <th className="px-3 py-2 text-left">类型</th>
                      <th className="px-3 py-2 text-left">IP地址</th>
                      <th className="px-3 py-2 text-left">端口</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.map((item, index) => (
                      <tr key={index} className="border-t">
                        <td className="px-3 py-2">{item.name}</td>
                        <td className="px-3 py-2">
                          {BENCH_TYPE_CONFIGS.find(c => c.type === item.type)?.label || item.type}
                        </td>
                        <td className="px-3 py-2 font-mono">{item.ipAddress}</td>
                        <td className="px-3 py-2">{item.port}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {result && (
            <div className={`mt-4 p-3 rounded text-sm ${
              result.failed === 0 ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'
            }`}>
              <div>成功导入: {result.success} 条</div>
              {result.failed > 0 && <div>失败: {result.failed} 条</div>}
              {result.errors.length > 0 && (
                <ul className="mt-2 list-disc list-inside">
                  {result.errors.map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        <div className="p-4 border-t flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            关闭
          </button>
          {previewData && previewData.length > 0 && !result && (
            <button
              onClick={handleImport}
              disabled={importing}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {importing ? '导入中...' : `导入 ${previewData.length} 条`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
