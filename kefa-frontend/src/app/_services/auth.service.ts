import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Observable, BehaviorSubject } from 'rxjs';
import jwtDecode from 'jwt-decode';

@Injectable()
export class AuthService {
  currentUser: BehaviorSubject<any> = new BehaviorSubject(false);
  constructor(private http: Http) {
    this.currentUser.next(this.getUser());
  }

  login(identifier, password): Observable<boolean> {
    return this.http.post('/api/v1.0/auth', { identifier, password })
      .map(res => res.json())
      .map(user => {
        if (user) {
          localStorage.setItem('token', user.token);
          let details = jwtDecode(user.token);
          localStorage.setItem('user', JSON.stringify(details));
          this.currentUser.next(user);
        }
        return !!user;
      });
  }

  logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    this.currentUser.next(false);
  }

  isLoggedIn(): boolean {
    return !!this.getUser();
  }

  getUser() {
    let user = localStorage.getItem('user'),
      token = localStorage.getItem('token');
    if (user && token) {
      return JSON.parse(user);
    }
    return false;
  }

}
