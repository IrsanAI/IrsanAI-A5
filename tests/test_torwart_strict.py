import pathlib, json, time, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import torwart.mandatory_inversion as t

def test_no_live():
    r=t.run_spd_barrier_dr_residual_i3(0)
    assert r.overall_confidence==0.72, "no live must be 0.72"
    assert r.survival_assessment=="partially reframed"
    print("PASS no live -> 0.72")

def test_crackme_does_not_unlock_spd():
    # Crackme Evidence darf SPD nicht auf 0.88 heben
    ev_dir=pathlib.Path.home()/ "a5_evidence"
    ev_dir.mkdir(exist_ok=True)
    fake=ev_dir/"test_crackme.json"
    fake.write_text(json.dumps({"confidence":"observed","finding_id":"a5_crackme_v2_key_check","provider":"a3_frida","target":"a5_crackme_v2","binary_sha256":"abc","ts":time.time(),"observed":{"input":"A5-Pro-Cockpit-2026!","result":1}}))
    r=t.run_spd_barrier_dr_residual_i3(1)
    assert r.overall_confidence==0.72, "crackme must not unlock SPD"
    fake.unlink()
    print("PASS crackme -> SPD stays 0.72")

def test_fake_spd_json():
    ev_dir=pathlib.Path.home()/ "a5_evidence"
    ev_dir.mkdir(exist_ok=True)
    fake=ev_dir/"test_fake_spd.json"
    fake.write_text(json.dumps({
      "confidence":"observed","provider":"a3_frida","target":"spd","finding_id":"spd_barrier_dr_order",
      "frida_version":"17.2.14","binary_sha256":"deadbeef","device_id":"local","ts":time.time(),
      "observed":{"barrier_absorb_value":5,"dr_min":2,"dr_max":10,"damage_roll":12}
    }))
    r=t.run_spd_barrier_dr_residual_i3(1)
    assert r.overall_confidence==0.72, "fully filled fake SPD JSON must stay 0.72"
    fake.unlink()
    print("PASS fake SPD JSON -> 0.72")

def test_spd_not_implemented():
    r=t.run_spd_barrier_dr_residual()
    assert "not implemented" in r.phase0_access_limitations.lower()
    assert r.overall_confidence==0.72
    print("PASS SPD not implemented marked")

if __name__=="__main__":
    test_no_live()
    test_crackme_does_not_unlock_spd()
    test_fake_spd_json()
    test_spd_not_implemented()
    print("ALL 4 TESTS PASS – security goal reached, functional goal correctly marked as not implemented")
