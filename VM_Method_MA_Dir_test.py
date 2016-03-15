from dolfin import *
from MA_Problems import *
import numpy as np

set_log_level(16)


#Values of N for the mesh
params = np.array([4, 8,16,32]);
# params = np.array([16]);

L = len(params);
e = np.zeros([L,1]);
ratio = np.zeros([L,1]);

p = 2;

ep = np.array([1, 1e-2, 1e-3, 0]);
# ep = np.logspace(0,-3,5)

for ii in range(L):
    N = params[ii];
    print(N);



    # Define Problem
    # 1. u(x,y) = x^4 + y^2
    # 2. u(x,y) = exp(.5*(x^2+y^2))
    # 3. u(x,y) = (1/3)(4x^2 + 4y^2)^(3/4)
    # #       Full domain, no function cutoff
    # 4. u(x,y) = (1/3)(4x^2 + 4y^2)^(3/4)
    # #       cutoff domain, no function cutoff
    # 5. u(x,y) = (1/3)(4x^2 + 4y^2)^(3/4)
    # #       Full domain, function cutoff
    # 6. u(x,y) = -sqrt(2 - x^2 - y^2)
    # #       Full domain, function cutoff
    # 7. u(x,y) = abs(x)
    # 8. u(x,y) = x/x^2 piecewise function
    # 9. u(x,y) = sqrt(x^2 + y^2)
    # #       numerical Dirac delta function
    prob = 5;
    (x0, y0, x1, y1, exact, f, gx, gy) = Problems(prob, N);



    # Create mesh and define function space
    mesh = RectangleMesh(Point(x0,y0),Point(x1,y1),N,N)
    V = FunctionSpace(mesh, 'Lagrange', p)
    MixedV = MixedFunctionSpace([V,V,V,V]);



    # Boundaries for the W_xx, W_yy and V spaces
    def Wxx_boundary(x, on_boundary):
        return near(x[0],x0) or near(x[0],x1);
    def Wyy_boundary(x, on_boundary):
        return near(x[1],y0) or near(x[1],y1);
    def V_boundary(x, on_boundary):
        return near(x[1],y0) or near(x[1],y1) or near(x[0],x0) or near(x[0],x1);


    # Boundaries data for integrating <g,\mu>
    class Left(SubDomain):
        def inside(self, x, on_boundary):
            return near(x[0], x0)

    class Right(SubDomain):
        def inside(self, x, on_boundary):
            return near(x[0], x1)

    class Bottom(SubDomain):
        def inside(self, x, on_boundary):
            return near(x[1], y0)

    class Top(SubDomain):
        def inside(self, x, on_boundary):
            return near(x[1], y1)
    left = Left();
    right = Right();
    top = Top();
    bottom = Bottom();
    
    
    
    # Set facet functions and define boundary measures
    boundaries = FacetFunction("size_t", mesh)
    boundaries.set_all(0)
    left.mark(boundaries, 1)
    top.mark(boundaries, 2)
    right.mark(boundaries, 3)
    bottom.mark(boundaries, 4)
    
    ds = Measure("ds")[boundaries]
    
    
    
    




    ##### Loop through epsilon values and solve ####################
    w = Function(MixedV);

    bcv = DirichletBC(MixedV.sub(3), exact, V_boundary)
    for epii in ep:
        print('Epsilon = ',epii)

        bcxx = DirichletBC(MixedV.sub(0), 0.0, Wxx_boundary)
        bcyy = DirichletBC(MixedV.sub(2), 0.0, Wyy_boundary)

        bc = [bcxx,bcyy,bcv]
    
        # Define variational problem
        (Sxx, Sxy, Syy, u) = TrialFunction(MixedV)
        (muxx, muxy, muyy, v) = TestFunction(MixedV)
    
        F = inner(Sxx,muxx)*dx + 2*inner(Sxy,muxy)*dx + inner(Syy,muyy)*dx;

        F += inner(Dx(u,0), Dx(muxx,0))*dx + inner(Dx(u,0), Dx(muxy,1))*dx;
        F += inner(Dx(u,1), Dx(muxy,0))*dx + inner(Dx(u,1), Dx(muyy,1))*dx;

        if(epii != 0):
            F += epii*muxx*dx + epii*muyy*dx;

            F += epii*( inner(Dx(Sxx,0), Dx(v,0)) + inner(Dx(Sxy,0), Dx(v,1)))*dx;
            F += epii*( inner(Dx(Sxy,1), Dx(v,0)) + inner(Dx(Syy,1), Dx(v,1)))*dx;

            F += inner(epii*Sxx + epii*Syy,v)*dx + epii*epii*v*dx;

        # Determinant term/Nonlinear term
        F += inner(Sxx*Syy,v)*dx - inner(Sxy*Sxy,v)*dx;

        F -= (f*v*dx - gy*muxy*ds(1) + gx*muxy*ds(2) + gy*muxy*ds(3) - gx*muxy*ds(4));



        # Solve problem

        R = action(F,w);
        DR = derivative(R, w);
        problem = NonlinearVariationalProblem(R,w,bc,DR);
        solver = NonlinearVariationalSolver(problem);
        prm = solver.parameters
        # prm["nonlinear_solver"] = "snes"
        # prm['snes_solver']['report'] = False;
        # prm["newton_solver"]["absolute_tolerance"] = 1e-13;
        # prm["newton_solver"]["relative_tolerance"] = 1e-13;
        # prm["newton_solver"]["linear_solver"] = "gmres"
        # prm["newton_solver"]["krylov_solver"]["absolute_tolerance"] = 1E-9
        # prm["newton_solver"]["krylov_solver"]["relative_tolerance"] = 1E-7
        # prm["newton_solver"]["krylov_solver"]["maximum_iterations"] = 1000
        # prm["newton_solver"]["krylov_solver"]["monitor_convergence"] = False
        # prm["newton_solver"]["krylov_solver"]["nonzero_initial_guess"] = False
        # prm["newton_solver"]["krylov_solver"]["gmres"]["restart"] = 40
        # prm["newton_solver"]["preconditioner"] = "ilu" # default is "ilu"
        # prm["newton_solver"]["krylov_solver"]["preconditioner"]["structure"]\
        # = "same_nonzero_pattern"
        # prm["newton_solver"]["krylov_solver"]["preconditioner"]["ilu"]["fill_level"] =0
        solver.solve();

        (Sxx,Sxy,Syy,u) = w.split(deepcopy=True);

        error = abs(exact-u)**2*dx
        print('At epsilon = ', epii, ' error = ', np.sqrt(assemble(error)))
  
  
  
  



    (Sxx,Sxy,Syy,u) = w.split(deepcopy=True);

    error = abs(exact-u)**2*dx
    u0 = project(exact,V)
    grad_error = inner(nabla_grad(u0) - nabla_grad(u), nabla_grad(u0) - nabla_grad(u))*dx
    e[ii] = np.sqrt(assemble(error))
    
    if(ii > 0):
        ratio[ii] = np.log(e[ii-1]/e[ii])/np.log(2)
 
# plot(abs(exact-u))
# interactive()
print("Error: ", e)
print("Ratio: ", ratio)
