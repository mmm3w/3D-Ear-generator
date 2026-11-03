# 3D Ear Generator

这是一个用于 Blender 的人耳生成与调整工具。项目现已提供适配 **Blender 4.2** 的标准插件版本，保留原工程的耳朵网格、骨架、形态键、38 个调节参数和 17 个预设。

插件默认使用中文界面，可在面板顶部的 **Language / 语言** 中切换为 English。

## 下载插件

在 GitHub 仓库的 **Releases** 页面打开最新版本，从 **Assets** 中下载：

```text
ear_generator_addon.zip
```

发布 Release 后，GitHub Actions 会自动从源码构建并上传该文件，无需手动上传安装包。

## 交付文件

- `ear_generator_addon.zip`：可直接在 Blender 中安装的插件包。
- `ear_generator/`：插件源码、模型资源和预设。
- `.github/workflows/release.yml`：Release 自动构建和上传工作流。
- `api_new_ear_en.zip`：原始英文完整工程。
- `api_new_ear_fr.zip`：原始法文完整工程。
- `api_new_ear-corrected.zip`：另一套资源使用的旧修改脚本，不是本插件的依赖，也不能直接读取本插件的 38 参数预设。

插件目录结构：

```text
ear_generator/
├── __init__.py
├── localization.py
├── assets/
│   └── ear_reference.blend
└── presets/
    ├── standard.ear
    ├── banipal.ear
    └── ...其他预设
```

## 环境要求

- 目标版本：Blender 4.2。
- 已验证版本：**Blender 4.2.9 LTS**。
- 其他 Blender 版本尚未验证。
- 模型资源已包含在安装包中，不需要原始 ZIP，也不需要配置外部模型路径。

## 安装插件

1. 不要解压 `ear_generator_addon.zip`。
2. 打开 Blender 4.2。
3. 进入 **编辑 → 偏好设置 → 插件**。
4. 打开右上角菜单，选择 **从磁盘安装 / Install from Disk**。
5. 选择 `ear_generator_addon.zip`。
6. 在插件列表中搜索并启用 **3D Ear Generator**。

插件入口位于：**3D 视口 → 按 `N` 打开侧栏 → Ear 标签**。面板默认显示中文；如需英文界面，将 **Language / 语言** 设置为 **English**。

## 创建和编辑耳朵

1. 打开 **Ear** 面板。
2. 点击 **创建耳朵 / Create Ear**。
3. 新耳朵会成为当前活动对象，面板随即显示全部调节参数。
4. 使用滑块调整整体比例、方向和局部形态。
5. 如果场景中有多个耳朵，先选中需要编辑的耳朵对象，再调整参数。

每次点击 **创建耳朵 / Create Ear** 都会创建独立实例。不同耳朵的骨架、网格和形态键互不影响。

创建时场景中只新增两个必要对象：耳朵网格和用于变形的骨架。插件会清除原始资源附带的展示角度和偏移，使新耳朵按默认方向对齐世界坐标。箭头、文字、封面、图例等辅助内容已全部移除；执行 **应用全部修改** 后骨架也会删除，只保留独立耳朵网格。

### 整体比例与方向

| 分组 | 中文参数 | English |
| --- | --- | --- |
| 整体尺寸 | 耳朵高度、耳朵宽度、耳朵厚度 | Ear height、Ear width、Ear thickness |
| 区域缩放 | 上部缩放、后部缩放、下部缩放 | Top scale、Rear scale、Bottom scale |
| 整体方向 | 耳朵外凸、耳朵垂直度、耳朵倾斜 | Ear protrusion、Ear verticality、Ear tilt |
| 上部弯曲 | 上部弯曲 X/Y/Z | Top curving X/Y/Z |
| 下部弯曲 | 下部弯曲 X/Y/Z | Bottom curving X/Y/Z |
| 后部弯曲 | 后部弯曲 X/Y/Z | Rear curving X/Y/Z |

点击 **重置比例与方向 / Reset Proportions and Orientations** 可将这 18 个参数恢复为默认值。

### 局部形态

| 分组 | 中文参数 | English |
| --- | --- | --- |
| 耳垂 | 无耳垂、耳垂最大高度、耳垂厚度 | No lobule、Lobule max height、Lobule thickness |
| 耳轮与结节 | 耳轮锐度、达尔文结节、上部结节、耳轮厚度 | Helix sharpness、Darwin tubercle、Top tubercle、Helix thickness |
| 对耳轮 | 对耳轮深度、对耳轮后部 | Antihelix depth、Antihelix rear |
| 耳屏 | 耳屏厚度、耳屏外凸、耳屏宽度 | Tragus thickness、Tragus protrusion、Tragus width |
| 对耳屏 | 对耳屏位置、对耳屏切迹、双对耳屏 | Antitragus location、Antitragus notch、Double antitragus |
| 凹陷与折痕 | 后部凹陷、耳垂折痕、耳垂中部折痕、耳根折痕 | Rear concavity、Lobule crease、Lobule mid crease、Root crease |
| 后部形状 | 后部隆起 | Rear protrusion |

