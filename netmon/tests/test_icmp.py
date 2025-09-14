from app.collectors.icmp import collect_ping

def test_ping_smoke():
    # 127.0.0.1 için simple call — DB yoksa bile hata atmaması için DB bağlantısı gereklidir.
    # Bu test yalnızca import/çağrı hatalarını yakalar (dummy).
    collect_ping(1, "127.0.0.1")