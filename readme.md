# CHK File Recovery Tool (chkrepair)

一个强大且专业的工具，用于恢复和修复由Windows磁盘检查工具(`chkdsk /f`)生成的`.CHK`文件。通过智能文件签名识别和ZIP容器深度分析，准确还原文件原始格式。

## 功能特点

-   **智能文件签名识别**：内置超过40种常见文件格式的魔法数字（Magic Number）签名，包括文档、图片、音视频、压缩包等。
-   **ZIP容器深度分析**：不仅能识别ZIP压缩包，还能深入分析其内部结构，精确恢复：
    -   Microsoft Office 文档 (`.docx`, `.xlsx`, `.pptx`)
    -   EPUB 电子书 (`.epub`)
    -   JAR/APK 包
    -   OpenDocument 格式 (`.odt`, `.ods`)
-   **高度可扩展**：支持通过外部配置文件自定义文件签名和ZIP分析规则，无需修改源代码即可支持任何新格式。
-   **安全可靠**：采用只读方式分析文件头，绝不会对原始`.CHK`文件造成二次损坏。自动处理重名文件，防止覆盖。

## 安装与使用

### 要求

-   **Python 3.6+**
-   无需任何第三方库（仅使用Python标准库：`os`, `shutil`, `zipfile`）

### 快速开始

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/your-username/chkrepair.git
    cd chkrepair
    ```

2.  **运行工具**:
    ```bash
    python chkrepair0.1.py
    ```

3.  **按提示操作**:
    -   输入包含`.CHK`文件的目录路径（通常是 `C:\FOUND.XXX` 文件夹）。
    -   输入恢复文件的输出目录。
    -   （可选）提供外部配置文件路径以扩展识别能力。

### 外部配置文件示例

创建一个文本文件（如 `my_rules.cfg`）来添加自定义规则：

```ini
# 自定义文件签名规则
type=.myfile
content=\x89\x4D\x59\x46

# 自定义ZIP容器规则（识别内部包含特定文件的自定义格式）
type=.myapp
zip=/metadata.json
