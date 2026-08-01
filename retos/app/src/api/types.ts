/** Espejo de los modelos de `retos/backend/app/models.py`. */

export type AgeBand = '3-4' | '5-6';

export type SkillArea =
  | 'motricidad_fina'
  | 'lenguaje'
  | 'logica'
  | 'atencion'
  | 'socioemocional';

export type RewardKind = 'personaje' | 'historia' | 'imprimible';

export type EntitlementStatus = 'trialing' | 'active' | 'expired' | 'none';

export type MilestoneStatus = 'pendiente' | 'canjeado';

export interface Activity {
  activity_id: string;
  title: string;
  instructions: string;
  skill_area: SkillArea;
  materials: string[];
  est_minutes: number;
  screen_free: boolean;
}

export interface ActivityStatus {
  activity: Activity;
  completed: boolean;
}

export interface RewardOption {
  option_id: string;
  kind: RewardKind;
  title: string;
  description: string;
  asset_key: string;
}

export interface RewardStatus {
  unlocked: boolean;
  claimed: boolean;
  options: RewardOption[];
  chosen_option_id: string | null;
}

export interface WeekView {
  week_index: number;
  title: string;
  subtitle: string;
  activities: ActivityStatus[];
  completed_count: number;
  activities_required: number;
  week_completed: boolean;
  accessible: boolean;
  locked_reason: string | null;
  reward: RewardStatus;
}

export interface Child {
  child_id: string;
  name: string;
  age_band: AgeBand;
  avatar_key: string;
  enrolled_at: string;
}

export interface PlanView {
  child: Child;
  total_weeks: number;
  unlocked_week: number;
  current_week: number;
  catchup_weeks: number[];
  completed_weeks: number[];
  plan_finished: boolean;
  next_unlock_at: string | null;
}

export interface Entitlement {
  status: EntitlementStatus;
  expires_at: string | null;
  active: boolean;
}

export interface ParentProfile {
  parent_id: string;
  email: string;
  entitlement: Entitlement;
  created_at: string;
}

export interface Milestone {
  milestone_id: string;
  week_index: number;
  code: string;
  status: MilestoneStatus;
  created_at: string;
  redeemed_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  parent_id: string;
}
