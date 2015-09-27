# HomeCon plugin




## System identification
A method of system identification is implemented in HomeCon. The method requires that several things are measured
### Optimization problem structure
the optimization problem is discretized to N timesteps with length 15 minutes

variables:
everything is treated as a variable but constrained appropriately. The variables are ordered like `[states , inputs , parameters]`

e.g.
```
x = [ T_zon[0] , ... , T_zon[N] ,
      T_emi[0] , ... , T_emi[N] ,
                 ...
      T_amb[1] , ... , T_amb[N] ,
      P_emi[1] , ... , P_emi[N] ,
      P_pro[1] , ... , P_pro[N] ,
      C_zon , C_emi , UA_zon_amb , UA_emi_zon , n_emi , n_pro ] 
```

The numer of variable is thus:
```
nvars = nstates*N + ninputs*N + nparameters
```

cost:
sum of squared errors of the representative zone temperature is taken as cost

e.g. 
```
f = T_zon[0]^2 - 2*T_zon[0]*T_zon_meas[0] + T_zon_meas[0]^2 + 
    ...
    T_zon[N]^2 - 2*T_zon[N]*T_zon_meas[N] + T_zon_meas[N]^2
```
 
constraints: 
constraints are passed as `c_min[j] <= c[j] <= c_max[j]` in the order `[state , algebraic  input , boundaries ]`

e.g.
```
c = [C_zon*(T_zon[1]-T_zon[0])/dt - UA_zon_amb*(T_amb[0]-T_zon[0])  - UA_emi_zon*(T_emi[0]-T_zon[0]) , 
      ...
     C_zon*(T_zon[N]-T_zon[N-1])/dt - UA_zon_amb*(T_amb[N-1]-T_zon[N-1])  - UA_emi_zon*(T_emi[N-1]-T_zon[N-1]) ,
     C_emi*(T_emi[1]-T_emi[0])/dt - UA_emi_zon*(T_zon[0]-T_emi[0]) -n_emi*P_emi[0] ,
      ...
     C_emi*(T_emi[N]-T_emi[N-1])/dt - UA_emi_zon*(T_zon[N-1]-T_emi[N-1]) -n_emi*P_emi[N-1] ,
      ...
     P_emi[0] - n_pro*P_pro[0] , ... , P_emi[N] - n_pro*P_pro[N] ,
      ...
     T_amb[0] - T_amb_meas[0] , ... , T_amb[N] - T_amb_meas[N] ,
      ...
     C_zon , C_emi , UA_zon_amb , UA_emi_zon , n_emi , n_pro ]
```
 
The gradient of the cost function can be defined as:

```
grad_f = np.zeros(nvars,1)
grad_f[0*N+0:0*N+N] = [2*T_zon[0] - 2*T_zon_meas[0] , ... , 2*T_zon[N] - 2*T_zon_meas[N]]
```

The jacobian of the constraint in the example becomes:
```
grad_c = [
```

The Hessian of the constraints lagrangian in the example becomes:
```
hess_l = [
```


