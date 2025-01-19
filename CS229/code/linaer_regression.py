import numpy as np
import os
import matplotlib.pyplot as plt
#加载数据
x=np.loadtxt('x.txt',delimiter='\n',dtype=float)
#定义损失函数
def cost_function(x,y,theta):
    m=len(y)
    h_theta=x.dot(theta)
    #根据定义的损失函数公式计算损失
    J_theta=(1/(2*m))*np.sum(h_theta-y)**2
    return J_theta
#梯度下降函数
#aplha:学习率,iterations:迭代次数,x:特征矩阵,y:标签矩阵
def gradient_descent(x,y,alpha,iterations):
    m,n=x.shape
    theta=np.zeros((n,1))
    cost_history=np.zeros(iterations)
    #迭代,求取梯度，更新theta
    for i in range(iterations):
        predictions=x.dot(theta)
        gradient=(1/m)*x.T.dot(predictions-y)
        theta=theta-alpha*gradient
        cost_history[i]=cost_function(x,y,theta)
    return theta,cost_history
