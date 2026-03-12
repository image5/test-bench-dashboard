'use client';

import { useEffect, useState } from 'react';
import { projectAPI, Project } from '@/lib/dvp-api';

export default function DVPDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  useEffect(() => {
    fetchProjects();
    
    // 定时刷新（每30秒）
    const interval = setInterval(fetchProjects, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await projectAPI.getAll(0, 500);
      setProjects(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching projects:', err);
      
      // 更友好的错误提示
      if (err.message?.includes('DVP后端服务未启动')) {
        setError('DVP后端服务未启动');
      } else if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        setError('无法连接到DVP后端服务');
      } else {
        setError(err.message || '加载项目失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleProjectClick = (project: Project) => {
    setSelectedProject(project);
  };

  // 计算统计数据
  const stats = {
    total: projects.length,
    running: projects.filter(p => p.progress < 100 && !p.is_interrupted).length,
    completed: projects.filter(p => p.progress >= 100).length,
    interrupted: projects.filter(p => p.is_interrupted).length,
    avgProgress: projects.length > 0 
      ? (projects.reduce((sum, p) => sum + p.progress, 0) / projects.length).toFixed(1)
      : 0,
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
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center max-w-lg">
          <span className="text-6xl mb-4 block">⚠️</span>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">{error}</h2>
          <p className="text-gray-600 mb-6">
            DVP进度看板需要独立的后端服务支持
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left mb-4">
            <h3 className="font-semibold text-blue-900 mb-2">📋 启动步骤：</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>打开新的终端窗口</li>
              <li>进入 DVP 后端目录：
                <code className="bg-blue-100 px-1 rounded ml-1">
                  cd dvp-dashboard/backend
                </code>
              </li>
              <li>启动后端服务：
                <code className="bg-blue-100 px-1 rounded ml-1">
                  start.bat
                </code>
              </li>
              <li>等待服务启动完成（约10秒）</li>
              <li>刷新此页面</li>
            </ol>
          </div>
          
          <div className="flex gap-3 justify-center">
            <button
              onClick={fetchProjects}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              🔄 重试
            </button>
            <button
              onClick={() => window.open('http://localhost:8001/docs', '_blank')}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              📚 查看API文档
            </button>
          </div>
          
          <p className="text-xs text-gray-500 mt-4">
            💡 提示：DVP后端运行在端口 8001，测试台架后端运行在端口 8000
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">车辆控制器 DVP 进度监控</h2>
        <p className="text-gray-600 mt-1">实时追踪项目进度，监控设备状态</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow border">
          <p className="text-sm text-gray-600">总项目数</p>
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <p className="text-sm text-gray-600">进行中</p>
          <p className="text-2xl font-bold text-blue-600">{stats.running}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <p className="text-sm text-gray-600">已完成</p>
          <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <p className="text-sm text-gray-600">已中断</p>
          <p className="text-2xl font-bold text-red-600">{stats.interrupted}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <p className="text-sm text-gray-600">平均进度</p>
          <p className="text-2xl font-bold text-purple-600">{stats.avgProgress}%</p>
        </div>
      </div>

      {/* 项目列表 */}
      <div className="bg-white rounded-lg shadow flex-1 overflow-auto">
        <div className="p-4 border-b bg-gray-50">
          <h3 className="font-semibold text-gray-900">项目进度列表</h3>
        </div>
        
        <div className="p-4">
          {projects.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              暂无项目数据
            </div>
          ) : (
            <div className="space-y-3">
              {projects.map((project) => (
                <div
                  key={project.project_id}
                  onClick={() => handleProjectClick(project)}
                  className="p-4 border rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">{project.name}</span>
                      
                      {/* 状态图标 */}
                      {project.is_interrupted && (
                        <span className="text-red-500" title="已中断">⚠️</span>
                      )}
                      {!project.is_interrupted && project.param_checked && (
                        <span className="text-green-500" title="参数已检查">✅</span>
                      )}
                      {!project.is_interrupted && !project.param_checked && (
                        <span className="text-gray-400" title="待检查">⏱️</span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-gray-600">
                        {project.progress.toFixed(1)}%
                      </span>
                      
                      {project.param_checked && (
                        <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                          参数已检查
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* 进度条 */}
                  <div className="relative h-2 bg-gray-200 rounded overflow-hidden">
                    <div
                      className={`absolute h-full transition-all duration-300 ${
                        project.is_interrupted 
                          ? 'bg-red-500' 
                          : project.progress >= 100 
                            ? 'bg-green-500' 
                            : 'bg-blue-500'
                      }`}
                      style={{ width: `${Math.min(100, project.progress)}%` }}
                    />
                  </div>
                  
                  {/* 项目详情 */}
                  <div className="mt-2 flex items-center gap-6 text-xs text-gray-500">
                    <span>实验组: {project.total_experiments}</span>
                    <span>设备: {project.total_devices}</span>
                    <span>更新: {new Date(project.updated_at).toLocaleString('zh-CN')}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 选中项目详情（可选） */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-semibold text-lg">{selectedProject.name}</h3>
              <button
                onClick={() => setSelectedProject(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600">进度</p>
                  <p className="text-xl font-bold">{selectedProject.progress.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">实验组数</p>
                  <p className="text-xl font-bold">{selectedProject.total_experiments}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">设备总数</p>
                  <p className="text-xl font-bold">{selectedProject.total_devices}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">状态</p>
                  <p className="text-xl font-bold">
                    {selectedProject.is_interrupted ? '已中断' : 
                     selectedProject.progress >= 100 ? '已完成' : '进行中'}
                  </p>
                </div>
              </div>
              
              <div className="text-sm text-gray-500">
                <p>项目ID: {selectedProject.project_id}</p>
                <p>创建时间: {new Date(selectedProject.created_at).toLocaleString('zh-CN')}</p>
                <p>更新时间: {new Date(selectedProject.updated_at).toLocaleString('zh-CN')}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
