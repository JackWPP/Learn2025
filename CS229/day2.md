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

## The First Classification problem

### 逻辑回归 logistic regression

we want $h_{\theta}(x) \in [0,1]$
$$
h_{\theta}(x)=g(\theta^Tx)=\frac{1}{1+e^{-\theta^Tx}}
$$
we can call it "Sigmoid"$g(z)=\frac{1}{1+e^{-z}}$

<center><svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -3 12 6" width="400" height="200">   <!-- 背景网格 -->   <defs>     <pattern id="grid" width="1" height="1" patternUnits="userSpaceOnUse">       <path d="M 1 0 L 0 0 0 1" fill="none" stroke="#eee" stroke-width="0.02"/>     </pattern>   </defs>   <rect x="-6" y="-2" width="12" height="6" fill="url(#grid)"/>      <!-- 坐标轴 -->   <line x1="-6" y1="1" x2="6" y2="1" stroke="black" stroke-width="0.05"/>   <line x1="0" y1="-2" x2="0" y2="4" stroke="black" stroke-width="0.05"/>      <!-- X轴刻度 -->   <g font-size="0.3" text-anchor="middle">     <text x="-4" y="1.4">-4</text>     <text x="-2" y="1.4">-2</text>     <text x="2" y="1.4">2</text>     <text x="4" y="1.4">4</text>   </g>      <!-- Y轴刻度 -->   <g font-size="0.3" text-anchor="start">     <text x="0.1" y="-1">1.0</text>     <text x="0.1" y="3">-1.0</text>     <text x="0.1" y="1.3">0</text>   </g>      <!-- Sigmoid函数曲线 -->   <path d="M -6 2.95             C -5 2.95 -3 2.7 -2 2             C -1 1.3 -0.5 0.5 0 0            C 0.5 -0.5 1 -1.3 2 -2            C 3 -2.7 5 -2.95 6 -2.95"          stroke="#2196F3"          fill="none"          stroke-width="0.1"/>      <!-- 函数标题 -->   <text x="-5.8" y="-2.5" font-size="0.4">g(z) = 1/(1+e^(-z))</text> </svg></center>

### Newton's method
skip

