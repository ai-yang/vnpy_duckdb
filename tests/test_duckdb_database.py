import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest


pytest.importorskip("duckdb")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vnpy.trader.constant import Exchange, Interval  # noqa: E402
from vnpy.trader.database import DB_TZ  # noqa: E402
from vnpy.trader.object import BarData, TickData  # noqa: E402
from vnpy_duckdb import DuckdbDatabase  # noqa: E402


def make_bar(dt: datetime, close_price: float = 1) -> BarData:
    return BarData(
        symbol="IF88",
        exchange=Exchange.CFFEX,
        datetime=dt,
        interval=Interval.MINUTE,
        volume=100,
        turnover=1000,
        open_interest=10,
        open_price=close_price - 1,
        high_price=close_price + 1,
        low_price=close_price - 2,
        close_price=close_price,
        gateway_name="TEST",
    )


def make_tick(dt: datetime, last_price: float = 1) -> TickData:
    return TickData(
        symbol="IF88",
        exchange=Exchange.CFFEX,
        datetime=dt,
        name="IF88",
        volume=100,
        turnover=1000,
        open_interest=10,
        last_price=last_price,
        bid_price_1=last_price - 1,
        ask_price_1=last_price + 1,
        bid_volume_1=10,
        ask_volume_1=20,
        gateway_name="TEST",
    )


@pytest.fixture()
def database(tmp_path: Path) -> DuckdbDatabase:
    db: DuckdbDatabase = DuckdbDatabase(tmp_path / "test.duckdb")
    yield db
    db.close()


def test_save_load_delete_bar_data(database: DuckdbDatabase) -> None:
    start: datetime = datetime(2024, 1, 1, 9, 0, tzinfo=DB_TZ)
    original: BarData = make_bar(start, 10)
    bars: list[BarData] = [
        original,
        make_bar(start + timedelta(minutes=1), 11),
        make_bar(start, 12),
    ]

    assert database.save_bar_data(bars)
    assert original.datetime == start

    loaded: list[BarData] = database.load_bar_data(
        "IF88",
        Exchange.CFFEX,
        Interval.MINUTE,
        start,
        start + timedelta(minutes=2),
    )
    assert [bar.close_price for bar in loaded] == [12, 11]
    assert all(bar.gateway_name == "DB" for bar in loaded)
    assert all(bar.datetime.tzinfo == DB_TZ for bar in loaded)

    overview = database.get_bar_overview()
    assert len(overview) == 1
    assert overview[0].count == 2
    assert overview[0].start == start
    assert overview[0].end == start + timedelta(minutes=1)

    deleted: int = database.delete_bar_data("IF88", Exchange.CFFEX, Interval.MINUTE)
    assert deleted == 2
    assert database.get_bar_overview() == []


def test_save_load_delete_tick_data(database: DuckdbDatabase) -> None:
    start: datetime = datetime(2024, 1, 1, 9, 0, tzinfo=DB_TZ)
    ticks: list[TickData] = [
        make_tick(start, 10),
        make_tick(start + timedelta(seconds=1), 11),
        make_tick(start, 12),
    ]

    assert database.save_tick_data(ticks)

    loaded: list[TickData] = database.load_tick_data(
        "IF88",
        Exchange.CFFEX,
        start,
        start + timedelta(seconds=2),
    )
    assert [tick.last_price for tick in loaded] == [12, 11]
    assert all(tick.gateway_name == "DB" for tick in loaded)
    assert all(tick.datetime.tzinfo == DB_TZ for tick in loaded)

    overview = database.get_tick_overview()
    assert len(overview) == 1
    assert overview[0].count == 2
    assert overview[0].start == start
    assert overview[0].end == start + timedelta(seconds=1)

    deleted: int = database.delete_tick_data("IF88", Exchange.CFFEX)
    assert deleted == 2
    assert database.get_tick_overview() == []


def test_stream_overview_updates_incrementally(database: DuckdbDatabase) -> None:
    start: datetime = datetime(2024, 1, 1, 9, 0, tzinfo=DB_TZ)

    database.save_bar_data(
        [
            make_bar(start, 10),
            make_bar(start + timedelta(minutes=1), 11),
        ],
        stream=True,
    )
    database.save_bar_data(
        [
            make_bar(start + timedelta(minutes=2), 12),
            make_bar(start + timedelta(minutes=3), 13),
        ],
        stream=True,
    )

    overview = database.get_bar_overview()[0]
    assert overview.count == 4
    assert overview.start == start
    assert overview.end == start + timedelta(minutes=3)

    database.save_tick_data(
        [
            make_tick(start, 10),
            make_tick(start + timedelta(seconds=1), 11),
        ],
        stream=True,
    )
    database.save_tick_data(
        [
            make_tick(start + timedelta(seconds=2), 12),
            make_tick(start + timedelta(seconds=3), 13),
        ],
        stream=True,
    )

    tick_overview = database.get_tick_overview()[0]
    assert tick_overview.count == 4
    assert tick_overview.start == start
    assert tick_overview.end == start + timedelta(seconds=3)


def test_restart_connection_reads_existing_data(tmp_path: Path) -> None:
    path: Path = tmp_path / "restart.duckdb"
    start: datetime = datetime(2024, 1, 1, 9, 0, tzinfo=DB_TZ)

    db1: DuckdbDatabase = DuckdbDatabase(path)
    db1.save_bar_data([make_bar(start, 10)])
    db1.close()

    db2: DuckdbDatabase = DuckdbDatabase(path)
    try:
        loaded: list[BarData] = db2.load_bar_data(
            "IF88",
            Exchange.CFFEX,
            Interval.MINUTE,
            start,
            start,
        )
        assert len(loaded) == 1
        assert loaded[0].close_price == 10
    finally:
        db2.close()


def test_get_database_loads_duckdb_driver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import vnpy.trader.database as database_module
    from vnpy.trader.setting import SETTINGS

    monkeypatch.setitem(SETTINGS, "database.name", "duckdb")
    monkeypatch.setitem(SETTINGS, "database.database", str(tmp_path / "integration.duckdb"))
    monkeypatch.setattr(database_module, "database", None)

    db = database_module.get_database()
    try:
        assert isinstance(db, DuckdbDatabase)
    finally:
        db.close()
        database_module.database = None
