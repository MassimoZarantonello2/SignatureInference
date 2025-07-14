
---

## 🎤 Presentation Script: *Identifying Mutational Signatures from Low-Resolution Genomic Data*

---

### Slide 1 – Title Slide

"Hello everyone, my name is Massimo Zarantonello. I'm currently studying Computer Science at the University of Milano-Bicocca, and more recently, I've developed a strong interest in computational biology — a field I hope to pursue further in my career.

Today, I’ll be presenting my work on identifying mutational signatures from low-resolution genomic data.
This project is part of a broader effort aimed at extracting de novo mutational signatures from genomic data, assigning known signatures to new samples, and investigating a key question: How much genomic information do we actually need to reliably recover the mutational processes that shape cancer genomes?"

---

### Slide 2 – The Idea

So, the main goal of this project is to build a model that can predict which mutational signatures are active in a tumor sample, even when we don’t have access to full genomic data.

In real clinical or research situations, having complete whole-genome sequencing (WGS) isn’t always possible — either because it’s too expensive or because the samples are degraded.
So instead of using full WGS, and then reduce the number of mutations — starting from 100% and going down to just 1%.
This helps test how well we can still detect signatures when we only have part of the data.

I focus especially on the 2% level, since that’s roughly what we get from exome sequencing, which is way more common in real cases.

The pipeline works like this:

First, I get the WGS data and compute the trinucleotide mutation counts for each sample.

Then, I set a threshold — basically, I say: if the exposure of a signature is above this value, we consider it active in the sample.

After that, I train a classifier to predict which signatures are active based on the reduced data.

I also compare my method with existing tools that do the same task.

And finally, from the predicted active signatures, I try to estimate the exposure values — which tell us how many mutations come from each signature in each patient.

---

### Slide 3 – What are Mutational Signatures

> Mutational signatures are distinct patterns of somatic mutations left behind by specific biological processes.
> These processes can include exposure to carcinogens, aging, or defects in DNA repair mechanisms.
> Each process tends to leave a characteristic imprint in the genome, and by analyzing these patterns, we can gain insights into the tumor’s history.
> As shown here, a typical representation involves classifying point mutations by their trinucleotide context.

---

### Slide 4 – Structure of the Data

> To ensure robustness and reproducibility, we generate synthetic data across **100 independent identically distributed runs**.
> For each run, we apply the same downsampling scheme, going from 100% to 1%. This structure allows us to perform a large number of comparisons and to evaluate variability across samplings and runs.

---

### Slide 5 – Input Data

> The input to our model is a mutation count matrix.
> Each row corresponds to a sample, and each column to a specific mutation channel, following the SBS-96 format.
> For instance, this row represents one sample at full coverage, with counts for each trinucleotide mutation type.

---

### Slide 6 – Ground Truth

> In parallel, a ground truth matrix was given, where each cell indicates whether a specific mutational signature is active in a given sample using a threshold value of 0 meaning that if a signature has exposure value grater than 0 the signature in that samplle is considered active.
> This is a multi-label prediction task: each sample can have multiple signatures present.
> From my professor Daniele Ramazzotti I obtain a set of 29 distinct signatures with varying probabilities of occurrence from RESOLVE tool.

---

### Slide 8 – Signature Frequency

Before training our model, we examine how frequently each mutational signature occurs across the dataset.
This step provides a baseline understanding of class imbalance, which is crucial for evaluating model performance.

Frequent signatures such as:

S1 — associated with age-related mutagenesis

S2 — linked to APOBEC enzymatic activity

S6 — involved in defective DNA mismatch repair
appear in a large number of samples and are therefore easier for the model to learn.

Rare signatures, including:

S19 — of unclear etiology

S24 — related to aflatoxin exposure
are present in only a small subset of samples, making them significantly harder to predict reliably.

Understanding this imbalance informs our choice of evaluation metrics and helps interpret model performance, especially on low-frequency classes.

