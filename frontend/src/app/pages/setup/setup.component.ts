import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { ApiService } from '../../core/api.service';
import { SessionStore } from '../../core/session.store';

@Component({
  selector: 'app-setup',
  imports: [FormsModule],
  templateUrl: './setup.component.html',
  styleUrl: './setup.component.css',
})
export class SetupComponent {
  scrappyLevel = 1;
  gunsmithLevel = 1;
  refinerLevel = 1;
  neverSellAmmo = true;
  keepSeeds = true;
  highlightLowDurability = true;
  error = '';
  saving = false;

  constructor(
    private readonly api: ApiService,
    private readonly session: SessionStore,
    private readonly router: Router,
  ) {}

  save(): void {
    const userId = this.session.userId;
    if (!userId) {
      void this.router.navigateByUrl('/');
      return;
    }
    this.saving = true;
    this.error = '';
    this.api
      .updatePreferences(userId, {
        scrappy_level: this.scrappyLevel,
        gunsmith_level: this.gunsmithLevel,
        refiner_level: this.refinerLevel,
        never_sell_ammo_materials: this.neverSellAmmo,
        keep_high_yield_seeds: this.keepSeeds,
        highlight_low_durability_duplicates: this.highlightLowDurability,
      })
      .subscribe({
        next: () => {
          this.session.markSetupComplete();
          this.api.optimizeStash(userId).subscribe({
            next: (result) => {
              this.session.setResult(result);
              void this.router.navigateByUrl('/dashboard');
            },
            error: () => {
              this.saving = false;
              this.error = 'Preferences saved, but stash scan failed.';
            },
          });
        },
        error: () => {
          this.saving = false;
          this.error = 'Could not save calibration.';
        },
      });
  }
}
