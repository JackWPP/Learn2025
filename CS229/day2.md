# day2 locally weighted regression（局部加权回归）

we can call it a non-parametric learning algorithm

我们可以将其成为 非参数的学习方法
>非参数学习算法不假设数据服从特定的分布，而是通过数据本身的结构进行建模，常见的例子包括K近邻算法（K-Nearest Neighbors, KNN）和决策树（Decision Trees）等。

在非参数学习的过程当中 我们仍然需要fit $\theta$ to minimize
$$
\sum^m_{i=1}\omega^{(i)}(y^{(i)}-\theta^{T}x^{(i)})^2
$$
其中 $\omega$是权重函数

一种比较常见的写法如下
$$
w^{(i)}=exp(-\frac{(x^{(i)}-x)^2}{2 })
$$