---

### Slide 9 – What is the Best Strategy? (Overview)

> We explore several training strategies and the most effecet was the use of an ensemble of models. Since the problem poses as a multi target the model is suppuosed to have a binary vector of 29 elements. But from litterature [add the source] has been proven that the presence of a signature can impat the presence of other, so it could be usefll to have each siganture infulence the predicion of the other.
> First, we compare results using the **default dataset**, both with and without correlation among target signatures. After the ensambels have been trained I extrapolated the models that took part in it togheter with how much of the final results they were accountable for
> Balanced accuracy is used as the main metric, to account for imbalance across classes.

---

### Slide 10 – Correlated Targets – Model Contributions

> With correlated targets, some models perform better than others. 
> Here you can see the position of each base model in the ensemble. So how many times the light model rank first in the ensamble for the prediction of the various sample
> LightGBMXT tends to dominate the top ranks, followed by KNeighbors with distance weighting.

---

### Slide 11 – Uncorrelated Targets – Model Contributions

> When we remove correlation among targets, the ensemble becomes more diversified.
> We see increased contribution from models like RandomForest and CatBoost.
> This variation highlights the importance of dependency structure in multi-label prediction.

---

### Slide 12 – LightGBMXT Summary

Given its strong performance in our experiments, I’d like to briefly explain why LightGBMXT performs so well in this task.

First of all, it uses leaf-wise tree growth, which means it grows the tree by splitting the leaf that will give the largest gain. This often leads to deeper trees and better accuracy compared to traditional level-wise growth.

Then, it uses histogram-based splitting, which speeds up training by grouping continuous feature values into discrete bins — this also reduces memory usage, which is useful for large datasets like ours.

It also uses gradient-based sampling, so instead of training on all the data, it selects the most informative samples based on their gradients — this helps speed up learning without sacrificing accuracy.

Finally, LightGBMXT supports L1 and L2 regularization, which helps prevent overfitting — especially important in our case, where the input matrices are sparse and noisy.

Together, these features make LightGBMXT a really strong choice for our structured input — which, in our case, are matrices of mutation counts across samples and trinucleotide contexts."**

When this is set to true, the algorithm uses what's called extremely randomized trees.
That means that instead of trying multiple split points for each feature, it picks just one random threshold per feature when building the tree.

This does two things:

It speeds up training, because there are fewer computations per node.

And it can help reduce overfitting, since the added randomness acts like a form of regularization.
---

### Slide 13 – Performance Summary per Signature
On the right, we compare the performance across all downsampling levels:
- the ensemble model with correlation features,
- the ensemble model without correlation features, and
- the baseline LightGBMXT model.

We report Balanced Accuracy, F1-score, and Matthews Correlation Coefficient (MCC).
As expected, model performance degrades as the number of mutations decreases:
Balanced Accuracy drops from 0.77 → 0.64
F1-score from 0.756 → 0.565
Mean MCC from 0.575 → 0.34

This decline highlights how low-resolution data limits the model's ability to make reliable predictions, especially for rare signatures and harder classification boundaries.

To assess whether the performance differences are statistically significant, we ran a Friedman test, which resulted in:
χ² = 6.1250, p = 0.0468.

This indicates a statistically significant difference overall.
However, a post-hoc Conover–Friedman test with Holm correction shows that none of the pairwise comparisons reach the significance threshold of 0.05:
This suggests that model performances are broadly comparable, with no significant superiority among them after correction.

---

### Slide 14 – Fit Time Comparison
Although performance differences are minimal, we can base our final choice on model efficiency.
The LightGBMXT model alone requires significantly less training time compared to the ensemble approaches.

Given that we need to train 100 × 16 models in total, fit time becomes a critical factor, making LightGBMXT the most practical and scalable option.

---

### Slide 15 – Final Accuracy Overview

