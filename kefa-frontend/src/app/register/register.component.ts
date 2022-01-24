import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { RegistrationService, AuthService, AlertService } from '../_services';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
  providers: [RegistrationService]
})
export class RegisterComponent implements OnInit {
  busy: Subscription;
  phoneNumber: string;
  form: FormGroup;
  code: AbstractControl;
  password: AbstractControl;
  volunteerId: AbstractControl;
  submitted: boolean = false;

  constructor(private service: RegistrationService,private router: Router,
              private auth: AuthService,private fb: FormBuilder, private alert: AlertService) { 
          this.setPhoneNumber();
  }

  setPhoneNumber(){
    let phone = localStorage.getItem('identifier')
    if(phone){
      this.phoneNumber = phone;
    }else{
      this.router.navigateByUrl('/register');
    }
  }

  ngOnInit() {
     this.setPhoneNumber();

     this.form = this.fb.group({
      /* code: ['',Validators.compose([
         Validators.required,
         Validators.minLength(6),
         Validators.maxLength(6)
       ])], */
       password: ['',Validators.compose([
         Validators.required,
         Validators.minLength(7),
         Validators.maxLength(36)
       ])],
       volunteerId: ['',Validators.compose([
         Validators.required,
         Validators.minLength(5)
       ])]
     });
     this.code = this.form.controls['code'];
     this.password = this.form.controls['password'];
     this.volunteerId = this.form.controls['volunteerId'];
  }


  handleSubmit() {
    if (this.form.valid && this.phoneNumber) {
       let body  ={
         // code: this.code.value,
          volunteerId: this.volunteerId.value,
          phoneNumber: this.phoneNumber,
          password: this.password.value
       }
      this.busy = this.service.createAccount(body).subscribe(
        (user)=>{
           this.auth.login(this.phoneNumber,this.password.value).subscribe(loggedIn=>{
             localStorage.removeItem('identifier');
             this.router.navigateByUrl('/dashboard');
           })
        },
        (res)=> {
           let {errors} = res.json();
          
           if(errors.code){
             this.code.setErrors({error: errors.code});
           } else if(errors.volunteerId){
            this.volunteerId.setErrors({error: errors.volunteerId});
           }else if(errors.password){
             this.password.setErrors({error: errors.password})
           }else if(errors.form){
            this.alert.error(errors.form)
             
           }else if(errors.phoneNumber){
            this.alert.error(errors.form)
            
           }
        }
      )

    } else {
      this.submitted = true;
    }

  }
  onChange(value) {
    this.service.checkUserExists(value).subscribe(
      ({status}) => {
        return;
      },
      (error) => {
         let {user} = error.json();
              if (user) {
                this.volunteerId.setErrors({ validity: 'Volunteer Id already in use' });
              }
      }
      );
  }



}
