# Rayyan csv parser
Restructuring rayyan csv output to extract and order relevant information and labeling decisions. Relevant information is in the context of evaluating the performance of active learning algorithms. 

There are two main files. A python script that can parse all `.csv` files in the working directory. The `.ipynb` gives insight into what which parts of the code do. 

Suggested improvements:

* Retrieve missing doi links (can be done using [this script](https://github.com/asreview/synergy-dataset/blob/461a0f757439c226acbc6bc320359001ecd26c69/scripts/enrich.py))