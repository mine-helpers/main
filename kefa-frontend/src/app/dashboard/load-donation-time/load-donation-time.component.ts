import { Component, OnInit } from '@angular/core';
import { AbstractControl,FormGroup, FormBuilder, Validators} from '@angular/forms'
import {Router} from '@angular/router';
import {TransactionService, AlertService} from '../../_services';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-load-donation-time',
  templateUrl: './load-donation-time.component.html',
  styleUrls: ['./load-donation-time.component.scss'],
  providers: [TransactionService]
})
export class LoadDonationTimeComponent implements OnInit {
  voucher: AbstractControl;
  formErrors: string [];
  submitted: boolean = false;
  form: FormGroup;
  busy: Subscription;

  constructor(private transactionService: TransactionService, 
               private fb: FormBuilder,
               private router: Router,
               private alert: AlertService) { }

  ngOnInit() {
    this.form = this.fb.group({
      voucher: ['',Validators.compose([
        Validators.required,Validators.minLength(14), Validators.maxLength(14)
      ])]
    });

    this.voucher = this.form.controls['voucher'];
  }

  handleSubmit(){
    if(this.form.valid){
       this.busy = this.transactionService.loadVoucher(this.form.value).subscribe(
         ({transaction})=>{
           this.alert.success('Donation time has been loaded successfully');
           this.router.navigateByUrl('/dashboard');
         },
         (errorResponse)=>{
           this.formErrors = new Array<string>();
            let {errors} = errorResponse.json()
            this.alert.error('Donation time has not been loaded successfully');
            if(errors.voucher){
              this.voucher.setErrors({validity: errors.voucher});
            }
            if(errors.form){
              this.form.controls['voucher'].setValue('');
              this.alert.error(errors.form);
            }
         }
       )
    }else{
      this.submitted=true;
    }
  }

}
