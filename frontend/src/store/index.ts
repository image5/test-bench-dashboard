import { create } from 'zustand';
import { TestBench, Laboratory, Alarm, StatisticsOverview, BenchStatus } from '@/types';

interface AppState {
  benches: TestBench[];
  selectedBenchId: string | null;
  laboratories: Laboratory[];
  currentLaboratoryId: string | null;
  alarms: Alarm[];
  activeAlarms: Alarm[];
  statistics: StatisticsOverview | null;
  isEditMode: boolean;
  showGrid: boolean;
  zoom: number;
  gridSnap: boolean;

  setBenches: (benches: TestBench[]) => void;
  addBench: (bench: TestBench) => void;
  updateBench: (id: string, updates: Partial<TestBench>) => void;
  updateBenchStatus: (id: string, status: any) => void;
  updateBenchPosition: (id: string, position: { x: number; y: number; rotation?: number }) => void;
  removeBench: (id: string) => void;
  selectBench: (id: string | null) => void;

  setLaboratories: (labs: Laboratory[]) => void;
  setCurrentLaboratory: (id: string | null) => void;

  setAlarms: (alarms: Alarm[]) => void;
  addAlarm: (alarm: Alarm) => void;
  acknowledgeAlarm: (id: string) => void;

  setStatistics: (stats: StatisticsOverview) => void;
  updateStatisticsFromBenches: () => void;

  setEditMode: (mode: boolean) => void;
  setShowGrid: (show: boolean) => void;
  setZoom: (zoom: number) => void;
  setGridSnap: (snap: boolean) => void;
}

export const useStore = create<AppState>((set, get) => ({
  benches: [],
  selectedBenchId: null,
  laboratories: [],
  currentLaboratoryId: null,
  alarms: [],
  activeAlarms: [],
  statistics: null,
  isEditMode: false,
  showGrid: true,
  zoom: 1,
  gridSnap: true,

  setBenches: (benches) => set({ benches }),

  addBench: (bench) =>
    set((state) => ({
      benches: [...state.benches, bench],
    })),

  updateBench: (id, updates) =>
    set((state) => ({
      benches: state.benches.map((b) => (b.id === id ? { ...b, ...updates } : b)),
    })),

  updateBenchStatus: (id, status) =>
    set((state) => ({
      benches: state.benches.map((b) =>
        b.id === id ? { ...b, status: { ...b.status, ...status } } : b
      ),
    })),

  updateBenchPosition: (id, position) =>
    set((state) => ({
      benches: state.benches.map((b) =>
        b.id === id ? { ...b, position: { ...b.position, ...position } } : b
      ),
    })),

  removeBench: (id) =>
    set((state) => ({
      benches: state.benches.filter((b) => b.id !== id),
      selectedBenchId: state.selectedBenchId === id ? null : state.selectedBenchId,
    })),

  selectBench: (id) => set({ selectedBenchId: id }),

  setLaboratories: (laboratories) => set({ laboratories }),

  setCurrentLaboratory: (id) => set({ currentLaboratoryId: id }),

  setAlarms: (alarms) =>
    set({
      alarms,
      activeAlarms: alarms.filter((a) => !a.acknowledged),
    }),

  addAlarm: (alarm) =>
    set((state) => ({
      alarms: [alarm, ...state.alarms],
      activeAlarms: alarm.acknowledged ? state.activeAlarms : [alarm, ...state.activeAlarms],
    })),

  acknowledgeAlarm: (id) =>
    set((state) => ({
      alarms: state.alarms.map((a) =>
        a.id === id ? { ...a, acknowledged: true } : a
      ),
      activeAlarms: state.activeAlarms.filter((a) => a.id !== id),
    })),

  setStatistics: (statistics) => set({ statistics }),

  updateStatisticsFromBenches: () => {
    const benches = get().benches;
    const total = benches.length;
    const running = benches.filter((b) => b.status.state === 'running').length;
    const offline = benches.filter((b) => b.status.state === 'offline').length;
    const maintenance = benches.filter((b) => b.status.state === 'maintenance').length;
    const alarm = benches.filter((b) => b.status.state === 'alarm').length;
    const idle = benches.filter((b) => b.status.state === 'idle').length;
    const online = running + idle + alarm;
    const onlineRate = total > 0 ? Math.round((online / total) * 100 * 10) / 10 : 0;

    set({
      statistics: {
        totalBenches: total,
        runningCount: running,
        offlineCount: offline,
        maintenanceCount: maintenance,
        alarmCount: alarm,
        idleCount: idle,
        onlineRate,
        currentTime: new Date().toISOString(),
        statusBreakdown: { running, offline, maintenance, alarm, idle },
      },
    });
  },

  setEditMode: (isEditMode) => set({ isEditMode }),

  setShowGrid: (showGrid) => set({ showGrid }),

  setZoom: (zoom) => set({ zoom: Math.max(0.25, Math.min(2, zoom)) }),

  setGridSnap: (gridSnap) => set({ gridSnap }),
}));
