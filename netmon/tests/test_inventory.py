from app.inventory.classify import mgmt_ip_from_name

def test_mgmt_ip():
    assert mgmt_ip_from_name("core@10.1.1.1")=="10.1.1.1"