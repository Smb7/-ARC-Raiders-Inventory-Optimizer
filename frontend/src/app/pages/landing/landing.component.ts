import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { ConnectModalComponent } from '../../components/connect-modal/connect-modal.component';
import { SessionStore } from '../../core/session.store';

@Component({
  selector: 'app-landing',
  imports: [ConnectModalComponent],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.css',
})
export class LandingComponent {
  showModal = false;

  constructor(
    private readonly router: Router,
    private readonly session: SessionStore,
  ) {}

  openConnect(): void {
    this.showModal = true;
  }

  onConnected(): void {
    this.showModal = false;
    const target = this.session.setupComplete ? '/dashboard' : '/setup';
    void this.router.navigateByUrl(target);
  }
}
