# SignatureInference

Repository per l’inferenza e l’analisi delle **mutational signatures** (SBS) su dati genomici, con workflow che comprende simulazioni, esposizioni, regressione/classificazione e valutazioni.

## Contenuto della cartella

* `logs/` — directory per i log delle esecuzioni e tracking dei run.
* `results/` — output del workflow: metriche, grafici, file di esposizione e classificazione.
* `scripts/` — script principali che avviano gli step del workflow.
* `simulations/` — dati simulati con ground‐truth delle firme (binaria o continua).
* `utils/` — funzioni ausiliarie: parsing, formattazione, metriche, helper vari.
* `README.md` — questo file.
* `presentation.md` — presentazione associata al progetto.
* `run_job.sh`, `run_job.slurm`, `run_job_exposure.slurm` — script di esecuzione batch/cluster (es. Slurm).

## Requisiti

* Python ≥ 3.10
* Librerie principali (esempi):

  ```
  numpy
  pandas
  scikit-learn
  matplotlib
  seaborn
  scipy
  ```
* Ambiente cluster / Slurm se si eseguono i job batch.
* Dati genomici di mutazione o simulazioni pronte.

## Installazione

```bash
git clone https://github.com/MassimoZarantonello2/SignatureInference.git
cd SignatureInference
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(Se manca `requirements.txt`, crealo con le librerie sopra.)*

## Utilizzo

### 1. Simulazione o caricamento dati

Esegui gli script in `simulations/` per generare dati con ground‐truth o caricare dataset reali.

### 2. Esecuzione workflow

Esempio per job singolo:

```bash
./run_job.sh
```

Oppure via Slurm:

```bash
sbatch run_job.slurm
```

Per esposizioni:

```bash
sbatch run_job_exposure.slurm
```

### 3. Risultati

I risultati (classificazioni, regressioni, matrici performance, grafici) si trovano in `results/`.
Puoi poi usarli con gli script in `utils/` per analisi aggiuntive o grafici.

## Struttura del workflow

* Generazione/simulazione matrici delle mutazioni.
* Sampling o elaborazione del dataset (down‐sampling, etc.).
* Predizione della presenza/assenza delle firme (multi‐label classification).
* Stima dell’esposizione alle firme (regressione continua).
* Valutazione: metriche, test statistici, grafici comparativi.

## Risultati attesi

* Valutazione dell’impatto del sampling sulla previsione della presenza di firme.
* Confronto tra metodi di regressione per l’esposizione.
* Grafici: heatmap di similarità, violini di performance, curve di apprendimento.
* Report delle metriche finali e analisi per ipotesi.

## Contributi

1. Fork del progetto.
2. Creare o modificare file/branch.
3. Aprire Pull Request.
4. Discutere issue prima di cambi sostanziali.
