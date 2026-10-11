import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../core/api.service';
import { SessionStore } from '../../core/session.store';

@Component({
  selector: 'app-connect-modal',
  imports: [FormsModule],
  templateUrl: './connect-modal.component.html',
  styleUrl: './connect-modal.component.css',
})
export class ConnectModalComponent {
  @Output() closed = new EventEmitter<void>();
  @Output() connected = new EventEmitter<void>();

  token = '';
  rememberMe = false;
  status = '';
  error = '';
  loading = false;

  constructor(
    private readonly api: ApiService,
    private readonly session: SessionStore,
  ) {}

  connect(): void {
    this.error = '';
    if (!this.token.trim()) {
      this.error = 'Enter your ARC Tracker token.';
      return;
    }
    this.loading = true;
    this.status = 'Validating token...';
    this.api.connect(this.token.trim(), this.rememberMe).subscribe({
      next: (response) => {
        this.status = 'Token accepted. Opening stash...';
        this.session.setUserId(response.user_id, response.remember_me);
        this.loading = false;
        this.connected.emit();
      },
      error: () => {
        this.loading = false;
        this.status = '';
        this.error = 'Could not connect. Check the token and try again.';
      },
    });
  }
}