> To conclude the core analysis, here’s the average balanced accuracy per signature across all runs.
> We can see that some signature can be predicted very well across all sampling size such as S5 and S1 keeping a balanced accuracy value higher than 0.85 whereas some signature like S12 recive a value close ti 0.5 meaning that mathcing the one of a random prediction.

---

### Slide 16 
In this slide, we compare Accuracy and Balanced Accuracy across all signatures.

While Accuracy appears consistently higher, this is misleading in imbalanced settings, where frequent signatures dominate the metric.For example, 
S1 shows a major accuracy boost due to its high prevalence.
S19, despite being rarely present, achieves high accuracy simply because the model almost always predicts it as absent.

This discrepancy reveals where the model benefits from class imbalance rather than actual predictive skill.
Comparing these two metrics helps identify underperforming signatures and guides targeted improvements, such as:
- applying oversampling or focal loss,
- or designing separate strategies for rare signatures.

### Slide 17 – How Much Can We Trust the Results?

> To assess the robustness of our predictions, we measure correlations between predicted and true signature profiles across multiple runs and sampling levels.
> This helps ensure that our results are not overly sensitive to stochastic variability in the simulations.

---

### Slide 19
"These plots show how model performance changes as we reduce the sampling level — in other words, as we limit the amount of available mutational data.

As expected, performance drops across all metrics — accuracy, F1-score, and MCC — as sampling decreases from full WGS to just 2% of the data.

My method (default_evaluations.json, shown in blue) does not always achieve the highest accuracy — the reference method (in green) performs slightly better, especially at high sampling levels.
However, when we look at more informative metrics like F1-score and especially MCC, which are more sensitive to class imbalance, my model clearly outperforms the others, particularly in the lower sampling range.

This suggests that, even if it's not the most accurate overall, my method is more robust under low-data conditions, which is exactly the kind of scenario we expect in real-world applications — such as exome sequencing or degraded samples."**z

### Slide 20 – Threshold Experiments

In this experiment, we analyze how varying the classification threshold affects the number of true and false predictions.

We tested multiple threshold splits to evaluate the model’s robustness to different levels of signature expression.
As shown in the distribution on the left, most expression values fall in the 0–0.2 range, so thresholds were chosen to ensure that each bin contains a comparable number of positive samples.
This allows for fair and balanced comparisons across splits.

---

### Slide 21 – Threshold Experiments

As shown in the graph to the right, Balanced Accuracy remains nearly constant across different expression thresholds.

This indicates that the model is robust to variations in signature expression levels, maintaining consistent performance even when the classification cutoff changes.

Such stability is crucial when applying the model in settings where the expression of mutational signatures may vary significantly.
---

### Slide 22 – Comparison with Other Methods
Now let’s take a look at how the three methods compare in terms of performance.

My method clearly shows the most balanced and reliable results.
It achieves the highest F1-score, around 0.74, which reflects a strong balance between precision and recall.
In contrast, SigProfileAssignment shows a very different behavior: it has an extremely high precision, over 93%, but at the cost of a very low recall, just around 17%.
This means that while it rarely makes false positive predictions, it also misses the vast majority of true signatures, which is problematic if recall is important.

MuSiCal performs somewhere in between, but still falls short in both F1 and recall compared to my method.

If we look at overall accuracy, the trend is similar:
My method reaches almost 78%, while MuSiCal and SigProfileAssignment stay below 70% and 64%, respectively.

Finally, when we consider Hamming Loss, which penalizes all types of incorrect predictions across multiple labels, my method again comes out on top, with the lowest error rate.

So overall, the results suggest that my approach not only performs best on paper, but it also offers a more consistent and balanced prediction strategy, which is crucial in real-world applications.

---

### Closing

> To sum up:
>
> * We developed a multi-label classifier for mutational signature prediction from sparse genomic data
> * We tested it across 100 runs and 16 sampling levels
> * And we showed that high accuracy can be maintained even with a fraction of the WGS input
>
> Thank you for your attention! I’d be happy to take any questions.

---