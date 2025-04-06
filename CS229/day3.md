## Decision Trees(决策树)
 Greedy, Top-Down, Recursive Partitioning

对于Region $R_P$ 我们需要寻找他的一个分割$S_P$满足
$$
S_P(j_iT)=(\{ X|X_j<T,X\in R_P\},\{X|X_j>=T,X\in R_P \})
$$
**The question is how to choose the splits?**

We define $L(R):Loss \space on \space R$

交叉信息熵
$L_{cross}=\sum_m\hat{P}_clog_2{\hat{P}_c}$
