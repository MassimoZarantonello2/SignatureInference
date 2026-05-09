# SignatureInference

Repository for the inference and analysis of **mutational signatures** (SBS) on genomic data, covering a full workflow that includes simulations, exposure estimation, regression/classification, and evaluation.

---

## Repository Structure

| Path | Description |
|---|---|
| `logs/` | Execution logs and run tracking |
| `results/` | Workflow outputs: metrics, plots, exposure and classification files |
| `scripts/` | Main scripts that drive the workflow steps |
| `simulations/` | Simulated data with ground-truth signatures (binary or continuous) |
| `tool/` | Inference tool: pre-trained models and `tool.py` entry point |
| `utils/` | Helper functions: parsing, formatting, metrics, etc. |
| `run_job.sh`, `run_job.slurm`, `run_job_exposure.slurm` | Batch/cluster execution scripts (Slurm) |

---

## Requirements

- Python ≥ 3.10
- Core libraries:
  ```
  numpy
  pandas
  scikit-learn
  matplotlib
  seaborn
  scipy
  ```
- A Slurm-compatible cluster environment if running batch jobs.

---

## Installation

```bash
git clone https://github.com/MassimoZarantonello2/SignatureInference.git
cd SignatureInference
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Research Workflow

The repository implements a full research pipeline for mutational signature analysis:

1. **Data generation / loading** — run scripts in `simulations/` to generate synthetic data with known ground-truth signatures, or load real mutation matrices.
2. **Sampling / preprocessing** — down-sampling or other dataset manipulations.
3. **Signature activity prediction** — multi-label classification to predict presence/absence of each signature.
4. **Exposure estimation** — continuous regression to estimate the contribution of each active signature.
5. **Evaluation** — metrics, statistical tests, and comparative plots.

### Running the workflow

Single job:
```bash
./run_job.sh
```

Via Slurm:
```bash
sbatch run_job.slurm       # classification + regression
sbatch run_job_exposure.slurm  # exposure estimation only
```

Results (classifications, regressions, performance matrices, plots) are written to `results/`.

### Expected outputs

- Impact analysis of sampling on signature presence prediction.
- Comparison of regression methods for exposure estimation.
- Plots: similarity heatmaps, performance violin plots, learning curves.
- Final metrics report and hypothesis-driven analysis.

---

## Inference Tool

`tool/tool.py` is a standalone command-line tool that infers active mutational signatures and estimates their exposures from a raw SBS96 mutation count matrix.

It combines a pre-trained multi-label classifier (to detect which signatures are active per sample) with a non-negative least squares (NNLS) solver (to estimate exposure magnitudes), using the selected reference signature matrix.

### Usage

```bash
python tool/tool.py -i <input_file> [options]
```

### Arguments

| Argument | Short | Required | Default | Description |
|---|---|---|---|---|
| `--input` | `-i` | ✅ | — | Path to the mutation count matrix (CSV) |
| `--dataset` | `-d` | ❌ | `default` | Reference signature set: `default`, `cosmic`, `reference` |
| `--sequencing` | `-s` | ❌ | `wgs` | Sequencing type: `wgs` (whole genome) or `wes` (whole exome) |
| `--output` | `-o` | ❌ | `results` | Directory where output files will be saved |

### Input Format

The input CSV must follow the **COSMIC SBS96** format: samples as rows, 96 trinucleotide mutation types as columns. The first column contains the sample ID with no column header.

```
,"A[C>A]A","A[C>A]C",...,"T[T>G]T"
"0009b464-b376-4fbc-8a56-da538269a02f",38,54,...,18
"1a2b3c4d-...",12,7,...,5
```

> The tool expects exactly 96 mutation type columns in standard COSMIC SBS96 channel order.

### Output

The tool writes `exposures.csv` to the output directory. Each row corresponds to a sample and each column to a mutational signature. Values represent the **absolute number of mutations** attributed to each signature.

```
,SBS1,SBS2,SBS3,...
0009b464-...,120,0,45,...
1a2b3c4d-...,0,88,12,...
```

### Examples

WGS data with COSMIC signatures:
```bash
python tool/tool.py -i data/mutation_counts.csv -d cosmic -s wgs -o results/
```

WES data with default signatures:
```bash
python tool/tool.py -i data/mutation_counts.csv -s wes
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Open a Pull Request.
4. Discuss substantial changes in an issue before implementing them.
