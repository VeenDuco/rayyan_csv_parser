# Rayyan csv parser
Restructuring rayyan csv output to extract and order relevant information and labeling decisions. Relevant information is in the context of evaluating the performance of active learning algorithms. 

There are two main files. A python script that can parse all `.csv` files in the working directory. The '.ipynb' gives insight into what which parts of the code do. 

Note. Scripts need to be improved to:

* Retrieve pubmed ID or DOI
* Find screening conclusions that are not in the notes column but jumped around the file. This seems to be an issue that sometimes occurs for some rows. The labelling decisions need to be traced in the files before throwing away columns.