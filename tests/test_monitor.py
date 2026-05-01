from app.services.monitor import monitor_api

def test_monitor_runs():
    # Should run without crashing
    monitor_api()
    assert True