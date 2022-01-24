import { Injectable } from '@angular/core';
import { CanActivate } from '@angular/router';
import { Observable } from 'rxjs/Observable';
import {AuthService, AlertService} from '../_services';
import {Router} from '@angular/router';

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private auth:AuthService,private router: Router,
              private alert: AlertService){}


  canActivate(): Observable<boolean> | Promise<boolean> | boolean {
    let loggedin = this.auth.isLoggedIn();
    if(loggedin){
      return true;
    }else{
      this.alert.error('Login to access this page');
      this.router.navigateByUrl('/login');
    }
  }
}
