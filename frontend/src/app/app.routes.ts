import { Routes } from '@angular/router';

import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { LandingComponent } from './pages/landing/landing.component';
import { SetupComponent } from './pages/setup/setup.component';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'setup', component: SetupComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: '**', redirectTo: '' },
];
