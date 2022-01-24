import { Component, OnInit } from '@angular/core';
import {DashboardHomeComponent} from './dashboard-home/dashboard-home.component';
import {ProfileComponent} from './profile/profile.component';
import {PurchaseGoalsComponent} from './purchase-goals/purchase-goals.component';
import {MobileTopupComponent} from './mobile-topup/mobile-topup.component';
import {LoadDonationTimeComponent}  from './load-donation-time/load-donation-time.component';
import {TransferGoalsComponent} from './transfer-goals/transfer-goals.component';
import {TransactionsComponent} from './transactions/transactions.component';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  currentYear:any;
  constructor() { }

  ngOnInit() {
    this.currentYear = new Date().getFullYear();
  }

}

export const dashboardChildRoutes = [
   {path: '',component: DashboardHomeComponent},
   {path: 'profile',component: ProfileComponent},
   {path: 'purchase-goals',component:PurchaseGoalsComponent},
   {path: 'mobile-topup',component: MobileTopupComponent},
   {path: 'load-donation-time',component: LoadDonationTimeComponent},
   {path: 'transfer-goals', component: TransferGoalsComponent},
   {path: 'transactions', component: TransactionsComponent}
]
