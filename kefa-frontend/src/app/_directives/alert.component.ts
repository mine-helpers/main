import { Component, OnInit } from '@angular/core';
import {AlertService} from  '../_services/alert.service';

@Component({
  moduleId: module.id,
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent implements OnInit {
    message: any;

    constructor(private alertService: AlertService) { }

    ngOnInit() {
        this.alertService.getMessage().subscribe(message => { 
            this.message = message; 
        });
    }

    deleteMessage(){
        this.alertService.deleteMessage();
        return false;
    }
}




