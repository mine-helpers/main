import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { RegistrationService } from '../../_services/registration.service';

@Component({
  selector: 'app-confirm',
  templateUrl: './confirm.component.html',
  styleUrls: ['./confirm.component.scss'],
  providers: [RegistrationService]
})
export class ConfirmComponent implements OnInit {
  form: FormGroup;
  phoneNumber: AbstractControl;
  submitted: boolean = false;
  isLoading: boolean = false;
  errors: {};

  constructor(private service: RegistrationService,
    private router: Router,
    private fb: FormBuilder) { }

  ngOnInit() {
    localStorage.removeItem('identifier');
    
    this.form = this.fb.group({
      phoneNumber: ['', Validators.compose([
        Validators.required,
        Validators.minLength(9),
        Validators.maxLength(9)
      ])]
    });
    this.phoneNumber = this.form.controls['phoneNumber'];
  }

  handleSubmit() {
    this.isLoading = true;
    if (this.form.valid) {
      
      this.router.navigateByUrl('/create-account');
      let phone = '256' + this.form.controls['phoneNumber'].value;
      localStorage.setItem('identifier',phone);
      /*
     this.service.sendConfirmationCode(phone).subscribe(
        ({identifier})=>{
            localStorage.setItem('identifier',identifier);
            this.router.navigateByUrl('/create-account');
        },
        (errors)=> {
           let {error} = errors.json();
           this.phoneNumber.setErrors({error: error});
        }
     ); */

    } else {
      this.isLoading = false;
      this.submitted = true;
    }

  }
  onChange(value) {
    let phone = '256' + value;
    this.service.checkUserExists(phone).subscribe(
      ({status}) => {
        return;
      },
      (error) => {
         let {user} = error.json();
              if (user) {
                this.phoneNumber.setErrors({ available: 'Phone number already in use' });
              }
      }
      );
  }

}
