import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TransferGoalsComponent } from './transfer-goals.component';

describe('TransferGoalsComponent', () => {
  let component: TransferGoalsComponent;
  let fixture: ComponentFixture<TransferGoalsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TransferGoalsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TransferGoalsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
