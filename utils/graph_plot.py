import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def heat_map(rs, f):
    x_labels = rs.sampling_labels
    y_labels = rs.signature_labels

    ra = rs.get_runs_sample_metrics('accuracy')  # shape: [num_runs][num_sampling][num_signature]

    # Converti in array numpy e calcola la media sulle run (asse 0)
    ra = np.array(ra)
    mean_accuracy = np.mean(ra, axis=0)  # shape: [num_sampling][num_signature]

    # Crea un DataFrame per la heatmap
    df = pd.DataFrame(mean_accuracy.T, index=y_labels, columns=x_labels)  # trasposta per avere signature come righe

    plt.figure(figsize=(10, max(0.21 * len(rs.signature_labels),15)))
    ax = sns.heatmap(df, annot=False, fmt=".2f", cmap="viridis")
    plt.xlabel("Sampling Method")
    plt.ylabel("Signature Type")
    plt.title(f"Average Balanced Accuracy for {f}")

    # Annotazioni personalizzate
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            value = df.iloc[i, j]
            color = 'red' if np.isclose(value, 0.5) else 'white'  # usa white o altro colore per il resto
            ax.text(j + 0.5, i + 0.5, f"{value:.2f}", ha='center', va='center', color=color)

    plt.tight_layout()
    plt.show()
    
def plot_standard_deviations(rs, f):
    m = np.array(rs.per_run_balanced_accuracy)
    std = np.std(m, axis=0)
    plt.figure(figsize=(max(0.5 * len(std[0]),15), 6))
    ax = sns.heatmap(std, xticklabels=rs.signature_labels, yticklabels=rs.sampling_labels, cmap='viridis', annot=True, fmt=".2f")
    plt.xlabel("Signature Labels")
    plt.ylabel("Sampling Labels")
    plt.title(f"Standard Deviation of Per-Run Accuracy {f}")
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

def plot_per_run_metric(rs, attr_name="per_run_accuracy", metric_name="Accuracy"):
    metric = getattr(rs, attr_name)
    
    per_run_mean_metric = []
    for i in range(len(metric)):      
        per_sample_mean = []
        for j in range(len(metric[i])):
            per_sample_mean.append(np.mean(metric[i][j]))
        per_run_mean_metric.append(per_sample_mean)
    
    per_run_mean_metric = np.array(per_run_mean_metric)  # shape: (n_runs, n_levels)

    means = per_run_mean_metric.mean(axis=0)
    std_err = per_run_mean_metric.std(axis=0, ddof=1) / np.sqrt(per_run_mean_metric.shape[0])
    conf_interval = 1.96 * std_err  # 95% CI

    plt.errorbar(rs.sampling_labels, means,  marker='o', label=metric_name, capsize=5)
    plt.xticks(rotation=90)
    plt.ylabel(attr_name[8:])
    plt.xlabel("Sampling Level")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
def per_sample_signature_metric(rs, attr_name="per_run_balanced_accuracy", metric_name="Balanced Accuracy"):
    metric = getattr(rs, attr_name)


    
def plot_violins(re):
    plt.figure(figsize=(20, 10))
    per_run_accuracy = np.array(re.per_run_accuracy)
    plt.xlabel('Sampling')
    plt.xticks(range(1, len(re.sampling_labels) + 1), re.sampling_labels, rotation=90)
    plt.ylabel('Accuracy')
    plt.title('Violin Plot of Accuracy Across Runs')
    plt.violinplot([per_run_accuracy[:, j, :].flatten() for j in range(len(re.sampling_labels))], showmeans=True, showmedians=True, showextrema=True)
    
def plot_boxplot_accuracy_by_sampling(rss, files):
    data = []
    runs = {}
    for rs, name in zip(rss, files):
        runs[name] = rs

    for run_name, run_obj in runs.items():
        for samp_idx, sampling in enumerate(run_obj.sampling_labels):
            accs = run_obj.per_run_accuracy[0][samp_idx]  # solo un run per oggetto
            for acc in accs:
                data.append({
                    'sampling': sampling,
                    'balanced_accuracy': acc,
                    'run': run_name
                })

    df = pd.DataFrame(data)

    plt.figure(figsize=(14, 6))
    sns.boxplot(x='sampling', y='balanced_accuracy', hue='run', data=df)
    plt.xticks(rotation=90)
    plt.title('Balanced Accuracy per Sampling Level (per Signature)')
    plt.tight_layout()
    plt.show()
    
def get_signature_mean_per_run(re, label):
    # Ottieni la lista delle signature
    signature_labels = re.signature_labels
    sig_acc = {sig: [] for sig in signature_labels}

    for run in re.per_run_accuracy:
        for sig_idx, sig in enumerate(signature_labels):
            # Media sui livelli di sampling
            sig_bal_acc = np.mean([sampling[sig_idx] for sampling in run])
            sig_acc[sig].append(sig_bal_acc)

    return pd.DataFrame(sig_acc, index=[label])

