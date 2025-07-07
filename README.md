Daniele Ramazzotti
10:08
https://github.com/AlexandrovLab
https://github.com/AlexandrovLab/SigProfilerExtractor
https://github.com/AlexandrovLab/SigProfilerAssignment
Daniele Ramazzotti
10:10
https://www.nature.com/articles/s41467-020-17388-x
https://www.nature.com/articles/s41588-024-01659-0


                 Welcome to New DC Cluster, University of Toronto               
     !!!! Visit http://itwiki.ccbr.utoronto.ca/index.php/Clusters for lastest updates !!!!
      !!!! Please SUBMIT JOBS to cluster with sbatch, srun, salloc whenever possible !!!!

****** Brief Info & Notes ******
1). 8 Compute+1 Master nodes, compute nodes have 68 Cores, 272 threads, 200GB RAM, OS RHEL9
2). 28TB SSD Storage, 8 partitions, /home[2,3,5,6], /scrtach[1,4,7,8]
3). Scratch storage available for everyone per request with reasonable time line
4). Slurm cluster, use sbatch, srun, salloc, scancel, sinfo, squeue, scontrol to manage jobs
5). PBS compatible scripts, try qsub, qstat, qdel, qhold, qalter, qrerun, qrls, pbsnodes 
6). Master node: dc10, DO NOT RUN CPU/MEMORY INTENSIVE processes on master
7). Slave nodes: dc[01-08], recommended to login & work on slaves
8). Change password, run "passwd" on master node, change 2b propagated to nodes in 1 hour
9). List of some installed apps
    R-4.4.2 https://www.r-project.org/
    Bioconductor-3.19 https://www.bioconductor.org
    Boltz-1/Alphafold3 https://github.com/jwohlwend/boltz 
    Localcolabfold/Alphafold2.3 https://github.com/YoshitakaMo/localcolabfold
    Chrombpnet https://github.com/kundajelab/chrombpnet
    Rstudio Server https://posit.co/, access at http://dc0N.ccbr.utoronto.ca
    Singularity https://github.com/sylabs/singularity
    Cellprofiler4 https://cellprofiler.org/
    Python-3.9 (System) and 3.12 (Conda) https://www.python.org/
    Miniconda https://docs.anaconda.com/miniconda/
    Perl-5.38.2 https://www.perl.org/
    BioPerl-1.7.8 https://bioperl.org/
    Go-1.23.2 https://go.dev/
    aws-cli & google-cloud-cli https://aws.amazon.com/cli & https://cloud.google.com/sdk
    Java openjdk https://www.java.com/
    Samtools, Bcftools, Htslib, Parallel
10). Limited 2 ssh login sessions on each node per user
11). Email support@rt.ccbr.utoronto.ca or jeffs.liu@utoronto.ca for questions & help
===============================================================================================
Last login: Fri Jul  4 16:50:44 2025 from 192.168.182.25
Identity added: /home/baderlab/mzarant/.ssh/toronto_git_key (m.zarantonello2@campus.unimib.it)
[mzarant@dc01 ~]$ 


