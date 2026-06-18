# VeighNa框架的DuckDB数据库接口

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-0.1.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg" />
</p>

## 说明

基于DuckDB原生Python接口开发的VeighNa数据库接口，无需另外安装配置数据库服务，易于使用。

DuckDB是高性能嵌入式列式数据库，数据保存在单个本地文件中。在K线历史数据管理、批量导入以及本地量化研究分析等场景下，相比SQLite具有更好的查询和聚合性能。

## 安装

安装环境推荐基于4.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。
下载源代码后，在项目根目录运行：

```bash
pip install .
```

## 使用

### 全局配置

在VeighNa中使用DuckDB时，需要在全局配置中填写以下字段信息：

|名称|含义|必填|举例|
|---------|----|---|---|
|database.name|名称|是|duckdb|
|database.database|实例|是|database.duckdb|

DuckDB为嵌入式数据库，无需填写host、port、user、password等连接字段。

### 创建实例

VeighNa会在首次连接时自动创建database.database字段对应的数据库文件，无需像PostgreSQL那样手动预先创建。数据库文件默认保存在VeighNa的运行时目录（即.vntrader文件夹）下，这一行为与SQLite接口保持一致。

## 注意事项

- DuckDB与SQLite类似，采用单写入者模型，不支持多个进程同时写入同一个数据库文件，请避免在多个进程中并发写入。
- 对于长期积累的超大规模Tick数据，可通过DuckDB的`COPY TO PARQUET`命令将冷数据归档导出，以控制数据库文件的体积。
