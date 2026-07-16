# Fetal Oxygen Distribution Model

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21384344.svg)](https://doi.org/10.5281/zenodo.21384344)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

A computational framework for simulating fetal haemodynamics and oxygen distribution in healthy and transposition of the great arteries (TGA) configurations.

The repository combines a closed-loop, zero-dimensional (0D) fetal cardiovascular model with an oxygen transport model. It can be used to investigate how fetal cardiovascular anatomy and physiological adaptations affect blood-flow distribution and oxygen delivery at approximately 36 weeks of gestation.

> **Research use only.** This code is intended for computational research and methodological development. It is not intended for clinical diagnosis, treatment planning, or medical decision-making.

## Main features

* Closed-loop 0D model of the fetal cardiovascular system.
* Healthy and TGA cardiovascular configurations.
* Representation of the main fetal shunts:

  * foramen ovale (FO),
  * ductus arteriosus (DA),
  * ductus venosus (DV).
* Coupling of fetal haemodynamics with oxygen transport and placental oxygen exchange.
* Simulation of cardiovascular adaptations and pathological scenarios, including:

  * reduced FO area,
  * DA constriction,
  * changes in lung size and pulmonary vascular properties,
  * altered DV-to-FO streaming,
  * changes in cerebral vascular properties,
  * ventricular and great-vessel remodelling.
* Storage of simulation results and scenario metadata in NumPy `.npz` files.
* Notebooks for running simulations, visualising outputs, and reading saved results.

## Repository structure

| File or directory             | Description                                                                                    |
| ----------------------------- | ---------------------------------------------------------------------------------------------- |
| `Healthy_O2_simulation.ipynb` | Runs and analyses the healthy fetal hemodynamic and oxygen-distribution model.                |
| `TGA_O2_simulations.ipynb`    | Runs and analyses oxygen-distribution scenarios for fetal TGA.                                 |
| `TGA_flow_simulation.py`      | Performs the hemodynamic parameter sweep used to generate TGA flow inputs.                    |
| `Read_results_npz.ipynb`      | Reads, explores, and visualises saved `.npz` simulation results.                               |
| `default_constants.npz`       | Reference model constants used when modifying physiological parameters.                         |
| `functions_to_import.py`      | Helper functions for parameter scaling, signal processing, plotting, and result analysis.      |
| `Hemodynamic model/`          | CellML models and generated C implementations of the healthy and TGA fetal circulation.        |
| `Oxygen distribution model/`  | CellML models, generated C implementations, and compiled libraries for the healthy and TGA oxygen-distribution models.       |
| `solver/`                     | Python, Cython, and C interface used to compile and solve the generated cardiovascular models. |
| `LICENSE`                     | GNU General Public License v3.0.                                                               |

## Model overview

The hemodynamic component represents the fetal circulation as a network of lumped cardiovascular compartments. The generated C models are wrapped using Cython and solved with the CVode integrator provided by Assimulo.

The oxygen-distribution component combines the simulated blood-flow distribution with oxygen transport calculations. It accounts for oxygen exchange at the placenta, oxygen consumption in fetal tissues, mixing between vascular compartments, and preferential streaming through the fetal shunts.

The TGA simulations allow the combined effects of several adaptations to be explored. In the current batch script, the investigated parameter ranges include:

* FO area: 100% to 20% of the reference value.
* DA diameter: 100% to 60% of the reference value.
* Lung-related scaling: 100% to 175% of the reference configuration.
* DV blood directed toward the FO: 90% to 40%.
* Cerebral vascular scaling: 100% to 115%.
* Associated ventricular and great-vessel remodelling.

Please consult the accompanying publication or thesis for the complete mathematical formulation, parameter definitions, assumptions, and validation.

## Requirements

The safest starting configuration is:

* Python 3.9
* NumPy
* SciPy
* Matplotlib
* JupyterLab or Jupyter Notebook
* Cython
* setuptools
* Assimulo
* A C compiler with C99 support

The repository contains a precompiled Cython extension for Python 3.9 on macOS. On a different Python version or operating system, the extension should be rebuilt locally.

Assimulo is most reliably installed through `conda-forge`.



## Output files

The solver saves results as compressed NumPy archives. Full simulation files may contain:

* simulation time,
* state variables,
* algebraic variables,
* model constants,
* variable and component names,
* scenario-specific parameter values.

The TGA flow summaries include cycle-averaged flows for the placenta, brain, upper body, ductus arteriosus, lungs, aorta, kidneys, liver, intestines, lower body, coronary circulation, and the DV/IVC pathways toward the FO and right atrium.

By default, the model solver stores the final two cardiac cycles of each simulation.

Saved files can be inspected using:

```text
Read_results_npz.ipynb
```

## Recompiling the Cython wrapper

The wrapper normally recompiles the generated model automatically when a `ModelSolver` object is created. It copies the selected C model into `solver/Cython/` and runs:

```bash
python setup.py build_ext --inplace
```

To compile it manually:

```bash
cd solver/Cython
python setup.py build_ext --inplace
cd ../..
```

If compilation fails after changing Python versions, compilers, or operating systems, remove previous build artefacts before rebuilding:

```bash
rm -rf solver/Cython/build
rm -f solver/Cython/computeRates*.so
```

Then rerun the model or the manual compilation command.

## Reproducibility notes

* Run the notebooks and scripts from the repository root unless otherwise specified.
* Preserve the original directory structure, as several scripts use relative paths.
* Confirm that output directories exist before starting batch simulations.
* The units and definitions of each variable are specified in the CellML and generated C model files.
* Compiled `.so` files are platform-dependent and may not be portable between systems.
* Large parameter sweeps can generate many result files and require significant storage.

## Citation

If you use this model or code, please cite:
> Villanueva-Baxarias, I. (2026). Fetal Oxygen Distribution Model [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21384344

A citation for the associated scientific publication should be added once it is available. 

The methodological framework is also described in:

> Villanueva Baxarias, M. I. **Advancing the understanding of congenital heart diseases through computational modeling of the fetal cardiovascular system.** PhD thesis, Universitat Pompeu Fabra, 2026.

## License

This project is distributed under the GNU General Public License v3.0. See `LICENSE` for the full license text.

## Contact

For questions about the model, its assumptions, or its use, please open an issue in this repository.
