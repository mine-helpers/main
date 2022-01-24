import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LoadDonationTimeComponent } from './load-donation-time.component';

describe('LoadDonationTimeComponent', () => {
  let component: LoadDonationTimeComponent;
  let fixture: ComponentFixture<LoadDonationTimeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LoadDonationTimeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LoadDonationTimeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
