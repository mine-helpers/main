import { Injectable } from '@angular/core';
import { Http, Headers, RequestOptions, Response } from '@angular/http';

import { User } from '../_models/user';

@Injectable()
export class TransactionService {
    constructor(private http: Http) { }


    getAccountDetails() {
        return this.http.get('/api/v1.0/account', this.jwt())
            .map(res => res.json());
    }

    loadVoucher({ voucher }) {
        return this.http.post('/api/v1.0/load-donation',{code:voucher}, this.jwt())
            .map(res => res.json());
    }

    getAllTransactions() {
        return this.http.get('/api/v1.0/transactions', this.jwt())
            .map((response: Response) => response.json());
    }

    getById(id: number) {
        return this.http.get('/api/users/' + id, this.jwt())
            .map((response: Response) => response.json());
    }

    create(user: User) {
        return this.http.post('/api/users', user, this.jwt())
            .map((response: Response) => response.json());
    }

    update(user: User) {
        return this.http.put('/api/users/' + user.id, user, this.jwt())
            .map((response: Response) => response.json());
    }

    delete(id: number) {
        return this.http.delete('/api/users/' + id, this.jwt())
            .map((response: Response) => response.json());
    }

    // private helper methods

    private jwt() {
        // create authorization header with jwt token
        let token = localStorage.getItem('token');
        if (token) {
            let headers = new Headers({ 'Authorization': 'Bearer ' + token });
            return new RequestOptions({ headers: headers });
        }
    }
}