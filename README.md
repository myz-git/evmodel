# 模型训练

## CNN模型

训练：用 **PyTorch CNN（IconCNN）**，带数据增强（RandomAffine/ColorJitter/Flip 等），训练后保存 `state_dict()` 到 `model_cnn/{icon}_classifier.pth`。

模型文件：`.pth`（PyTorch 权重），输入是 **Tensor + Normalize**（不是直方图）

CNN 能学习到形状/纹理等更复杂特征，通常比“颜色直方图 + 传统分类器”更能抗：

- UI 亮度/色温变化、截图压缩噪声

- 图标轻微缩放/旋转/平移

- 局部遮挡、背景干扰

  

## joblib模型

颜色直方图特征 + scaler + sklearn/joblib 分类器

识别流程：**OpenCV 模板匹配**找到候选位置 → 截出小图 → 用 **BGR 三通道颜色直方图(16×16×16)** 做特征 → `scaler.transform()` → `joblib` 的 sklearn 分类器 `clf.predict()` 做二分类验证。

模型文件：`{model}.joblib` + `{model}_scaler.joblib`（scikit-learn/joblib）



优点：依赖轻（不需要 torch）、推理快、部署简单、CPU 友好。

缺点：特征主要是颜色分布，对“主题换色/光照变化/背景色干扰”更敏感；遇到图标边缘细节变化时泛化一般。

## 环境准备

 **环境**：使用 Python 3.10.6，PyTorch 2.3.1，OpenCV 4.9.0.80，PyAutoGUI 0.9.54，屏幕分辨率为 1920x1080

```
cd D:\Workspace\git\evmodel
conda remove -n evmodel--all
conda create -n evmodel python=3.10.6
conda activate evmodel 

conda install -y numpy=1.26.4
pip uninstall -y torch torchvision torchaudio
#for gpu
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
#for cpu:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

pip install opencv-python
pip install scikit-learn scikit-image
pip install pillow pyautogui

```

