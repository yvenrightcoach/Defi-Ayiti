export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type League =
  | "bronze"
  | "silver"
  | "gold"
  | "platinum"
  | "diamond"
  | "master"
  | "champion";

export interface UserProfile {
  id: string;
  user: { id: string; username: string; is_guest: boolean };
  avatar_url: string;
  active_frame: string | null;
  department: string | null;
  department_detail: Department | null;
  level: number;
  xp: number;
  points: number;
  trophies: number;
  coins: number;
  diamonds: number;
  league: League;
  win_streak: number;
  best_win_streak: number;
  created_at: string;
}

export interface Department {
  id: string;
  name: string;
  slug: string;
  code: string;
  capital: string;
  description: string;
  map_image: string;
  icon: string;
  boss_name: string;
  order: number;
  is_unlocked: boolean;
}

export interface Level {
  id: string;
  department: string;
  order: number;
  name: string;
  description: string;
  question_count: number;
  required_score: number;
  xp_reward: number;
  coin_reward: number;
  is_boss_level: boolean;
  unlocks_hero: string | null;
}

export interface DepartmentDetail extends Department {
  levels: Level[];
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  order: number;
}

export type QuestionType =
  | "multiple_choice"
  | "true_false"
  | "image"
  | "timeline"
  | "matching"
  | "map";

export type Difficulty = "easy" | "medium" | "hard";

export interface Answer {
  id: string;
  text: string;
  image: string;
  order: number;
}

export interface Question {
  id: string;
  category: string;
  department: string | null;
  level: string | null;
  question_type: QuestionType;
  difficulty: Difficulty;
  text: string;
  image: string;
  xp_reward: number;
  is_boss_question: boolean;
  answers: Answer[];
}

export interface AnswerResult {
  is_correct: boolean;
  correct_answer_ids: string[];
  explanation: string;
  xp_awarded: number;
}

export interface Hero {
  id: string;
  name: string;
  slug: string;
  image: string;
  card_image: string;
  biography: string;
  quote: string;
  department: string | null;
  unlock_level: number;
  rarity: "common" | "rare" | "epic" | "legendary";
  order: number;
  is_unlocked: boolean;
}

export interface HeroCard {
  id: string;
  hero: Hero;
  unlocked_at: string;
  unlocked_via_level: string | null;
}

export interface PlayerProgress {
  id: string;
  department: string;
  department_detail: Department;
  current_level: string | null;
  current_level_detail: Level | null;
  stars: number;
  total_score: number;
  is_completed: boolean;
  completed_at: string | null;
}

export interface CompleteLevelResult {
  progress: PlayerProgress;
  level_passed: boolean;
  xp_awarded: number;
  coin_awarded: number;
  hero_unlocked: Hero | null;
}

export type FriendStatus = "pending" | "accepted" | "declined";

export interface Friend {
  id: string;
  requester: UserProfile;
  addressee: UserProfile;
  status: FriendStatus;
  created_at: string;
  responded_at: string | null;
}

export type RoomType = "duel" | "friend" | "tournament";
export type RoomStatus = "waiting" | "in_progress" | "finished" | "cancelled";
export type MatchStatus = "pending" | "ongoing" | "finished" | "cancelled";

export interface MatchParticipant {
  id: string;
  profile: UserProfile;
  score: number;
  correct_answers: number;
  rank: number | null;
  joined_at: string;
}

export interface Match {
  id: string;
  room: string;
  round_number: number;
  questions: string[];
  question_count: number;
  time_limit_seconds: number;
  status: MatchStatus;
  winner: string | null;
  started_at: string | null;
  ended_at: string | null;
  participants: MatchParticipant[];
}

export interface BattleRoom {
  id: string;
  room_code: string;
  room_type: RoomType;
  host: UserProfile;
  participants: UserProfile[];
  max_players: number;
  status: RoomStatus;
  rematch_of: string | null;
  started_at: string | null;
  finished_at: string | null;
  matches: Match[];
}

export interface Season {
  id: string;
  name: string;
  theme: string;
  description: string;
  banner_image: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export interface EventItem {
  id: string;
  season: string | null;
  name: string;
  description: string;
  banner_image: string;
  start_at: string;
  end_at: string;
  reward: string | null;
  is_active: boolean;
}

export type LeaderboardScope = "national" | "department" | "friends";
export type LeaderboardPeriod = "weekly" | "monthly" | "yearly" | "season" | "all_time";

export interface LeaderboardEntry {
  id: string;
  scope: LeaderboardScope;
  period: LeaderboardPeriod;
  department: string | null;
  season: string | null;
  profile: UserProfile;
  score: number;
  rank: number;
  period_start: string;
  period_end: string;
  generated_at: string;
}

export interface Reward {
  id: string;
  name: string;
  description: string;
  reward_type: string;
  image: string;
  coins_amount: number;
  diamonds_amount: number;
  xp_amount: number;
  grants_hero: string | null;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  criteria_type: string;
  criteria_value: number;
  reward: Reward | null;
}

export interface PlayerAchievement {
  id: string;
  achievement: Achievement;
  progress: number;
  unlocked_at: string | null;
}

export interface Mission {
  id: string;
  name: string;
  description: string;
  mission_type: string;
  target_value: number;
  xp_reward: number;
  coin_reward: number;
  is_daily: boolean;
  is_active: boolean;
}

export interface PlayerMission {
  id: string;
  mission: Mission;
  assigned_date: string;
  progress: number;
  is_completed: boolean;
  completed_at: string | null;
  reward_claimed: boolean;
}

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  item_type: "avatar" | "frame" | "booster";
  image: string;
  price_coins: number;
  price_diamonds: number;
  is_available: boolean;
}

export interface Purchase {
  id: string;
  shop_item: ShopItem;
  price_paid_coins: number;
  price_paid_diamonds: number;
  purchased_at: string;
}

export interface DiamondPack {
  id: string;
  name: string;
  diamonds_amount: number;
  price_usd_cents: number;
  order: number;
}

export interface AppNotification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  action_url: string;
  is_read: boolean;
  created_at: string;
}
