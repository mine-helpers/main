import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {Http} from '@angular/http';

@Injectable()
export class RegistrationService {

  constructor(private http: Http) { }
   
  createAccount(body): Observable<any>{
    return this.http.post('api/v1.0/create-account',body).map(res=>res.json());
  }

  sendConfirmationCode(phoneNumber): Observable<any>{
    return this.http.get(`api/v1.0/send-confirmationcode/${phoneNumber}`)
               .map(res=>res.json());
  }
  checkUserExists(value):Observable<any>{
    return this.http.get(`api/v1.0/check-user/${value}`)
               .map(res=>res.json());
              
  }
}
