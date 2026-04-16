# Geo-MOEA: A Multi-Objective Evolutionary Algorithm with Geo-Obfuscation for Spatial Crowdsourcing

<br>

## Project Description

This repository contains the implementation of Geo-MOEA (Multi-Objective Evolutionary Algorithm with Geo-Obfuscation) and its baseline comparison schemes. It is designed to protect workers' location privacy in Spatial Crowdsourcing (SC) scenarios, realize the trade-off between location privacy protection and SC service quality, and support research and experimental reproducibility in privacy-preserving spatial crowdsourcing computing.

<br>

## Usage

The code consists of four core Python scripts that jointly implement the Geo-MOEA framework and comparative experiments:

<br>

### MOEA.py

Implements the core multi-objective evolutionary algorithm of Geo-MOEA, including population initialization, non-dominated sorting, binary tournament selection, crossover/mutation operations, hypervolume (HV) indicator calculation, and Pareto optimal solution solving. It also integrates baseline experiments (QK-means/DPIVE, single-objective PSO).

<br>

### region_division.py

Implements the binary grid-based large-scale spatial domain partition method, including dataset loading, spatial region segmentation, and region distribution visualization. It provides the foundational spatial division for the Geo-MOEA framework.

<br>

### SC2.py

Implements the local adaptive geo-obfuscation mechanism, including retreat-based K-means clustering, personalized privacy budget allocation, exponential mechanism for pseudo-location generation, and calculation of service quality loss (QLoss) and expected inference error (ExpErr).

<br>

### SC.py 

Implements the baseline DPIVE/QK-means location privacy protection scheme, used as a comparative algorithm to verify the performance advantages of Geo-MOEA.
