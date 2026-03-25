'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useStore } from '@/store';
import { loadConfig } from '@/lib/config';

type WebSocketMessage = {
  event: string;
  data: any;
};

const MAX_RECONNECT_ATTEMPTS = 10;
const HEARTBEAT_INTERVAL = 30000; // 30秒
const OFFLINE_THRESHOLD = 4; // 4次无响应判定离线
const isDev = process.env.NODE_ENV === 'development';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const missedHeartbeatsRef = useRef(0);
  const [isConnected, setIsConnected] = useState(false);
  const mountedRef = useRef(true);

  const {
    updateBench,
    updateBenchStatus,
    updateBenchPosition,
    removeBench,
    addBench,
    addAlarm,
    acknowledgeAlarm,
    setStatistics,
    updateStatisticsFromBenches,
    benches,
  } = useStore();

  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      const { event, data } = message;

      switch (event) {
        case 'bench_created':
          addBench(data);
          updateStatisticsFromBenches();
          break;

        case 'bench_updated':
        case 'bench_maintenance_changed':
          updateBench(data.id, data);
          updateStatisticsFromBenches();
          break;

        case 'bench_heartbeat':
          if (data.id && data.status) {
            updateBenchStatus(data.id, data.status);
            if (data.currentTask !== undefined) {
              updateBench(data.id, {
                status: {
                  ...benches.find(b => b.id === data.id)?.status,
                  currentTask: data.currentTask,
                  lastHeartbeat: data.lastHeartbeat
                } as any
              });
            }
            updateStatisticsFromBenches();
          }
          break;

        case 'bench_moved':
          if (data.id && data.position) {
            updateBenchPosition(data.id, data.position);
          }
          break;

        case 'bench_deleted':
          removeBench(data.id);
          updateStatisticsFromBenches();
          break;

        case 'bench_alarm_cleared':
          if (data.id) {
            updateBench(data.id, {
              alarm: { hasAlarm: false, message: null },
            });
          }
          break;

        case 'alarm_created':
          addAlarm(data);
          break;

        case 'alarm_acknowledged':
        case 'alarm_cleared':
          if (data.id) {
            acknowledgeAlarm(data.id);
          }
          break;

        case 'device_status_update':
          if (Array.isArray(data)) {
            data.forEach((update: any) => {
              if (update.id && update.status) {
                updateBenchStatus(update.id, { state: update.status });
              }
            });
            updateStatisticsFromBenches();
          }
          break;

        case 'statistics_update':
          setStatistics(data);
          break;

        case 'pong':
          missedHeartbeatsRef.current = 0;
          break;

        default:
          break;
      }
    },
    [
      addBench,
      updateBench,
      updateBenchStatus,
      updateBenchPosition,
      removeBench,
      addAlarm,
      acknowledgeAlarm,
      setStatistics,
      updateStatisticsFromBenches,
      benches,
    ]
  );

  const sendHeartbeat = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      missedHeartbeatsRef.current++;
      
      if (missedHeartbeatsRef.current >= OFFLINE_THRESHOLD) {
        if (isDev) console.log('[WS] 心跳超时，标记所有台架离线');
        benches.forEach(bench => {
          if (bench.status.state !== 'offline' && bench.status.state !== 'maintenance') {
            updateBenchStatus(bench.id, { state: 'offline' });
          }
        });
        updateStatisticsFromBenches();
      } else {
        wsRef.current.send(JSON.stringify({ event: 'ping', data: {} }));
      }
    }
  }, [benches, updateBenchStatus, updateStatisticsFromBenches]);

  const connect = useCallback(async () => {
    if (!mountedRef.current) return;

    try {
      const config = await loadConfig();
      const apiUrl = config.apiUrl;
      const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
      const wsHost = apiUrl.replace(/^https?:\/\//, '').replace(/\/api\/v1$/, '');
      const wsUrl = `${wsProtocol}://${wsHost}/ws`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isDev) console.log('[WS] Connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        missedHeartbeatsRef.current = 0;
        
        if (heartbeatTimeoutRef.current) {
          clearInterval(heartbeatTimeoutRef.current);
        }
        heartbeatTimeoutRef.current = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (err) {
          if (isDev) console.error('[WS] Parse error:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        if (heartbeatTimeoutRef.current) {
          clearInterval(heartbeatTimeoutRef.current);
        }
        if (mountedRef.current) {
          scheduleReconnect();
        }
      };

      ws.onerror = () => {
        // Error is handled by onclose
      };
    } catch (err) {
      if (mountedRef.current) {
        scheduleReconnect();
      }
    }
  }, [handleMessage, sendHeartbeat]);

  const scheduleReconnect = useCallback(() => {
    if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
      return;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
    reconnectAttemptsRef.current++;

    reconnectTimeoutRef.current = setTimeout(() => {
      if (mountedRef.current) {
        connect();
      }
    }, delay);
  }, [connect]);

  const disconnect = useCallback(() => {
    mountedRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    disconnect,
    reconnect: connect,
  };
}
