import { Component, OnInit } from '@angular/core';
import {AuthService} from '../../_services/auth.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {
  user: any = {}
  constructor(private auth: AuthService,private router: Router) { }

  ngOnInit() {
    this.auth.currentUser.subscribe(user=>this.user = user);
  }

  logout(){
    this.auth.logout();
    this.router.navigateByUrl('/home');
    return false;
  }

}
