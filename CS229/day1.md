## Supervised Learning（有监督的学习）

- Regression problem **回归问题** 要预测的数值连续
- Classification problem **分类问题** 要预测的问题离散

## lecture1 linear Regression（线性回归）
$$
h(x)=\sum^m_{j=0}\theta_jx_j	 
\\where \ x_0=1
$$
we need to find the **Minimize $\theta$** ，为此，我们定义Theta的成本函数$J(\theta)$
$$
J(\theta)=\frac{1}{2}\sum_{i=1}^{m}(h_\theta(x^{(i)})-y^{(i)})^2
$$
其中 $h_{\theta}(x)=h(x)$
