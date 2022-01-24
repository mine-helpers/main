import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseGoalsComponent } from './purchase-goals.component';

describe('PurchaseGoalsComponent', () => {
  let component: PurchaseGoalsComponent;
  let fixture: ComponentFixture<PurchaseGoalsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PurchaseGoalsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PurchaseGoalsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
