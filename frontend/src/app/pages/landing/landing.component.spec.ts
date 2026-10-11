import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { LandingComponent } from './landing.component';

describe('LandingComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LandingComponent],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('should render the value proposition and CTA', () => {
    const fixture = TestBed.createComponent(LandingComponent);
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('h1')?.textContent).toContain('Clean Your Stash in Seconds');
    expect(el.textContent).toContain('Connect Stash / Get Started');
    expect(el.textContent).toContain('read-only');
  });

  it('should open the connect modal', () => {
    const fixture = TestBed.createComponent(LandingComponent);
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    button.click();
    fixture.detectChanges();
    expect(fixture.componentInstance.showModal).toBeTrue();
    expect(fixture.nativeElement.querySelector('app-connect-modal')).toBeTruthy();
  });
});
