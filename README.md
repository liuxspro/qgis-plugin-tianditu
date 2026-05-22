# TianDiTu Tools

[![Downloads](https://img.shields.io/badge/dynamic/xml?color=success&label=Downloads&query=%2F%2Fpyqgis_plugin%5B%40name%3D%27TianDiTu%20Tools%27%5D%2Fdownloads%2Ftext%28%29&url=https%3A%2F%2Fplugins.qgis.org%2Fplugins%2Fplugins.xml%3Fqgis%3D3.30)](https://plugins.qgis.org/plugins/tianditu-tools/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

QGIS 天地图工具，方便进行天地图瓦片底图的添加以及简单实现了部分[天地图 Web 服务 API](http://lbs.tianditu.gov.cn/server/guide.html)（地名搜索、地理编码查询、逆地理编码查询）。

此外，还内置了部分**天地图省级节点历史影像**、**谷歌地图**、**ESRI**、**高德地图**等常用第三方在线地图源。

---

## 功能特性

- **天地图底图添加** — 一键添加天地图矢量、影像、地形、山体阴影等官方瓦片底图
- **省级历史影像** — 支持部分天地图省级节点历史遥感影像
- **第三方地图** — 内置 Google Maps、ESRI、高德地图等常用在线地图源
- **地名搜索** — 调用天地图地名搜索 API，检索地点
- **地理编码查询** — 将地址转换为坐标
- **逆地理编码查询** — 将坐标转换为地址
- **结果定位** — 双击（或点击链接）搜索结果项，自动在地图上添加标记并定位
- **多 Key 管理** — 支持保存多个天地图 Key，可指定使用或随机选用

---

## 使用说明

安装插件后，QGIS 工具栏会增加一个名为 **"天地图 Tools 工具栏"** 的专属工具栏，包含以下按钮：

| 按钮 | 功能 |
|------|------|
| 底图下拉菜单 | 选择并添加各种在线地图底图 |
| 搜索按钮 | 打开搜索面板，进行地名/地理编码/逆地理编码查询 |
| 设置按钮 | 配置天地图 API Key |

### 1. 设置天地图 Key

使用前需要先设置天地图 Key：

1. 点击工具栏上的**设置按钮**，打开设置面板
2. 输入你的天地图 Key，点击保存按钮
3. 可以保存多个 Key，后续可在设置中选择使用或随机选用

> 天地图 Key 需要到 [天地图控制台](https://console.tianditu.gov.cn/api/key) 申请，申请类型请选择 **"浏览器端"** 或 **"Android 平台"**。

### 2. 添加天地图底图

点击工具栏上的底图下拉菜单，从列表中选择所需底图（天地图矢量、影像、地形、山体阴影等），点击即可添加到当前工程中。

菜单按类别分组，涵盖：
- 天地图官方底图（矢量、影像、地形、山体阴影等）
- 部分天地图省级节点历史影像
- 第三方地图（Google 卫星图、ESRI 影像、高德地图等）

### 3. 天地图 Web 服务 API

点击搜索按钮，打开搜索面板，可切换以下三种查询模式：

| 模式 | 说明 |
|------|------|
| **地名搜索** | 输入地名关键词，检索匹配的地理位置 |
| **地理编码查询** | 输入结构化地址，返回对应的坐标 |
| **逆地理编码查询** | 输入经纬度坐标，返回对应的地址信息 |

**结果交互**：在搜索结果列表中**双击**任意结果项（或点击结果中的链接），即可在地图上添加对应位置的标记点并自动缩放定位到该位置。

---

## 安装方式

### QGIS 插件管理器（推荐）

1. 打开 QGIS，进入 **插件 → 管理并安装插件**
2. 搜索 **"TianDiTu Tools"**
3. 点击 **安装**
4. 安装后即可在工具栏中看到插件按钮

### 手动安装

从 [GitHub Releases](https://github.com/liuxspro/qgis-plugin-tianditu/releases) 下载最新版本压缩包，在 QGIS 插件管理器中选择`从ZIP文件安装`。

---

## 环境要求

- QGIS >= 3.4（支持 QGIS 4.x）
- Python 3
- 网络连接（用于加载在线地图和调用 API）
- 有效的[天地图 Key](https://console.tianditu.gov.cn/api/key)

---

## 免责声明

本插件为开源项目，仅提供技术集成功能。插件内置的第三方地图源（包括但不限于 Google Maps、ESRI、高德地图等）均来源于其官方公开的瓦片服务地址，仅供学习与研究参考。请遵守各地图服务商的使用条款及相关法律法规。

---

## 许可证

本项目采用 [GNU General Public License v3](LICENSE) 开源许可。

---

## 项目地址

- [QGIS 插件页面](https://plugins.qgis.org/plugins/tianditu-tools/)
- [项目主页](https://space.liuxs.pro/docs/projects/tianditu-tools)
