# Cost-scaling of large Power-to-Methanol plants supplied with wind power and CO2 from direct air capture: a Chile case study

Tibor Svitnic

## Overview

This repository contains the code and data used for the analysis presented in the paper [Cost-scaling of large Power-to-Methanol plants supplied with wind power and CO2 from direct air capture: a Chile case study by Tibor Svitnic and Kai Sundmacher].


## Installation


### Prerequisites

Ensure you have Python installed (recommended version: 3.8 or higher). It is advised to create a virtual environment before installing dependencies.

Please note: The models are set-up to be solved by the Gurobi solver, so a Gurobi license is required.


```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Then, clone this repository and enter the working folder:

```
git clone https://github.com/tiborsv/max-e-methanol.git
cd max-e-methanol
```

### Install Dependencies

```
pip install -r requirements.txt
```

or simply do

```
conda create --name venv --file requirements.txt
```


## License

This project is licensed under the [MIT License] - see the LICENSE file for details.
