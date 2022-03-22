# Abstraction of State Languages in Automata Algorithms

A set of programs and scripts to optimize automata algorithms using various abstractions of automata state languages.

# About
Finite automata are a well-known field of computational theory, and we use them widely in many situations. We will focus our attention to different heuristics for optimizing several typical problems with finite automata. We are interested especially in computation of intersection of automata product construction and its emptiness test, which is time and again required in modern computation technologies, but requires a lot of computational time and generates vast yet unnecessary so-called state space in the end.  For this reason, we will try to use length abstraction for solving these problems and optimizing the product construction and its emptiness test as good as possible using solely knowledge about recognized words lengths.

# Experiments and Results
We have tested various different finite automata, their combinations and often used the same automata with their slightly changed variations to simulate real world examples of usually used automata to see how the optimization algorithm would reduce the generated state space for certain types of automata with their typical qualities.

The complete table with all of our tests and their results and graphs is accessible on [Google Sheets](https://docs.google.com/spreadsheets/d/e/2PACX-1vS889bLFdMRI5-KM6IfjeM_c5EKmSKLG4jfU9Uy5YteUf_yaO0vKfUe5vm5B0keazzVOlsExaEztf4k/pubhtml#) or [Alternative link](https://docs.google.com/spreadsheets/d/1yYntWX8WVISE5ptbfxlIBUCFnFH9OlViT-nkl1b5zZ8/edit?usp=sharing).

We have tested two main aspects:
- First, we have tested the generated state space for emptiness test. That is, whenever we find a solution -- accept state in the intersection, the test ends and we count the amount of generated state space to this moment. If no intersection is found, we end the test when it is certain there is no accept state and the intersection is indeed empty.
- Second, for the same pair of automata, we have tested the full product construction. Adding new accept states along the ways and comparing generated state spaces in the end for the full products accepting the whole intersection of original automata.

## License
Abstraction of State Languages in Automata Algorithms

GPLv3 License \
David Chocholatý \
See [LICENSE](https://github.com/Adda0/optimizing_automata_product_construction_and_emptiness_test/blob/master/LICENSE)

