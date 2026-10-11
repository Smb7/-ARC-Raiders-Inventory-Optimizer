import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { SessionStore } from '../../core/session.store';
import { OptimizeResult } from '../../models/optimizer';
import { DashboardComponent } from './dashboard.component';

const result: OptimizeResult = {
  keep: [
    {
      item_id: 'metal_parts',
      raw_id: 'metal_parts',
      name: 'Metal Parts',
      category: 'material',
      rarity: 'gray',
      quantity: 8,
      weight: 0.2,
      vendor_sell_price: 50,
      durability: null,
      known: true,
      reason: 'Ammo Essential',
      badge: 'Ammo Essential',
      yields: [],
    },
  ],
  recycle: [],
  sell: [],
  scanned_count: 1,
  total_quantity: 8,
};

describe('DashboardComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting(), SessionStore],
    }).compileComponents();
    const store = TestBed.inject(SessionStore);
    store.setUserId('user-1', false);
    store.setResult(result);
  });

  it('should render kanban columns', () => {
    const fixture = TestBed.createComponent(DashboardComponent);
    fixture.detectChanges();
    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('Keep');
    expect(text).toContain('Recycle');
    expect(text).toContain('Sell');
    expect(text).toContain('Metal Parts');
    expect(text).toContain('Refresh Stash');
  });

  it('should build a delta banner', () => {
    const fixture = TestBed.createComponent(DashboardComponent);
    const message = fixture.componentInstance.buildDelta(result, {
      ...result,
      total_quantity: 50,
      recycle: [
        {
          ...result.keep[0],
          item_id: 'broken_arc_module',
          name: 'Broken Arc Module',
          reason: 'Yield Value',
          badge: 'Yield Value',
        },
      ],
    });
    expect(message).toContain('+42 items scanned');
    expect(message).toContain('1 new items ready to recycle');
  });
});
