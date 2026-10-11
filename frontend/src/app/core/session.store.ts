import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

import { OptimizeResult } from '../models/optimizer';

const USER_KEY = 'arc.userId';
const SETUP_KEY = 'arc.setupComplete';

@Injectable({ providedIn: 'root' })
export class SessionStore {
  private readonly userIdSubject = new BehaviorSubject<string | null>(localStorage.getItem(USER_KEY));
  private readonly resultSubject = new BehaviorSubject<OptimizeResult | null>(null);
  private readonly previousQuantitySubject = new BehaviorSubject<number | null>(null);

  readonly userId$ = this.userIdSubject.asObservable();
  readonly result$ = this.resultSubject.asObservable();
  readonly previousQuantity$ = this.previousQuantitySubject.asObservable();

  get userId(): string | null {
    return this.userIdSubject.value;
  }

  get result(): OptimizeResult | null {
    return this.resultSubject.value;
  }

  get setupComplete(): boolean {
    return localStorage.getItem(SETUP_KEY) === 'true';
  }

  setUserId(userId: string, remember: boolean): void {
    this.userIdSubject.next(userId);
    if (remember) {
      localStorage.setItem(USER_KEY, userId);
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }

  markSetupComplete(): void {
    localStorage.setItem(SETUP_KEY, 'true');
  }

  setResult(result: OptimizeResult): void {
    this.previousQuantitySubject.next(this.resultSubject.value?.total_quantity ?? null);
    this.resultSubject.next(result);
  }
}
