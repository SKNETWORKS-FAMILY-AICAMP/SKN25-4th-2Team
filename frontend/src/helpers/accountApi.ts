import type {
  ApiKeyPayload,
  AuthPayload,
  FavoriteListPayload,
  FavoriteTogglePayload,
  SettingsPayload,
} from "../types/app";
import { fetchJson, fetchJsonWithBody } from "./http";


export async function postSignup(username: string, password: string): Promise<AuthPayload> {
  return fetchJsonWithBody<AuthPayload>("/auth/signup/", "POST", { username, password });
}


export async function postLogin(username: string, password: string): Promise<AuthPayload> {
  return fetchJsonWithBody<AuthPayload>("/auth/login/", "POST", { username, password });
}


export async function postLogout(): Promise<AuthPayload> {
  return fetchJsonWithBody<AuthPayload>("/auth/logout/", "POST");
}


export async function fetchSettings(): Promise<SettingsPayload> {
  return fetchJson<SettingsPayload>("/settings/");
}


export async function saveSettings(preferredSummaryModel: string): Promise<SettingsPayload> {
  return fetchJsonWithBody<SettingsPayload>("/settings/", "POST", {
    preferred_summary_model: preferredSummaryModel,
  });
}


export async function savePersonalApiKey(apiKey: string): Promise<ApiKeyPayload> {
  return fetchJsonWithBody<ApiKeyPayload>("/settings/api-key/", "POST", { api_key: apiKey });
}


export async function clearPersonalApiKey(): Promise<ApiKeyPayload> {
  return fetchJsonWithBody<ApiKeyPayload>("/settings/api-key/", "DELETE");
}


export async function fetchFavorites(): Promise<FavoriteListPayload> {
  return fetchJson<FavoriteListPayload>("/favorites/");
}


export async function toggleFavorite(arxivId: string): Promise<FavoriteTogglePayload> {
  return fetchJsonWithBody<FavoriteTogglePayload>("/favorites/toggle/", "POST", { arxiv_id: arxivId });
}
