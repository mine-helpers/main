import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../_services/auth.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  busy: Subscription;
  form: FormGroup;
  identifier: AbstractControl;
  password: AbstractControl;
  submitted: boolean = false;
  formErrors: string[];
  constructor(private router: Router,
    private auth: AuthService, private fb: FormBuilder) {
  }

  ngOnInit() {

    this.form = this.fb.group({
      identifier: ['', Validators.compose([
        Validators.required
      ])],
      password: ['', Validators.compose([
        Validators.required
      ])]
    });
    this.identifier = this.form.controls['identifier'];
    this.password = this.form.controls['password'];
  }


  handleSubmit() {
    if (this.form.valid) {
      let identifier = '256'+ this.identifier.value,
        password = this.password.value;
        
    this.busy =  this.auth.login(identifier, password).subscribe(
        (loggedIn) => {
          if (loggedIn) {
            this.router.navigateByUrl('/dashboard');
          }
        },
        (error) => {
          let { errors } = error.json();
          this.formErrors = new Array<string>();
          if (errors.form) {
            this.formErrors.push(errors.form);
          } else if (errors.identifier) {
            this.identifier.setErrors({ validity: errors.identifier });
          } else if (errors.password) {
            this.password.setErrors({ validity: errors.password })
          }
        }
      );
    } else {
      this.submitted = true;
    }

  }


}
