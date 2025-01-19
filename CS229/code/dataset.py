#创建一个线性数据集 服从函数：y=3x+4
import numpy as np
import matplotlib.pyplot as plt

#数据集的样本数
np.random.seed(1)
N = 100
#生成数据集
X = np.random.rand(N, 1)
Y_true = 3 * X + 4
Y = Y_true + np.random.randn(N, 1)*0.3

#绘制数据集
plt.scatter(X, Y, color='blue')
plt.plot(X, Y_true, color='red')
plt.show()

#保存数据集为txt格式
np.savetxt('X.txt', X)
np.savetxt('Y.txt', Y)
np.savetxt('Y_true.txt', Y_true)
