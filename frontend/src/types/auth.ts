export interface AuthUser {
  id: string;
  username: string;
  email?: string;
  isGuest: boolean;
}
