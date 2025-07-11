# BUILDING DIVERSIFIED PORTFOLIOS THAT OUTPERFORM OUT-OF-SAMPLE
*Marcos López de Prado*

---

The paper introduces Hierarchical Risk Parity (HRP) as a remedy for instability, concentration, and poor out-of-sample variance in quadratic optimizers, and demonstrates HRP vs. CLA vs. inverse-variance portfolio (IVP) on 10 simulated series. My first itertaion on the paper is to repeate the demonstration using samples from real data instead of simulated series, and then comparing the results. My data is minute-by-minute OHLC publicly traded stock prices, so there is a significant amount of data stored elsewhere with a sample saved in the data folder.

</br>
</br>

## Paper roadmap and section summaries
| Section                                          | Purpose & key points                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Abstract**                                     | Introduces Hierarchical Risk Parity (HRP) as a remedy for instability, concentration, and poor out-of-sample variance in quadratic optimizers .                                                                                                                                                                                                          |
| **Introduction & Markowitz’s Curse**             | Reviews critical-line algorithm (CLA) history and explains why inverting large, ill-conditioned covariance matrices makes classical optimization unstable. Exhibit 1 visualizes the exploding condition number .                                                                                                                                         |
| **From Geometric to Hierarchical Relationships** | Argues that a complete correlation graph treats every asset as a substitute; replacing it with a tree captures natural hierarchies and stabilizes weights .                                                                                                                                                                                              |
| **HRP Algorithm Overview**                       | Breaks HRP into three deterministic $O(\log N)$ stages:<br>1. **Tree clustering** (single-linkage on a correlation-derived distance) .<br>2. **Quasi-diagonalisation** of the covariance matrix to group similar assets (Code Snippet 1) .<br>3. **Recursive bisection** that splits portfolio weights inversely to cluster variances (Code Snippet 2) . |
| **Numerical Example**                            | Demonstrates HRP vs. CLA vs. inverse-variance portfolio (IVP) on 10 simulated series; HRP achieves lower concentration than CLA and better risk balance than IVP .                                                                                                                                                                                       |
| **Out-of-Sample Monte-Carlo Simulations**        | Repeats portfolio formation 10 000 times with shocks; HRP delivers the lowest out-of-sample variance (≈ –31 % vs. CLA) under identical assumptions .                                                                                                                                                                                                     |
| **Further Research**                             | Suggests extensions: Black-Litterman views, alternative distance metrics, and replacing unstable econometric models (e.g., VAR) with hierarchical analogues .                                                                                                                                                                                            |
| **Conclusions**                                  | Recaps that HRP keeps correlation information, avoids matrix inversion, and is robust to singular covariances – making it attractive for leveraged risk-parity funds .                                                                                                                                                                                   |
| **Appendices A.1–A.4**                           | Provide proofs that the correlation-based distance is a true metric, show why inverse-variance weights are optimal for diagonal covariances, supply fully commented Python code for the example and Monte-Carlo study .                                                                                                                                  |
| **Exhibits**                                     | Visual aids: graph vs. tree, clustered heatmaps, allocation bar-plots, time-series of portfolio weights.                                                                                                                                                                                                                                                 |



---

</br>
</br>
</br>

# Functions in *portfolio_methods.py*
*porfolio_methods.py is the Python script with the core portfolio optimization methods* 

- Inverse-Variance Portfolio (IVP) – traditional “risk-parity” baseline.

- Markowitz minimum-variance portfolio – the classical mean-variance optimiser (the paper calls it CLA, but any constrained min-var solver is equivalent in spirit).

- Hierarchical Risk Parity (HRP) – the three-stage algorithm (tree clustering → quasi-diagonalisation → recursive bisection) reproduced exactly from the paper’s Appendix code snippets.

---

</br>
</br>
</br>

# Running the pipeline end-to-end

## 1) Daily volume-weighted prices
python make_daily_vwap.py raw dlyvolwtd

### 2a) Minute-by-minute log returns
python make_log_returns.py raw mbmlr Close

# 2b) Daily VWMP log returns
python make_log_returns.py dlyvolwtd dlyvolwtdlr VWMP

# 3) Ingest chosen frequency into PostgreSQL  (choose one folder)
python ingest_returns_long_pg.py mbmlr \
    postgresql+psycopg2://mdtuser:Str0ngPwd!@localhost/mdt \
    log_returns

# 4) Optimise portfolios (IVP, GMV, HRP) from PostgreSQL
python run_portfolio_from_pg.py

Swap mbmlr for dlyvolwtdlr (and use a different table name, e.g. log_returns_daily) if you want daily rather than minute data.
