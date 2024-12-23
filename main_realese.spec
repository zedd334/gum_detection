# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None

# 收集 torch 和 ultralytics 的所有子模块
hidden_imports = collect_submodules('torch') + collect_submodules('ultralytics')

# 手动添加隐藏导入
hidden_imports += [
    'numpy.core.complexfloating',
    'numpy.core.inexact',
    'numpy.core.cdouble',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'cryptography',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.primitives',
    'scipy.special.airy',
    'pycocotools',
    'h5py',
    'tensorflow',
    'torch.nn.Module',
    'torch.cuda',
    'torch.distributed',
    'torch.optim',
    'torch.autograd',
    'torch.Tensor',
    'torch.nn.Sequential',
    'torch.nn.ParameterList',
    'torch.nn.BatchNorm1d',
    'matplotlib.backends.backend_qt5agg',  # 确保包含 Qt5Agg 后端
    'ultralytics.trackers',
]

# 收集动态库
binaries = collect_dynamic_libs('torch') + collect_dynamic_libs('ultralytics')

# 添加额外动态库
binaries += [
    ('/usr/local/cuda/targets/aarch64-linux/lib/libcudart.so', '.'),
    ('/usr/local/cuda/targets/aarch64-linux/lib/libcublas.so', '.'),
    ('/usr/local/cuda/targets/aarch64-linux/lib/libcufft.so', '.'),
    ('/home/nvidia/miniconda3/envs/myenv/lib/python3.8/site-packages/torch/lib/libtorch.so', '.'),
    ('/home/nvidia/miniconda3/envs/myenv/lib/python3.8/site-packages/torch/lib/libtorch_cuda.so', '.'),
    ('/home/nvidia/桌面/aarch64/libMvCameraControl.so.4.4.1.3', '.'),
    ('/home/nvidia/桌面/aarch64/libMvCameraControlWrapper.so.2.4.0.6', '.'),
    ('/home/nvidia/桌面/aarch64/MvProducerGEV.cti', '.'),
    ('/home/nvidia/桌面/aarch64/MvProducerU3V.cti', '.'),
    ('/home/nvidia/miniconda3/envs/myenv/lib/libffi.so.8', '.'),
    ('/usr/lib/aarch64-linux-gnu/libpthread.so.0', '.'),
    ('/usr/lib/aarch64-linux-gnu/librt.so.1', '.'),
    ('/usr/lib/aarch64-linux-gnu/libdl.so.2', '.'),
    ('/usr/lib/aarch64-linux-gnu/libm.so.6', '.'),
    ('/usr/lib/aarch64-linux-gnu/libgcc_s.so.1', '.'),
    ('/home/nvidia/桌面/aarch64/CommonParameters.ini', '.'),
    ('/home/nvidia/桌面/aarch64/libavutil.so', '.'),
    ('/home/nvidia/桌面/aarch64/libFormatConversion.so', '.'),
    ('/home/nvidia/桌面/aarch64/libMediaProcess.so', '.'),
    ('/home/nvidia/桌面/aarch64/libMVGigEVisionSDK.so.4.4.1.2', '.'),
    ('/home/nvidia/桌面/aarch64/libMVRender.so', '.'),
    ('/home/nvidia/桌面/aarch64/libMvSDKVersion.so', '.'),
    ('/home/nvidia/桌面/aarch64/libMvUsb3vTL.so.4.4.1.2', '.'),
    ('/home/nvidia/桌面/aarch64/libusb-1.0.so.0', '.'),
    ('/usr/lib/aarch64-linux-gnu/libswscale.so', '.'),
    ('/usr/lib/aarch64-linux-gnu/libavutil.so', '.'),
    ('/home/nvidia/miniconda3/envs/myenv/lib/libpython3.8.so.1.0', '.'),
    ('/usr/lib/aarch64-linux-gnu/libncursesw.so.6', '.'),
    ('/usr/lib/aarch64-linux-gnu/libc.so.6', '.'),
]

# 收集静态数据文件
datas = [
    ('/home/nvidia/桌面/new/智能检测系统切图', '智能检测系统切图'),
    ('/home/nvidia/桌面/new/defect_data.db', '.'),
    ('/home/nvidia/桌面/new/best.torchscript', '.'),
    ('/home/nvidia/桌面/new/best_new.pt', '.'),
] + collect_data_files('matplotlib')

# 创建 Analysis 对象
a = Analysis(
    ['main_realese.py'],
    pathex=['/home/nvidia/桌面/new'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[
        '/home/nvidia/miniconda3/envs/myenv/lib/python3.8/site-packages/pyinstaller_hooks_contrib/stdhooks',
        '/home/nvidia/miniconda3/envs/myenv/lib/python3.8/site-packages/pyinstaller_hooks_contrib/rthooks'
    ],
    runtime_hooks=[],
    excludes=[
        'torch.testing._internal.optests',
        'org',
        'urllib.quote',
        'pyarrow',
        'win32pdh',
        'numpy.core.complexfloating',
        'numpy.core.inexact',
        'numpy.core.cdouble',
        'numpy.core.csingle',
        'numpy.core.double',
        'numpy.core.single',
        'numpy.core.intc',
        'numpy.core.empty_like',
        'numpy.core.empty',
        'numpy.core.zeros',
        'numpy.core.asarray',
        'numpy.core.array',
        'numpy.eye',
        'scikits.umfpack',
        'sksparse.cholmod',
        'scipy.special.airy',
        'pyarrow',
        'tensorflow',
        'pycocotools',
        'h5py',
        'accimage',
        'lmdb',
        'av',
        'defusedxml',
        'matplotlib.backends.backend_tkagg',  # 排除 TkAgg 后端
    ],
    cipher=block_cipher,
)

# 创建 PYZ 对象
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# 创建 EXE 对象
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main_realese',
    debug=False,  # 发布时设置为 False
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 应用程序设置为 False
)

# 创建 COLLECT 对象
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main_realese',
)


