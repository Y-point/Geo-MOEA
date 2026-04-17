# Project Description
This repository contains the implementation of Geo-MOEA (Multi-Objective Evolutionary Algorithm with Geo-Obfuscation) and its comparative experiments, which is proposed for location privacy protection in Spatial Crowdsourcing (SC) scenarios. The framework integrates geo-indistinguishability, local differential privacy and multi-objective evolutionary optimization to achieve the trade-off between location privacy preservation and service quality, supporting research and experimental reproducibility in privacy-preserving spatial crowdsourcing computing.
<br>

# Usage
The repository contains core code files of Geo-MOEA and its dependent modules, with the following functions:

- `MOEA_6.py`: The main program of Geo-MOEA, which implements the complete algorithm flow including population initialization, fast non-dominated sorting, genetic crossover & mutation, Pareto optimal solution generation, hypervolume (HV) calculation, comparative experiments with QK-means and PSO, as well as result visualization.

- `region_division.py`: Implements binary grid partition of large-scale spatial location domains, including spatial dataset loading, location distribution visualization and adaptive region division to generate suitable cell units for location obfuscation.

- `L-SRR`: The `L-SRR` folder contains a reproduction of the L-SRR scheme proposed by Wang et al. 
