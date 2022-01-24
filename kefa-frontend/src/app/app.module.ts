import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import {BusyModule, BusyConfig} from 'angular2-busy';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import {
  DashboardComponent, ProfileComponent, LoadDonationTimeComponent, MobileTopupComponent,
  DashboardHomeComponent, SideBarComponent, NavigationBarComponent,
  TransactionsComponent, TransferGoalsComponent,PurchaseGoalsComponent, dashboardChildRoutes
} from './dashboard';
import { ConfirmComponent } from './register/confirm/confirm.component';
import { AuthService, AlertService, TransactionService } from './_services';
import { AuthGuard,LoggedOutGuard } from './_guards';
import { NotFoundComponent } from './not-found/not-found.component';
import { AlertComponent } from './_directives/alert.component';

const routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent, canActivate: [LoggedOutGuard] },
  { path: 'login', component: LoginComponent, canActivate: [LoggedOutGuard] },
  { path: 'register', component: ConfirmComponent, canActivate: [LoggedOutGuard] },
  { path: 'create-account', component: RegisterComponent, canActivate: [LoggedOutGuard] },
  { path: 'dashboard', component: DashboardComponent, children: dashboardChildRoutes, canActivate: [AuthGuard] },
  { path: '**', component: NotFoundComponent }
];

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    ConfirmComponent,
    NotFoundComponent,
    TransactionsComponent,
    NavigationBarComponent,
    SideBarComponent,
    DashboardHomeComponent,
    AlertComponent,
    ProfileComponent,
    PurchaseGoalsComponent,
    MobileTopupComponent,
    LoadDonationTimeComponent,
    TransferGoalsComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule.forRoot(routes),
    HttpModule,
    BusyModule,
    BrowserAnimationsModule
  ],
  providers: [AuthService, AuthGuard, LoggedOutGuard, AlertService, TransactionService],
  bootstrap: [AppComponent]
})
export class AppModule { }
