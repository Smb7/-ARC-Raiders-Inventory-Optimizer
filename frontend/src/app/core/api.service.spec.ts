import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), ApiService],
    });
    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('should connect with a token', () => {
    service.connect('tok', true).subscribe((response) => {
      expect(response.user_id).toBe('u1');
    });
    const req = http.expectOne('/api/v1/auth/connect');
    expect(req.request.body).toEqual({ token: 'tok', remember_me: true });
    req.flush({ user_id: 'u1', remember_me: true });
  });

  it('should optimize a stash', () => {
    service.optimizeStash('u1').subscribe((result) => {
      expect(result.scanned_count).toBe(0);
    });
    const req = http.expectOne('/api/v1/optimize-stash');
    expect(req.request.body).toEqual({ user_id: 'u1' });
    req.flush({ keep: [], recycle: [], sell: [], scanned_count: 0, total_quantity: 0 });
  });
});
