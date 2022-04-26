# 介绍
修复 [genshin_auto_fish](https://github.com/7eu7d7/genshin_auto_fish) 里的小bug

**现已支持不同分辨率屏幕**

原神自动钓鱼AI由[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX), DQN两部分模型组成。使用迁移学习，半监督学习进行训练。
模型也包含一些使用opencv等传统数字图像处理方法实现的不可学习部分。

其中YOLOX用于鱼的定位和类型的识别以及鱼竿落点的定位。DQN用于自适应控制钓鱼过程的点击，让力度落在最佳区域内。

# 注意
## 欢迎提交游戏内鱼群图片给我扩充数据集，用于增加识别准确度

## 使用这个项目遇到的问题直接在这里提Issues就行，不用再跑到 [原作者(7eu7d7)](https://github.com/7eu7d7) 那里提Issues了

### 一定要先在游戏内开SMAA再运行此项目！！！！

1.一定要，一定要，一定要先安装 [Visual Studio](https://visualstudio.microsoft.com/zh-hans/downloads/) 否则安装pycocotools和yolox的时候会出现奇奇怪怪的错误

2.原神需要以1920x1080的分辨率运行，比此分辨率高的屏幕可以开窗口模式。

### <font color=#0000ff>**安装CUDA和CUDNN教程（CUDA v11.6.2, CUDNN v8.4.0）**</font>
### A卡用户请忽略安装CUDA部分，使用cpu跑(就是有点卡)


1.<font color=#ff9900>更新显卡驱动到最新版本</font>

2.在NVIDIA官网下载CUDA,[exe(local)](https://developer.download.nvidia.com/compute/cuda/11.6.2/local_installers/cuda_11.6.2_511.65_windows.exe) [2.5GB] & [exe(network)](https://developer.download.nvidia.com/compute/cuda/11.6.2/network_installers/cuda_11.6.2_windows_network.exe) [33.6MB] 【任选一个】下载下来后打开无脑下一步，等待其安装完成

3.在NVIDIA官网下载 [CUDNN v8.4.0](https://developer.nvidia.cn/compute/cudnn/secure/8.4.0/local_installers/11.6/cudnn-windows-x86_64-8.4.0.27_cuda11.6-archive.zip) [670MB] 可能需要登陆NVIDIA账号

4.解压下载下来的CUDNN zip压缩包，将里面的所有文件复制到以下目录 <font color=#7cfc00>C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.6\ </font>

5.重启PC，即安装完成

### <font color=#0000ff>**安装pycocotools教程**</font>

方法1(需要安装[git](https://github.com/git-for-windows/git/releases/download/v2.36.0.windows.1/Git-2.36.0-64-bit.exe)), [git安装教程](https://www.cnblogs.com/xiaoliu66/p/9404963.html):

```shell
pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI
```
方法2 (方法1无效时可尝试)

1.在此 [链接](https://github.com/philferriere/cocoapi/archive/refs/heads/master.zip) & [镜像链接](https://ghproxy.com/https://github.com/philferriere/cocoapi/archive/refs/heads/master.zip) 下载pycocotools源码并解压

2.<font color=7cfc00>**激活虚拟环境后**</font>进入解压出来的cocoapi-master\PythonAPI文件夹下，输入
```shell
python setup.py build_ext install
```
# 更新&修复&优化

2022/4/26 0:16 修复了鱼饵 果酿饵 ^ 赤糜饵 的选择问题

2022/4/25 23:36 优化识别的准确度

2022/3/11 18:35 修复了在鱼饵选择界面如果选择的鱼饵重复会跳出鱼饵详情界面影响程序运行的bug

2022/3/10 21:47 修复了无法换鱼饵，抛竿时无法移动的bug

2022/3/9 14:32 更新可识别渊下宫的鱼


# 安装使用流程
安装python运行环境（解释器），推荐使用 [anaconda](https://www.anaconda.com/products/individual#Downloads).

## python环境配置

打开anaconda prompt(命令行界面)，创建新python环境并激活:
```shell
# 创建虚拟环境
conda create -n ysfish python=3.7

# 激活虚拟环境
conda activate ysfish 
```
推荐安装<font color=#66CCFF>**python3.7或以下**</font>版本。

## 下载工程代码
使用git下载
```shell
git clone https://github.com/HuYo-OS/Genshin_auto_fish.git
```
或直接点这里的 [链接](https://github.com/HuYo-OS/Genshin_auto_fish/archive/refs/heads/main.zip) & [镜像链接](https://ghproxy.com/https://github.com/HuYo-OS/Genshin_auto_fish/archive/refs/heads/main.zip) 下载后直接解压。

## 依赖库安装
切换命令行到本工程所在目录:
```shell
cd genshin_auto_fish
```
############################################################

##<font color=#66ccff>**推荐**</font>


```shell
pip install -U pip
pip install -r requirements.txt
```
安装PyTorch
需要<font color=#33e6cc>安装CUDA，CUDNN</font>【<font color=#adff2f>**安装教程看最顶上**</font>】，这里以CUDA11.6.2为例：
```shell
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
```

如果你是A卡还想要运行的话可以试试安装CPU版的PyTorch
```shell
pip3 install torch torchvision torchaudio
```
############################################################

## 安装yolox
切换命令行到本工程所在目录，执行以下命令安装yolox:
```shell
python setup.py develop
```

## 预训练权重下载（本项目只对我训练好的模型做了适配）
从右边的 [Releases](https://github.com/HuYo-OS/Genshin_auto_fish/releases) 下载权重放到 **工程目录/weights**</font> 文件夹下

# 运行钓鱼AI
原神需要以1920x1080的分辨率运行，比此分辨率高的屏幕可以开窗口模式。

命令行窗口一定要以<font color=#66CCFF>**管理员权限**</font>启动

显卡加速
```shell
python fishing.py image -f yolox/exp/yolox_tiny_fish.py -c weights/best_tiny3.pth --conf 0.25 --nms 0.45 --tsize 640 --device gpu
```
cpu运行
```shell
python fishing.py image -f yolox/exp/yolox_tiny_fish.py -c weights/best_tiny3.pth --conf 0.25 --nms 0.45 --tsize 640 --device cpu
```
运行后出现**init ok**后按r键开始钓鱼，原神需要以1920x1080的分辨率运行。出于性能考虑检测框不会实时显示，处理运算后台进行。


# DQN训练工作流程(以下部分可跳过)
控制力度使用强化学习模型DQN进行训练。两次进度的差值作为reward为模型提供学习方向。模型与环境间交互式学习。

直接在原神内训练耗时较长，太累了。首先制作一个仿真环境，大概模拟钓鱼力度控制操作。在仿真环境内预训练一个模型。
随后将这一模型迁移至原神内，实现域间迁移。

仿真环境预训练代码:
```shell
python train_sim.py
```
原神游戏内训练:
```shell
python train.py
```
