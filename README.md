##AWS Scripts

####identify\_unused\_aws\_resources.py
Search AWS for resources that are not in use, are underutilized, or are legacy resources that could be decommissioned (wasting money!). Outputs an HTML report of its findings. Written in Python 3.5.

####identify\_most\_expensive\_clusters.py
Identify the most expensive clusters in AWS and return a table of results, ranking them from most to least expensive. Useful for making informed decisions about purchasing reserved instances. Pass command-line arguments to tailor output. This script supports execution with both Python 2 and 3.

Example Output:
<pre><code>┌Top 10 Clusters by Cost─────────────────┬──────────────┬─────────────┬────────────────────┬────────────────────┬──────────────────────┬─────────────────────┐
│ Name                                   │ Member Count │ Member Size │ Member Cost (Hour) │ Cluster Cost (Day) │ Cluster Cost (Month) │ Cluster Cost (Year) │
├────────────────────────────────────────┼──────────────┼─────────────┼────────────────────┼────────────────────┼──────────────────────┼─────────────────────┤
│ some-cluster 					         │ 7            │ c4.8xlarge  │ $ 1.675            │ $ 281.40           │ $ 8,442.00           │ $ 101,304.00        │
│ some-other-cluster	                 │ 6            │ c4.8xlarge  │ $ 1.675            │ $ 241.20           │ $ 7,236.00           │ $ 86,832.00         │
│ cluster-number-three					 │ 10           │ c3.4xlarge  │ $ 0.840            │ $ 201.60           │ $ 6,048.00           │ $ 72,576.00         │
│ cluster-number-four         	         │ 8            │ c4.4xlarge  │ $ 0.838            │ $ 160.90           │ $ 4,826.88           │ $ 57,922.56         │
│ cluster-number-five 		             │ 8            │ c4.4xlarge  │ $ 0.838            │ $ 160.90           │ $ 4,826.88           │ $ 57,922.56         │
│ cluster-number-six         		     │ 4            │ c4.8xlarge  │ $ 1.675            │ $ 160.80           │ $ 4,824.00           │ $ 57,888.00         │
│ cluster-number-seven                   │ 10           │ r3.2xlarge  │ $ 0.665            │ $ 159.60           │ $ 4,788.00           │ $ 57,456.00         │
│ cluster-number-eight 			         │ 12           │ m4.2xlarge  │ $ 0.479            │ $ 137.95           │ $ 4,138.56           │ $ 49,662.72         │
│ cluster-number-nine                    │ 10           │ c4.2xlarge  │ $ 0.419            │ $ 100.56           │ $ 3,016.80           │ $ 36,201.60         │
│ cluster-number-ten                     │ 7            │ c4.2xlarge  │ $ 0.419            │ $ 70.39            │ $ 2,111.76           │ $ 25,341.12         │
└────────────────────────────────────────┴──────────────┴─────────────┴────────────────────┴────────────────────┴──────────────────────┴─────────────────────┘</code></pre>