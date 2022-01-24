import { Component, OnInit, Input } from '@angular/core';
import {AlertService, TransactionService} from '../../_services';
import {IBusyConfig} from 'angular2-busy';
import {Subscription} from 'rxjs';


@Component({
  selector: 'app-dashboard-home',
  templateUrl: './dashboard-home.component.html',
  styleUrls: ['./dashboard-home.component.scss']
})
export class DashboardHomeComponent implements OnInit {
  accountNumber: string;
  accountName: string;
  accountBalance: string;
  goalBalance: string;
  vsseBalance: string;
  phoneNumber: string;
  transactions: Array<Object>;
  busy: Subscription;

  constructor(private alert:AlertService,private transactionSvc: TransactionService) {
     this.transactions = new Array<Object>();
    }

  ngOnInit() {
    this.busy = this.transactionSvc.getAccountDetails().subscribe(
      ({account, transactions})=>{
        //console.log(account);
        this.accountBalance = account.accountBalance;
        this.accountNumber  = account.accountNumber;
        this.goalBalance = account.goalsBalance;
        this.phoneNumber = account.phoneNumber;
        this.vsseBalance = account.vsseBalance;
        this.transactions = transactions;

      },
      (error)=>{
        console.log(error.json());
      }
    );
  }

}
