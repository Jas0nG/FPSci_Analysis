import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

def one_dimensional_fft(data, sampling_rate):
    """
    对一维数据进行傅里叶变换。

    参数：
        data：一维数据数组
        sampling_rate：采样率（数据点之间的时间间隔）

    返回：
        frequencies：频率数组
        amplitudes：振幅数组
    """
    n = len(data)
    frequencies = np.fft.fftfreq(n, d=1/sampling_rate)
    amplitudes = np.abs(fft(data))

    return frequencies, amplitudes

# 示例使用
data = np.array([2, 4, 1, 6, 8, 3, 5, 7])
sampling_rate = 1  # 假设数据点之间的时间间隔为1

frequencies, amplitudes = one_dimensional_fft(data, sampling_rate)

# 绘制频谱图
plt.figure()
plt.plot(frequencies, amplitudes)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Frequency Spectrum')
plt.grid(True)
plt.show()
