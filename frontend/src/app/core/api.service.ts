import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ConnectResponse, OptimizeResult, PreferenceUpdate } from '../models/optimizer';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private readonly http: HttpClient) {}

  connect(token: string, rememberMe: boolean): Observable<ConnectResponse> {
    return this.http.post<ConnectResponse>('/api/v1/auth/connect', {
      token,
      remember_me: rememberMe,
    });
  }

  updatePreferences(userId: string, preferences: PreferenceUpdate): Observable<{ status: string }> {
    return this.http.patch<{ status: string }>(`/api/v1/users/${userId}/preferences`, preferences);
  }

  optimizeStash(userId: string): Observable<OptimizeResult> {
    return this.http.post<OptimizeResult>('/api/v1/optimize-stash', { user_id: userId });
  }
}
