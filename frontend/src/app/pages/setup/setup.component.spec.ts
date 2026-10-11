import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { SetupComponent } from './setup.component';

describe('SetupComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SetupComponent],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('should render workbench controls and hoarding rules', () => {
    const fixture = TestBed.createComponent(SetupComponent);
    fixture.detectChanges();
    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('Scrappy');
    expect(text).toContain('Gunsmith');
    expect(text).toContain('Gear Bench');
    expect(text).toContain('Medical Lab');
    expect(text).toContain('Refiner');
    expect(text).toContain('Never sell base ammo materials');
  });
});
