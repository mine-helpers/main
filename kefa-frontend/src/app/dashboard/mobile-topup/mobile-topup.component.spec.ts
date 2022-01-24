import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MobileTopupComponent } from './mobile-topup.component';

describe('MobileTopupComponent', () => {
  let component: MobileTopupComponent;
  let fixture: ComponentFixture<MobileTopupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MobileTopupComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MobileTopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
