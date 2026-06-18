# 0.1.0版本

1. 基于DuckDB实现VeighNa数据库接口，支持K线和Tick数据的读取、写入、删除与汇总查询
2. 采用批量staging写入与INSERT OR REPLACE去重，并支持stream流式写入参数
3. 复用框架convert_tz/DB_TZ进行时区处理，与其他数据库接口的行为保持一致
