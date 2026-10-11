import { TestBed } from '@angular/core/testing';

import { ChecklistItem } from '../../models/optimizer';
import { ItemCardComponent } from './item-card.component';

const item: ChecklistItem = {
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
  yields: [
    { item_id: 'arc_circuitry', name: 'Arc Circuitry', quantity: 2, context: 'in_stash' },
    { item_id: 'arc_circuitry', name: 'Arc Circuitry', quantity: 1, context: 'in_raid' },
  ],
};

describe('ItemCardComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ItemCardComponent],
    }).compileComponents();
  });

  it('should render name, quantity, and badge', () => {
    const fixture = TestBed.createComponent(ItemCardComponent);
    fixture.componentInstance.item = item;
    fixture.detectChanges();
    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('Metal Parts');
    expect(text).toContain('x8');
    expect(text).toContain('Ammo Essential');
  });
});
