import { create } from 'zustand';
import { TestBench, Laboratory, Alarm, StatisticsOverview, BenchStatus } from '@/types';

interface AppState {
  // 台架
  benches: TestBench[];
  selectedBenchId: string | null;
  
  // 实验室
  laboratories: Laboratory[];
  currentLaboratoryId: string | null;
  
  // 告警
  alarms: Alarm[];
  activeAlarms: Alarm[];
  
  // 统计
  statistics: StatisticsOverview | null;
  
  // UI 状态
  isEditMode: boolean;
  showGrid: boolean;
  zoom: number;
  
  // Actions
  setBenches: (benches: TestBench[]) => void;
  addBench: (bench: TestBench) => void;
  updateBench: (id: string, updates: Partial<TestBench>) => void;
  removeBench: (id: string) => void;
  selectBench: (id: string | null) => void;
  
  setLaboratories: (labs: Laboratory[]) => void;
  setCurrentLaboratory: (id: string | null) => void;
  
  setAlarms: (alarms: Alarm[]) => void;
  addAlarm: (alarm: Alarm) => void;
  
  setStatistics: (stats: StatisticsOverview) => void;
  
  setEditMode: (mode: boolean) => void;
  setShowGrid: (show: boolean) => void;
  setZoom: (zoom: number) => void;
}

export const useStore = create<AppState>((set) => ({
  // 初始状态
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
  
  // Actions
  setBenches: (benches) => set({ benches }),
  
  addBench: (bench) => set((state) => ({
    benches: [...state.benches, bench]
  })),
  
  updateBench: (id, updates) => set((state) => ({
    benches: state.benches.map((b) =>
      b.id === id ? { ...b, ...updates } : b
    )
  })),
  
  removeBench: (id) => set((state) => ({
    benches: state.benches.filter((b) => b.id !== id),
    selectedBenchId: state.selectedBenchId === id ? null : state.selectedBenchId
  })),
  
  selectBench: (id) => set({ selectedBenchId: id }),
  
  setLaboratories: (laboratories) => set({ laboratories }),
  
  setCurrentLaboratory: (id) => set({ currentLaboratoryId: id }),
  
  setAlarms: (alarms) => set({ 
    alarms,
    activeAlarms: alarms.filter(a => !a.acknowledged)
  }),
  
  addAlarm: (alarm) => set((state) => ({
    alarms: [alarm, ...state.alarms],
    activeAlarms: alarm.acknowledged 
      ? state.activeAlarms 
      : [alarm, ...state.activeAlarms]
  })),
  
  setStatistics: (statistics) => set({ statistics }),
  
  setEditMode: (isEditMode) => set({ isEditMode }),
  
  setShowGrid: (showGrid) => set({ showGrid }),
  
  setZoom: (zoom) => set({ zoom }),
}));
