import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error
#加载数据
x=np.loadtxt('CS229\code\X.txt',dtype=float)
y=np.loadtxt('CS229\code\Y.txt',dtype=float)
#对于x,增加一列,用于存放常数项,即theta0
X_b=np.c_[np.ones((len(x),1)),x]
#将y转换为列向量
y=y.reshape(-1,1)
#测试数据加载是否正确 打印各个数据的维度
print(x.shape)
print(y.shape)
print(X_b.shape)

#定义损失函数
def cost_function(x,y,theta):
    m=len(y)
    h_theta=x.dot(theta)
    #根据定义的损失函数公式计算损失
    J_theta=(1/(2*m))*np.sum(h_theta-y)**2
    return J_theta
#梯度下降函数
#aplha:学习率,iterations:迭代次数,x:特征矩阵,y:标签矩阵
def gradient_descent(x, y, alpha, iterations):
    m, n = x.shape
    theta = np.zeros((n, 1))
    print(theta.shape)
    cost_history = np.zeros(iterations)  # 修改为数组存储
    theta_history = []
    
    y=y.reshape(-1,1)
    print("开始训练...")
    for i in range(iterations):
        predictions = x.dot(theta)
        gradient = (1/m) * x.T.dot(predictions - y)
        theta = theta - alpha * gradient
        #print(theta.shape)
        cost = cost_function(x, y, theta)
        cost_history[i] = cost  # 直接存储到数组
        theta_history.append(theta.copy())
        
        if i % 1000 == 0:
            print(f"迭代次数: {i}, 损失值: {cost:.6f}")
    
    return theta, cost_history, theta_history

def plot_results(x, y, theta, cost_history):
    plt.figure(figsize=(12, 4))
    
    # 绘制损失函数变化
    plt.subplot(121)
    plt.plot(cost_history)
    plt.title('代价函数收敛曲线')
    plt.xlabel('迭代次数')
    plt.ylabel('代价值')
    
    # 绘制拟合结果
    plt.subplot(122)
    plt.scatter(x, y, color='blue', label='实际值')  # 修正索引错误
    y_pred = X_b.dot(theta).flatten()  # 展平预测结果
    plt.plot(x, y_pred, color='red', label='预测值')  # 修正索引错误
    plt.title('线性回归拟合结果')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    theta, cost_history, theta_history = gradient_descent(X_b, y, 0.001, 10000)
    
    # 计算预测值
    print(theta.shape)
    
    # 选取最后一次迭代的参数计算预测值
    theta_final = theta_history[-1]
    y_pred = X_b.dot(theta)

    print(y_pred.shape)

    
    # 计算评估指标
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    
    print("\n模型评估结果:")
    print(f"R² 得分: {r2:.4f}")
    print(f"均方误差: {mse:.4f}")
    print(f"最终模型参数: θ₀={theta[0][0]:.4f}, θ₁={theta[1][0]:.4f}")
    
    plot_results(x, y, theta, cost_history)