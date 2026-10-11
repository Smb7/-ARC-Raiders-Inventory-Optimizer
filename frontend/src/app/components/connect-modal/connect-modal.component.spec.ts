import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { ApiService } from '../../core/api.service';
import { SessionStore } from '../../core/session.store';
import { ConnectModalComponent } from './connect-modal.component';

describe('ConnectModalComponent', () => {
  let api: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    api = jasmine.createSpyObj('ApiService', ['connect']);
    await TestBed.configureTestingModule({
      imports: [ConnectModalComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ApiService, useValue: api },
        SessionStore,
      ],
    }).compileComponents();
  });

  it('should require a token', () => {
    const fixture = TestBed.createComponent(ConnectModalComponent);
    fixture.detectChanges();
    fixture.componentInstance.connect();
    expect(fixture.componentInstance.error).toContain('Enter your ARC Tracker token');
    expect(api.connect).not.toHaveBeenCalled();
  });

  it('should emit connected after a successful scan', () => {
    api.connect.and.returnValue(of({ user_id: 'user-1', remember_me: true }));
    const fixture = TestBed.createComponent(ConnectModalComponent);
    const component = fixture.componentInstance;
    spyOn(component.connected, 'emit');
    component.token = 'abc';
    component.rememberMe = true;
    component.connect();
    expect(api.connect).toHaveBeenCalledWith('abc', true);
    expect(component.connected.emit).toHaveBeenCalled();
  });

  it('should surface connect errors', () => {
    api.connect.and.returnValue(throwError(() => new Error('nope')));
    const fixture = TestBed.createComponent(ConnectModalComponent);
    const component = fixture.componentInstance;
    component.token = 'bad';
    component.connect();
    expect(component.error).toContain('Could not connect');
  });
});