点击 **重置区域与形态 / Reset Regions and Shapes** 可将这 20 个参数恢复为默认值。

## 细分显示

点击 **细分 / Subdivision** 可切换耳朵的细分效果。细分由耳朵网格上的修改器完成，不会增加辅助对象；应用修改后将不可再切换。

## 加载和保存预设

### 加载预设

1. 选中一个尚未应用修改的耳朵。
2. 点击 **加载预设 / Load preset**。
3. 选择一个 `.ear` 文件。

未指定预设目录时，文件选择器默认打开插件自带的 `presets` 目录。成功加载后，该文件所在目录会成为后续保存的默认目录。

### 保存预设

1. 选中需要保存参数的耳朵。
2. 点击 **保存预设 / Save preset**。
3. 选择保存位置并输入文件名。

预设由 38 行数值组成，顺序与原版英文/法文完整工程一致。加载时会检查数值数量和有效性；参数数量不同的旧 corrected 脚本预设不能混用。

面板顶部的 **预设目录（可选）/ Work directory** 只用于决定加载和保存 `.ear` 预设时文件选择器的默认位置。它不是模型资源路径，不影响耳朵的创建、位置、旋转或形状，留空也可以正常使用。

## 应用修改

点击 **应用全部修改 / Apply All Changes** 会将以下内容固化为独立网格：

- 当前骨架变形；
- 当前形态键结果；
- 当前视口细分状态。

应用后：

- 耳朵不再依赖骨架和形态键；
- 骨架和该实例的集合会被删除；
- 独立耳朵网格直接保留在场景集合中；
- 原有参数滑块不能继续修改该耳朵。

此操作会改变模型结构。需要继续调整时，请使用 Blender 的撤销功能，或在应用前保留一份副本。

若要将耳朵合并到人物模型，可以将最终网格复制到目标场景，或保存工程后使用 Blender 的追加功能。插件不再提供 STL 导出按钮。

## 禁用与卸载

- 在 Blender 插件列表中取消勾选 **3D Ear Generator** 可禁用插件。
- 禁用插件不会删除场景中已经创建的耳朵。
- 卸载插件前建议先保存工程；已经应用修改的耳朵是普通独立网格。
- 未应用修改的耳朵仍依赖场景中的骨架和形态键数据，因此保留这些对象，不要只保留耳朵网格而删除其骨架。

## 常见问题

### 面板没有显示参数

确认已点击 **创建耳朵 / Create Ear**，并选中由插件创建的耳朵对象。应用修改后的耳朵也不会再显示可编辑状态。

### 修改滑块没有作用

检查该耳朵是否已经执行过 **应用全部修改 / Apply All Changes**。应用后请撤销操作，或重新创建一个耳朵。

### 无法加载预设

本插件要求预设恰好包含 38 个有限数值。不要使用 `api_new_ear-corrected.zip` 所采用的 34 参数格式。

## 发布 GitHub Release

仓库已配置 `.github/workflows/release.yml`。维护者按以下步骤发布后，插件 ZIP 会自动出现在 Release 的 **Assets** 中：

1. 将插件源码、资源和工作流提交并推送到 GitHub 默认分支。
2. 打开仓库的 **Releases** 页面，选择 **Draft a new release**。
3. 创建或选择版本标签，例如 `v1.2.1`，填写版本标题和更新说明。
4. 点击 **Publish release**。
5. 等待 **Package and publish Blender add-on** 工作流完成，刷新 Release 页面即可下载 `ear_generator_addon.zip`。

工作流只在 **Release 正式发布**时触发，不会因为创建草稿或普通 push 而上传附件。重复上传同名 ZIP 时会替换旧附件。该自动化需要仓库允许 GitHub Actions 写入 Release 内容；工作流已声明 `contents: write` 权限。

## 验证情况

最终安装 ZIP 已在 Blender 4.2.9 LTS 中完成以下实际验证：

- 从 ZIP 安装、启用、禁用和重新注册；
- 中文/English 界面设置与切换；
- 创建时每个实例只包含耳朵网格和骨架；
- 创建多个独立耳朵实例并修改骨架和形态键参数；
- 加载自带预设并保存、重新加载 38 参数预设；
- 应用修改后删除骨架和实例集合，只保留独立耳朵网格；
- 确认面板和注册操作符中不再包含 STL 导出功能。

## 原项目

原作者：Jac Petit-Jean-Boret（Rimpotche）。

原项目以 CC0 发布，可免费使用。原始教程：

<https://youtu.be/6QlsoSDqUoc>
