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

基于DuckDB开发的数据库接口。

DuckDB是一个高性能的嵌入式列式（OLAP）数据库，无需安装和配置独立的服务进程，所有数据保存在单个本地文件中，部署方式和SQLite一样简单。相比SQLite，DuckDB在K线历史数据管理、批量导入以及本地量化研究分析等场景下具有更好的查询和聚合性能。

## 安装

安装环境推荐基于4.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。

直接使用pip命令：

```bash
pip install vnpy_duckdb
```

或者下载源代码后，解压后在cmd中运行：

```bash
pip install .
```

## 使用

### 全局配置

在VeighNa中使用DuckDB时，需要在全局配置中填写以下字段信息：

|名称|含义|必填|举例|
|---------|----|---|---|
|database.name|名称|是|duckdb|
|database.database|数据库文件|是|database.duckdb|

DuckDB为嵌入式数据库，无需填写host、port、user、password等连接字段。database.database填写的数据库文件默认保存在VeighNa的运行时目录（即.vntrader文件夹）下，这一行为与SQLite接口保持一致。

### 数据表

接口启动时会自动创建以下4张数据表（若不存在）：

|表名|说明|主键|
|---------|----|---|
|dbbardata|K线数据|symbol, exchange, interval, datetime|
|dbtickdata|Tick数据|symbol, exchange, datetime|
|dbbaroverview|K线汇总数据|symbol, exchange, interval|
|dbtickoverview|Tick汇总数据|symbol, exchange|

### 写入说明

- 写入时先将数据转换为DataFrame并注册为临时表，再通过`INSERT OR REPLACE`一次性批量写入，避免逐行插入带来的性能损耗。
- 实时录制行情时（`stream=True`）会增量更新汇总数据；批量导入数据时（`stream=False`）会重新统计对应合约的汇总数据。
- 时间数据复用框架的`convert_tz`与`DB_TZ`进行时区处理，与其他数据库接口的行为保持一致。

## 注意事项

- DuckDB与SQLite类似，采用单写入者（single-writer）模型，不支持多个进程同时写入同一个数据库文件，请避免在多个进程中并发写入。
- 对于长期积累的超大规模Tick数据，建议定期通过`COPY TO PARQUET`将冷数据归档导出，以控制数据库文件的体积。
