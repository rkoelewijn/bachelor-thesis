The project would work as follows: 

**1. Extract data**
The newsletter would output a certain concert :
````
**Main Act:** Jehnny Beth
**Related Artists:** Gorillaz, Bobby Gillespie ... 
````

**2. Open Web Index**
We query the OWI to fetch pages mentioning the artists. 

**3. Evaluation**
We set up a artist graph, and load it with the articles from the OWI. 
Then we use a Knowledge Graph Embedding (GATSY (?) ) and calculate Link Prediction Score
and use it to get a similarity score. 


