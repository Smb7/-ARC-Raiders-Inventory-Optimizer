import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { ItemCardComponent } from '../../components/item-card/item-card.component';
import { ApiService } from '../../core/api.service';
import { SessionStore } from '../../core/session.store';
import { ChecklistItem, OptimizeResult } from '../../models/optimizer';

@Component({
  selector: 'app-dashboard',
  imports: [ItemCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  result: OptimizeResult | null = null;
  deltaMessage = '';
  loading = false;
  error = '';
  checked = new Set<string>();

  constructor(
    private readonly api: ApiService,
    private readonly session: SessionStore,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    if (!this.session.userId) {
      void this.router.navigateByUrl('/');
      return;
    }
    this.result = this.session.result;
    if (!this.result) {
      this.refresh();
    }
  }

  cardKey(bucket: string, item: ChecklistItem): string {
    return `${bucket}:${item.item_id}:${item.reason}`;
  }

  toggle(bucket: string, item: ChecklistItem): void {
    const key = this.cardKey(bucket, item);
    if (this.checked.has(key)) {
      this.checked.delete(key);
    } else {
      this.checked.add(key);
    }
  }

  refresh(): void {
    const userId = this.session.userId;
    if (!userId) {
      return;
    }
    this.loading = true;
    this.error = '';
    const previous = this.session.result;
    this.api.optimizeStash(userId).subscribe({
      next: (result) => {
        this.session.setResult(result);
        this.result = result;
        this.loading = false;
        this.deltaMessage = this.buildDelta(previous, result);
      },
      error: () => {
        this.loading = false;
        this.error = 'Stash refresh failed.';
      },
    });
  }

  buildDelta(previous: OptimizeResult | null, current: OptimizeResult): string {
    if (!previous) {
      return `${current.scanned_count} items scanned.`;
    }
    const added = current.total_quantity - previous.total_quantity;
    const newRecycle = Math.max(0, current.recycle.length - previous.recycle.length);
    const signed = added >= 0 ? `+${added}` : `${added}`;
    return `${signed} items scanned. ${newRecycle} new items ready to recycle.`;
  }
}