def plot_signature_heatmap(rss, files):
    runs = {}
    for rs, name in zip(rss, files):
        runs[name] = rs

    # Preparo la struttura per il DataFrame
    data = { run_name: [] for run_name in runs }
    signatures = rss[0].signature_labels

    for run_name, run_obj in runs.items():
        # per ogni signature, raccolgo tutte le balanced_accuracy su tutti i sampling
        for sig_idx, sig in enumerate(signatures):
            vals = []
            for samp_idx in range(len(run_obj.sampling_labels)):
                vals.append(run_obj.per_run_accuracy[0][samp_idx][sig_idx])
            data[run_name].append(np.mean(vals))

    df = pd.DataFrame(data, index=signatures)

    # Plotto la heatmap
    plt.figure(figsize=(8,10))
    sns.heatmap(df, annot=True, fmt=".3f", cbar_kws={'label': 'Mean Balanced Accuracy'})
    plt.title('Mean Balanced Accuracy per Signature e Run')
    plt.ylabel('Signature')
    plt.xlabel('Run strategy')
    plt.tight_layout()
    plt.show()
    
def plot_evaluation_ensamble(rs):
    fig, axes = plt.subplots(4, 4, figsize=(60, 30))
    axes = axes.flatten()

    for plot_idx, sampling in enumerate(rs.sampling_labels):
        rows = []
        for i, sig in enumerate(rs.signature_labels):
            df = pd.DataFrame(rs.evaluations_df['run_1'][sampling][i]['ensemble_info'])
            for _, row in df.iterrows():
                rows.append({
                    'signature': sig,
                    'model': row['model_name'],
                    'val_score': row['val_score']
                })
            rows.append({
                'signature': sig,
                'model': 'total_accuracy',
                'val_score': rs.evaluations_df['run_1'][sampling][i]['best_model_val_score']
        })

        # Genera il grafico per il subplot corrente
        df_plot = pd.DataFrame(rows)
        processed = []

        for sig, group in df_plot.groupby('signature'):
            sorted_group = group.sort_values('val_score')
            prev = 0
            for _, row in sorted_group.iterrows():
                height = row['val_score'] - prev
                processed.append({
                    'signature': sig,
                    'model': row['model'],
                    'height': height
                })
                prev = row['val_score']

        df_stacked = pd.DataFrame(processed)
        # Pivot e riordino delle colonne
        df_pivot = df_stacked.pivot_table(index='signature', columns='model', values='height', fill_value=0)
        df_pivot.plot(kind='bar', stacked=True, colormap='Dark2', ax=axes[plot_idx])
        axes[plot_idx].set_title(f"Sampling: {sampling}")
        axes[plot_idx].set_ylabel("Max Validation Score")
        axes[plot_idx].set_xlabel("Signature")
        axes[plot_idx].legend(title="Model", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()

def plot_all_signature_all_sampling_graph(re, folder_name=None, bins = False):
    per_run_accuracy = np.array(re.per_run_balanced_accuracy)
    mean_accuracy = np.mean(per_run_accuracy, axis=0)

    fig, ax1 = plt.subplots()
    plt.title('Average Balanced Accuracy per Signature (Averaged Across Runs)')
    # Plotta la media per ogni campione (dimensione j di per_sample_accuracy)
    for j in range(len(mean_accuracy)):
        plt.plot(re.signature_labels, mean_accuracy[j], marker='o', label=re.sampling_labels[j])

    legend = fig.legend(re.sampling_labels, )
    legend.set_loc('outside upper right')
    ax1.set_xlabel('Signature')
    ax1.set_xticks(ax1.get_xticks())
    ax1.set_xticklabels(ax1.get_xticks(), rotation=45, ha='right')
    ax1.set_ylabel('Average Accuracy')
    if bins:
        ax2 = ax1.twinx()
        signature_gt_path = f'../simulations/ground_truth{folder_name}/bin_exposures.csv'
        signature_gt_df = pd.read_csv(signature_gt_path)
        active_segnature = signature_gt_df.iloc[:, 1:].sum()
        active_segnature.plot(kind='bar', alpha=0.7, color='gray', ax=ax2)
        ax2.set_ylabel('Number of samples for segnature')
        
    fig.set_figheight(10)
    fig.set_figwidth(max(0.25 * len(active_segnature),15))
    plt.tight_layout()
    plt.show()
    
    
from scipy.stats import pearsonr
def plot_correlation_scatter_plot(rs, attr_name, ground_truth, gt_name):
    metric = getattr(rs, attr_name)
    signature_gt_path = f'../simulations/ground_truth{ground_truth}/bin_exposures.csv'

    signature_gt_df = pd.read_csv(signature_gt_path)
    active_segnatures = signature_gt_df.iloc[:, 1:].sum()
    averaged_accuracy = np.mean(np.mean(np.array(metric), axis = 0), axis = 0)
    df = pd.DataFrame({
        'Signature Activity': active_segnatures.values,
        'Average Accuracy': averaged_accuracy
    })

    # Plot
    plt.figure(figsize=(8, 6))
    r, p = pearsonr(df['Signature Activity'], df['Average Accuracy'])
    plt.text(0.05, 0.95, f'r = {r:.3f}, p = {p:.3g}', transform=plt.gca().transAxes, 
         verticalalignment='top', fontsize=12, bbox=dict(facecolor='white', alpha=0.6, edgecolor='gray'))
    sns.scatterplot(data=df, x='Signature Activity', y='Average Accuracy')
    sns.regplot(data=df, x='Signature Activity', y='Average Accuracy', ci=None, scatter_kws={"s": 60})
    plt.title(f'Correlation between Signature Balanced Activity and Accuracy for {gt_name}')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
