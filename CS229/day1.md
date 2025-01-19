## Supervised Learning（有监督的学习）

- Regression problem **回归问题** 要预测的数值连续
- Classification problem **分类问题** 要预测的问题离散

## lecture1 linear Regression（线性回归）

### 前置定义

$$
h(x)=\sum^m_{j=0}\theta_jx_j	 
\\where \ x_0=1
$$
we need to find the **Minimize $\theta$** ，为此，我们定义Theta的成本函数$J(\theta)$
$$
J(\theta)=\frac{1}{2}\sum_{i=1}^{m}(h_\theta(x^{(i)})-y^{(i)})^2
$$
其中 $h_{\theta}(x)=h(x)$

### 梯度下降算法

在成本函数的基础上，我们定义**梯度下降**算法，对于$\theta$进行更新，本质是逐步最小化成本函数$J(\theta)$

梯度下降通过更新参数向量$\theta$来逐步最小化成本函数。更新规则为：
$$
\theta=\theta-\alpha\nabla_{\theta}J(\theta)
$$


为了使用梯度下降，我们需要计算成本函数 $ J(\theta) $ 关于参数 $ \theta $ 的梯度 $\nabla_\theta J(\theta)$。首先，我们对任一参数 $\theta_j$ 求偏导数：
$$
 \frac{\partial}{\partial \theta_j} J(\theta) = \frac{\partial}{\partial \theta_j} \left( \frac{1}{2} \sum_{i=1}^{m} (h_\theta(x^{(i)}) - y^{(i)})^2 \right) 
$$
利用链式法则，可以推导出：
$$
\frac{\partial}{\partial \theta_j} J(\theta) = \sum_{i=1}^{m} \left( h_\theta(x^{(i)}) - y^{(i)} \right) \cdot \frac{\partial}{\partial \theta_j} h_\theta(x^{(i)}) 
$$

由于 
$$
h_\theta(x^{(i)}) = \theta^T x^{(i)} = \sum_{j=0}^{n} \theta_j x_j^{(i)} 
$$
因此：
$$
\frac{\partial}{\partial \theta_j} h_\theta(x^{(i)}) = x_j^{(i)} 
$$

将其代入到偏导数表达式中：
$$
\frac{\partial}{\partial \theta_j} J(\theta) = \sum_{i=1}^{m} \left( h_\theta(x^{(i)}) - y^{(i)} \right) x_j^{(i)}
$$

将上述结果带入到梯度下降的更新公式中，对所有参数 $\theta_j$ $(j = 0, 1, \ldots, n)$进行更新：
$$
\theta_j := \theta_j - \alpha \sum_{i=1}^{m} \left( h_\theta(x^{(i)}) - y^{(i)} \right) x_j^{(i)} 
$$

通过不断迭代这个更新过程，我们能够使成本函数 $J(\theta)$ 降低，从而找到使 $J(\theta)$ 最小的参数向量$\theta$




>*数学相关的知识已经遗忘干净，暂时先不过多追究了，有时间再多花时间处理处理推导推导*
