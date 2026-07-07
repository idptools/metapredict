import os
import tempfile
import shutil
import pytest
import metapredict as meta
from metapredict.backend import meta_tools

FASTA_CONTENT = ">seq1\nMEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD\n>seq2\nMSEYIRVTEDENDEPIEIPSEDDGTVLLSTVTAQFPGACGLRYRNPVSQCMRGVRLVEGILHAPDAGWGNLVYVVNYPKDNKRKMDETDASSAVKVKRAVQKTSDLIVLGLPWKTTEQDLKEYFSTFGEVLMVQVKKDLKTGHSKGFGFVRFTEYETQVKVMSQRHMIDGRWCDCKLPNSKQSQDEPLRSRKVFVGRCTEDMTEDELREFFSQYGDVMDVFIPKPFRAFAFVTFADDQIAQSLCGEDLIIKGISVHISNAEPKHNSNRQLERSGRFGGNPGGFGNQGGFGNSRGGGAGLGNNQGSNMGGGMNFGAFSINPAMMAAAQAALQSSWGMMGMLASQQNQSGPSGNNQNQGNMQREPNQAFGSGNNSYSGSNSGAAIGWGSASNAGSGSGFNGGFGSSMDSKSSGWGM\n"

@pytest.fixture(scope="module")
def temp_fasta():
    tmpdir = tempfile.mkdtemp()
    fasta_path = os.path.join(tmpdir, "test.fasta")
    with open(fasta_path, "w") as f:
        f.write(FASTA_CONTENT)
    yield fasta_path
    shutil.rmtree(tmpdir)

@pytest.fixture(scope="module")
def temp_outdir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)

def test_predict_disorder_caid_domain(temp_fasta, temp_outdir):
    # Should use domain-based binary assignment
    meta.predict_disorder_caid(temp_fasta, temp_outdir, version="v3")
    out1 = os.path.join(temp_outdir, "seq1.caid")
    out2 = os.path.join(temp_outdir, "seq2.caid")
    assert os.path.isfile(out1)
    assert os.path.isfile(out2)
    for out in [out1, out2]:
        with open(out) as f:
            lines = f.readlines()
        # Header line
        assert lines[0].startswith(">seq")
        # All other lines should have 4 columns: idx, residue, score, binary
        for l in lines[1:]:
            parts = l.strip().split("\t")
            assert len(parts) == 4
            assert parts[0].isdigit()
            assert len(parts[1]) == 1
            float(parts[2])  # should be convertible
            assert parts[3] in {"0", "1"}

def test_predict_disorder_caid_fixed_cutoff(temp_fasta, temp_outdir):
    # Should use fixed cutoff for binary assignment
    meta.predict_disorder_caid(temp_fasta, temp_outdir, version="v3", use_fixed_cutoff=0.5)
    out1 = os.path.join(temp_outdir, "seq1.caid")
    assert os.path.isfile(out1)
    with open(out1) as f:
        lines = f.readlines()
    binary = [int(l.split()[3]) for l in lines[1:]]
    # Should have at least one 1 and one 0 in binary column
    assert set(binary) <= {0, 1}
    assert 1 in binary
    assert 0 in binary

def test_write_caid_format_fixed_cutoff(temp_outdir):
    # Directly test meta_tools.write_caid_format with fixed cutoff
    seq = "MEEEKKKK"
    scores = [0.1, 0.6, 0.7, 0.2, 0.8, 0.3, 0.9, 0.4]
    input_dict = {"test": [seq, scores]}
    meta_tools.write_caid_format(input_dict, temp_outdir, version="v3", use_fixed_cutoff=0.5)
    out = os.path.join(temp_outdir, "test.caid")
    with open(out) as f:
        lines = f.readlines()
    binary = [int(l.split()[3]) for l in lines[1:]]
    assert binary == [0,1,1,0,1,0,1,0]

def test_write_caid_format_domain(temp_outdir):
    # Use metapredict to get a DisorderObject
    seq = "MEEEKKKK"
    disorder_obj = meta.predict_disorder_domains(seq, version="v3")
    input_dict = {"test": disorder_obj}
    meta_tools.write_caid_format(input_dict, temp_outdir, version="v3", use_fixed_cutoff=None)
    out = os.path.join(temp_outdir, "test.caid")
    with open(out) as f:
        lines = f.readlines()
    # Should have 8 residues
    assert len(lines) == 9
    # Should have at least one 1 in binary column
    binary = [int(l.split()[3]) for l in lines[1:]]
    assert 1 in binary


def test_caid_output_matches_reference(tmp_path):
    """
    Test that running predict_disorder_caid on three_seqs.fasta reproduces the exact output in caid_default.
    """
    import filecmp
    import metapredict as meta

    # Paths
    fasta_path = os.path.join(os.path.dirname(__file__), "input_data", "three_seqs.fasta")
    ref_dir = os.path.join(os.path.dirname(__file__), "input_data", "caid_default")
    # Output to a temp directory
    out_dir = tmp_path

    # Run prediction. Pin to CPU: the reference .caid files were generated
    # on CPU and this test does an exact string diff, so cuDNN LSTM's ~1e-4
    # drift from CPU is enough to change 3rd-decimal scores in the output.
    meta.predict_disorder_caid(fasta_path, str(out_dir), version="v3", device="cpu")

    # List of expected files (from reference dir)
    expected_files = [f for f in os.listdir(ref_dir) if f.endswith(".caid")]
    for fname in expected_files:
        ref_file = os.path.join(ref_dir, fname)
        out_file = os.path.join(out_dir, fname)
        assert os.path.isfile(out_file), f"Missing output file: {fname}"
        # Compare file contents exactly
        with open(ref_file, "r") as f1, open(out_file, "r") as f2:
            ref_lines = f1.readlines()
            out_lines = f2.readlines()
        assert ref_lines == out_lines, f"Output mismatch in {fname}"
