from app.ml.models.dsm_icd_mapper import DSMICDMapper


class TestDSMICDMapper:

    def setup_method(self):
        self.mapper = DSMICDMapper()

    def test_map_icd_to_dsm_f32_1(self):
        dsm = self.mapper.map_icd_to_dsm("F32.1")
        assert dsm == "296.22", "ICD F32.1 should map to DSM 296.22"

    def test_map_dsm_to_icd(self):
        icd = self.mapper.map_dsm_to_icd("296.22")
        assert icd == "F32.1", "DSM 296.22 should map to ICD F32.1"

    def test_map_gad_code(self):
        icd = self.mapper.map_dsm_to_icd("300.02")
        assert icd == "F41.1", "DSM 300.02 should map to ICD F41.1"

    def test_get_mapping_returns_code_mapping(self):
        mapping = self.mapper.get_mapping("F32.1")
        assert mapping is not None
        assert mapping.icd_code == "F32.1"
        assert "Moderate" in mapping.disorder_name

    def test_invalid_code_returns_none(self):
        assert self.mapper.map_icd_to_dsm("Z99.99") is None
        assert self.mapper.map_dsm_to_icd("999.99") is None
        assert self.mapper.get_mapping("INVALID") is None

    def test_validate_icd_code(self):
        assert self.mapper.validate_code("F32.0", "icd") is True
        assert self.mapper.validate_code("F41.1", "icd") is True
        assert self.mapper.validate_code("Z99.99", "icd") is False

    def test_validate_dsm_code(self):
        assert self.mapper.validate_code("296.21", "dsm") is True
        assert self.mapper.validate_code("300.02", "dsm") is True
        assert self.mapper.validate_code("999.99", "dsm") is False

    def test_list_all_returns_mappings(self):
        all_mappings = self.mapper.list_all()
        assert len(all_mappings) > 0
        assert all(m.dsm_code for m in all_mappings)
        assert all(m.icd_code for m in all_mappings)

    def test_bidirectional_consistency(self):
        for icd in ["F32.0", "F32.1", "F33.2", "F41.1", "F42"]:
            dsm = self.mapper.map_icd_to_dsm(icd)
            assert dsm is not None, f"ICD {icd} should map to DSM"
            icd_back = self.mapper.map_dsm_to_icd(dsm)
            assert icd_back == icd, f"Round-trip failed for {icd}"
