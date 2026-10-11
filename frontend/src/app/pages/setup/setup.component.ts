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
  gunsmithLevel = 0;
  gearBenchLevel = 0;
  medicalLabLevel = 0;
  explosivesLevel = 0;
  utilityLevel = 0;
  refinerLevel = 0;
  researchLevel = 0;
  stashLevel = 0;
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
        gear_bench_level: this.gearBenchLevel,
        medical_lab_level: this.medicalLabLevel,
        explosives_station_level: this.explosivesLevel,
        utility_station_level: this.utilityLevel,
        refiner_level: this.refinerLevel,
        research_station_level: this.researchLevel,
        stash_level: this.stashLevel,
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
