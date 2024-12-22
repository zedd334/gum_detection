# gum_detection
口香糖缺陷检测



2.1 启用ssh
操作步骤：	
打开终端，依次输入以下命令即可。
sudo systemctl enable ssh
sudo systemctl start ssh

2.2安装MVS并调试相机
操作步骤：
下载网盘文件软件包2.0，将其中的这个MVS程序拷贝到主板的桌面
通过网盘分享的文件：软件包2.0
链接: https://pan.baidu.com/s/1PmFt8IzqLkzMZfDySfaEBg 提取码: 1111 
--来自百度网盘超级会员v1的分享
 
进入这个deb文件同级目录，打开终端，输入↓
sudo dpkg -i MVS-3.0.1_aarch64_20240902.deb
如果有依赖问题输入↓来修复
sudo apt --fix-broken install
在当前终端中运行以下命令来应用新的环境变量
source ~/.bashrc
执行以下命令，将当前目录中的库文件路径添加到 LD_LIBRARY_PATH：
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/MVS/bin
然后再次尝试运行：
./MVS
设置环境变量持久化
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/MVS/bin' >> ~/.bashrc
source ~/.bashrc
运行 MVS 启动脚本
./MVS.sh

使用以下命令确认安装路径：
ls /opt/MVS/bin
（例如 MVS 或 MVS.sh），可以通过以下命令运行它：
/opt/MVS/bin/MVS
打开终端并创建软链接：
sudo ln -s /opt/MVS/bin/MVS /usr/local/bin/MVS
之后可以直接在终端中输入以下命令来运行：
MVS
点击摄像头看看是否可以连接上
如果连接不上那就改为手动，填写地址和子网掩码，网关空出来，再试试连接 
这两个图片IP不一致，是因为采用不同的设备示例，实操时把红框内部分填到右图即可。
2.3安装MVSSDK
官方SDK调用
安装软件包里面的
 
sudo dpkg -i /home/nvidia/桌面/MvCamCtrlSDK_Runtime-4.4.1_aarch64_20240827.deb
如果在安装遇到依赖性问题
sudo apt-get install -f
刷新一下
source ~/.bashrc
2.4安装conda并移植环境
 
将软件包中yml文件放到合适的路径，桌面或者什么地方，下面标黄的命令部分替换为自己改的路径
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh


初始化conda
source ~/miniconda3/bin/activate
conda init
重新加载配置
source ~/.bashrc
创建新的 Conda 环境
conda create -n myenv python=3.8
conda activate myenv
激活 Conda 环境
source ~/.bashrc
 检查 Conda 版本
现在可以通过以下命令检查 conda 是否已成功安装和可用：
conda --version
禁用自动激活
conda config --set auto_activate_base false
配置 Conda 使用清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro
conda config --set show_channel_urls yes
在base环境下执行以下命令
conda env create -f /home/nvidia/ environment.yml
恢复完成后，激活新环境
conda activate myenv
如果遇到ERROR: No matching distribution found for opencv-python==4.10.0
pip install --force-reinstall --no-deps opencv-python==4.10.0.84
使用以下命令更新 myenv 环境
conda env update -n myenv -f /home/jetson/Desktop/environment.yml

2.5启动程序
通过网盘分享的文件：main_realese
链接: https://pan.baidu.com/s/1cdBEU8QNNW3SYVuAfNuY9A 提取码: 1111 
--来自百度网盘超级会员v1的分享
通过网盘分享的文件：_internal
链接: https://pan.baidu.com/s/1QJyNIIKDkNeVAZFrXAHH5A 提取码: 1111 
--来自百度网盘超级会员v1的分享
在环境搭配好之后，将这两个文件拷贝到桌面
 
之后在终端输入
./main_realese
之后启动程序即可
