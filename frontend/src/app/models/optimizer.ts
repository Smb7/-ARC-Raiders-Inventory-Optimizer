export interface YieldPreview {
  item_id: string;
  name: string;
  quantity: number;
  context: string;
}

export interface ChecklistItem {
  item_id: string;
  raw_id: string;
  name: string;
  category: string;
  rarity: string;
  quantity: number;
  weight: number;
  vendor_sell_price: number;
  durability: number | null;
  known: boolean;
  reason: string;
  badge: string;
  yields: YieldPreview[];
}

export interface OptimizeResult {
  keep: ChecklistItem[];
  recycle: ChecklistItem[];
  sell: ChecklistItem[];
  scanned_count: number;
  total_quantity: number;
}

export interface ConnectResponse {
  user_id: string;
  remember_me: boolean;
}

export interface PreferenceUpdate {
  scrappy_level: number;
  gunsmith_level: number;
  gear_bench_level: number;
  medical_lab_level: number;
  explosives_station_level: number;
  utility_station_level: number;
  refiner_level: number;
  research_station_level: number;
  stash_level: number;
  never_sell_ammo_materials: boolean;
  keep_high_yield_seeds: boolean;
  highlight_low_durability_duplicates: boolean;
}
