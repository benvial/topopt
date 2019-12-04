#!/usr/bin/env python
import os
import tempfile
import numpy as np
from pytheas import Scatt2D
from pytheas.material import genmat
from pytheas.optim import topopt
from pytheas.tools.utils import between_range

# import matplotlib.pyplot as plt
from appwdgt import *

type_des = "elements"


def get_fem_params():
    ###########################################
    ###############  FEM PARAMETERS  ##########
    ###########################################
    #  instanciate fem model ------------------------------------------
    fem = Scatt2D()
    fem.analysis = "direct"
    fem.lambda0 = wl_box.value
    fem.lambda_mesh = fem.lambda0
    fem.pola = pola_dropdown.value
    fem.theta_deg = angle_slider.value
    fem.h_pml = fem.lambda0
    dpml = fem.lambda0 * 2
    fem.space2pml_L, fem.space2pml_R = fem.lambda0 * 1, fem.lambda0 * 1
    fem.space2pml_T, fem.space2pml_B = fem.lambda0 * 1, fem.lambda0 * 1
    tandelta = 0.002
    epsmin = epsmin_re_box.value + 1j * epsmin_im_box.value
    epsmax = epsmax_re_box.value + 1j * epsmax_im_box.value
    eps_interp = np.array([epsmin, epsmax])
    fem.eps_interp = eps_interp
    fem.eps_des = max(eps_interp)
    fem.eps_incl = 1.0
    fem.eps_host = 1.0  #
    # fem.parmesh_incl = 22
    fem.parmesh = mesh_slider.value
    fem.parmesh_des = fem.parmesh
    fem.parmesh_pml = fem.parmesh * 2 / 3
    fem.gmsh_verbose = 0  #: str: Gmsh verbose (int between 0 and 4)
    fem.getdp_verbose = 0  # : str: GetDP verbose (int between 0 and 4)
    fem.python_verbose = 0  #: str: GetDP verbose (int between 0 and 1)
    fem.type_des = type_des
    fem.quad_mesh_flag = True
    fem.Nix = 55
    fem.inclusion_flag = False
    fem.hx_des = hx_box.value
    fem.hy_des = hy_box.value
    fem.ls_flag = False
    fem.beam_flag = False
    fem.waist = 1.0
    fem.xs = 0
    fem.ys = +fem.hy_des / 2 + fem.lambda0 / 2
    fem.xpp = fem.xs
    fem.ypp = -fem.ys
    fem.target_flag = True
    fem.x_target = target_x_box.value
    fem.y_target = target_y_box.value
    fem.r_target = fem.lambda0 / 20
    return fem


def get_opt_params(fem):
    ###########################################
    ##########  OPTIMIZATION PARAMETERS  ######
    ###########################################
    to = topopt.TopOpt(fem)
    to.type_des = type_des
    to.algorithm = topopt.nlopt.LD_MMA
    to.typeopt = "max"  # type of optimization "min" or "max"
    to.pmin = 0  # minimum value
    to.pmax = 1  # maximum value
    to.m = 1  # interpolation order eps=(eps_min-eps_max)*x^m-eps_min
    to.ptol_rel = 1.0e-12
    to.ftol_rel = 1.0e-16
    to.maxeval = maxeval_slider.value  # maximum of function evaluation
    to.Nitmax = Nitmax_slider.value  # maximum number of global iterations
    to.N0 = 0  # initial global iterations
    to.rfilt = rfilt_box.value  # filter radius
    to.filt_weight = "gaussian"
    to.verbose = 0
    return to


def initialize():
    fem = get_fem_params()
    to = get_opt_params(fem)
    fem.initialize()
    fem.make_mesh()
    xdes, ydes, zdes = fem.des[1].T
    to.nvar = len(fem.des[0])
    if starting_dropdown.value == "constant":
        to.p0 = p0_slider.value * np.ones(to.nvar)
    else:
        to.p0 = np.random.rand(to.nvar)
    return fem, to


def field_interp_grid(self):
    x1 = np.linspace(self.domX_L, self.domX_R, self.Nix)
    y1 = np.linspace(self.domY_B, self.domY_T, self.Niy)
    return x1, y1


def run_fem(fem, to, p, sens_ana=False, filt=True, proj=True):

    to.eps_interp = fem.eps_interp
    fem.adjoint = sens_ana
    G, S = [], []
    epsilon = to.make_epsilon(p, filt=filt, proj=proj)
    fem.path_pos = fem.make_eps_pos(fem.des[0], epsilon)
    fem.compute_solution()
    goal = to.get_objective()
    if sens_ana:
        adjoint = fem.get_adjoint()
        deq_deps = fem.get_deq_deps()
        sens = to.get_sensitivity(p, filt=filt, proj=proj)
    else:
        sens = 0

    return goal, sens


def make_plots(fem, to, p, filt=True, proj=True):
    if to.verbose:
        print("Plotting")

    epsilon = to.make_epsilon(p, filt=filt, proj=proj)
    scatter_conv = conv_plt.data[0]
    scatter_conv.x = np.array(range(to.Nit_tot))
    scatter_conv.y = np.array(to.obj_history)

    ######
    varplot = to.mesh2grid(epsilon.real, interp_method="nearest")
    x_grid, y_grid = to.grid
    coutour_eps = eps_map.data[0]
    coutour_eps.x = x_grid
    coutour_eps.y = y_grid
    coutour_eps.z = varplot

    ######
    fem.postpro_fields()
    u_tot = fem.get_field_map("u_tot.txt")
    E = u_tot.real
    x_grid_map, y_grid_map = field_interp_grid(fem)
    coutour_field = field_map.data[0]
    coutour_field.x = x_grid_map
    coutour_field.y = y_grid_map
    coutour_field.z = E

    # width = 500
    # height = int(width * fem.hy_des / fem.hx_des)
    #
    # eps_map.layout = dict(
    #     width=width,
    #     height=height,
    # )


def main(rm_tmp_dir=True):

    fem, to = initialize()
    p0 = to.p0

    ## objective function
    def f_obj(p, grad, filt=True, proj=True, force_xsym=True):
        if to.verbose:
            print("eval obj func")
        sens_ana = np.size(grad) > 0
        goal, sens = run_fem(fem, to, p, sens_ana=sens_ana, filt=filt, proj=proj)
        if sens_ana:
            grad[:] = sens
        to.param_history.append(p)
        to.obj_history.append(goal)
        to.Nit_tot += 1
        to.Nit_loc += 1
        if to.Nit_tot > 0:
            make_plots(fem, to, p, filt=filt, proj=proj)
        return goal

    ###### MAIN OPTIMIZATION LOOP ############
    popt, opt_f, opt = to.main_loop_topopt(f_obj, p0)
    if to.verbose:
        print("optimum at ", popt)
        print("with value  = ", opt_f)
        print("\n")
        print("Final design")
        print("#" * 60)
    popt_filt, _ = to.filter_param(popt, grad=False)
    p_thres = to.get_threshold_design(popt_filt)
    opt_thres = f_obj(p_thres, np.array([]), filt=False, proj=False, force_xsym=False)
    if to.verbose:
        print("optimum at ", p_thres)
        print("with value  = ", opt_thres)
    if rm_tmp_dir:
        fem.rm_tmp_dir()
    return p_thres, opt_thres


@run_button.on_click
def run_on_click(b):
    main()


app = Box(children=[fem_par, plots])
