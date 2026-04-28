import type { PaperListItem } from "../pages/list/listTypes";


export interface BootstrapPayload {
  is_authenticated: boolean;
  username: string;
  has_personal_api_key: boolean;
  preferred_summary_model: string;
  available_summary_models: string[];
}


export interface AuthPayload {
  ok?: boolean;
  username?: string;
  error?: string;
}


export interface SettingsPayload {
  preferred_summary_model: string;
  available_summary_models: string[];
  error?: string;
}


export interface FavoriteListPayload {
  items: PaperListItem[];
  error?: string;
}


export interface FavoriteTogglePayload {
  is_favorited?: boolean;
  error?: string;
}


export interface ApiKeyPayload {
  ok?: boolean;
  has_personal_api_key?: boolean;
  error?: string;
}
