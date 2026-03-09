#meeting #preparation
## 1. Research LLM Errors 

- Huang et al. (2025) [[A Survey on Hallucination in Large Language Models - Principles, Taxonomy, Challenges, and Open Questions]]
  Paper over de verschillende fouten van LLMs, geeft vooral terminologie over welke typen fouten een LLM kan maken. -> Meest relevante zijn de verschillen tussen *fabrications* en *instruction/context incosistencies*
- Vinay (2025) [[Failure Modes in LLM Systems - A System-Level Taxonomy for Reliable AI Applications]]
  Paper over fouten die een LLM kan maken in een productie omgeving. Identificeert 15 verschillende fouten die kunnen gebeuren, relevant voor de pipeline van de newsletter die tot fouten kan leiden. 
- Chen et al. [[FELM - Benchmarking Factuality Eval of LLM]]
  Paper die laat zien waarom ik niet zomaar de informatie in een andere LLM kan stoppen om te verifieren, LLMs zijn nog niet goed genoeg om dit zelf te doen, dus scriptie onderwerp is belangrijk. 

## 2. Knowledge Graphs 
GraphCheck [[GraphCheck - Breaking Long-Term Text Barriers with Extracted Knowledge Graph-Powered Fact-Checking]] en GraphEval [[GraphCheck - Breaking Long-Term Text Barriers with Extracted Knowledge Graph-Powered Fact-Checking]] zijn twee manieren om een Knowledge graph op te zetten. Beide maken ze gebruik van een LLM in de setup of afronding, dus het lijkt me goed om deze twee papers op een manier te combineren, zodat altijd duidelijkheid hebben over de uitkmost en opzet. 

## 3. Online Search Test
**Example 1**
[[Test Example 1 - Noor]] laat zien dat de LLM niet perse zelf informatie genereert, maar de website van Doornroosje "scraped" en dit omzet naar de juiste categorien. Nu we dit weten, kunnen we concluderen dat we opzoek zijn naar *Context Inconsistency* of *Unfaithful Generation* van de paper van Hueng, [[A Survey on Hallucination in Large Language Models - Principles, Taxonomy, Challenges, and Open Questions]]. Dit zou dan gebeuren wanneer de tekst niet goed geintreperteerd wordt. 

In dit geval, wordt nergens het woord "nederpop" genoemd, maar toch weet de LLM dit te linken. DIt is waarschijnlijk omdat de artiesten die gerelateerd zijn ook nederpop doen en er wordt gesproken van "moedertaal" en "nederlandse popscene". 

Verder is het zichtbaar dat de website van Doornroosje hier de informatie in het Nederlands weergeeft, en dat dit omgezet wordt naar het Engels. Dit kan ook implicaties hebben voor het controleren van webdata.  

De zoekopdracht "Noor artiest" laat verder webpaginas gelijk aan die van Doornroosje zien. De search geeft bijvoorbeeld haar optreden in Paradiso en de Melkweg weer. (Twee poppodia in Amsterdam)

**Example 2**
[[Test Example 2 - Jehnny Beth + MARIA ISKARIOT]] laat zien dat bij sommige artiesten er *wel* een genre onderaan de pagina staat en dat de LLM deze dan vervolgens overneemt.  Het laat ook zien dat wanneer er een artiest op de pagina staat, deze direct onder **related artitsts** valt, terwijl dit niet zo door Doornroosje neergezet wordt. 

**Example 3**
[[Test Example 3 - Michael Prins]] laat zien dat als er geen informatie over **related artists** zichtbaar is, dit ook niet weergegeven wordt. Verder laat een online search vooral wikipedia en andere poppodia zien. 


**CONCLUSIE TESTS**
Uit de testen blijkt dat de LLM vooral doet aan *Instruction Inconsistency,* een subtype van een *Faithfulness Hallucination* [[A Survey on Hallucination in Large Language Models - Principles, Taxonomy, Challenges, and Open Questions]], waar deze in Example 2 artiesten uit de tekst toevoegd aan **related_artists** terwijl deze niet zo op de website beschreven stonden.  De LLM verzint dus niet zelf items, maar kan alsnog verkeerde informatie weergeven. 

De teksten van Doornroosje zijn (voornamelijk) Nederlands, dus moet ik kijken naar een manier om Nederlandse en Engelse tekst te kunnen vergelijken. 

## 4. Output Verificatie 
**Related Artist Verificatie**
De paper: [[GATSY - Graph Attention Network for Music Artist Similarity]] geeft een manier om duidelijk de relevante artiesten te checken, zonder LLM werk. Dit zou een goede toevoeging kunnen zijn om **related_artists** te controleren. 

**Summary Verificatie**
Om de summary te kunnen vergelijken, kan ik gebruik maken van XLM-R. [[Unsupervised Cross-lingual Representation Learning at Scale (XLM-RoBERTa)]]  Verder is deze multi talig, wat inhoudt dat het verschil tussen Nederlands en Engels niet uit zou moeten maken. De vraag is wel of deze niet te zwaar/te groot zou kunnen zijn. 

## 5. Vragen
- De LLM controleert de website van Doornroosje, moet ik gaan controleren of de LLM de website van Doornroosje gelezen heeft, of dat de informatie die deze genereert klopt en misschien Doornroosje een fout heeft gemaakt op de website? 
- De artiesten worden van de website gehaald, moet dit ook geverifieerd worden of alleen de summary? 
- Is de XLM-R te groot om voor dit doeleinde te gebruiken? 



