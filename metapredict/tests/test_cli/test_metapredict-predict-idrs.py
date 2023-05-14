import subprocess
import pytest
import protfasta
import os

from . import run_command



def test_metapredict_predict_IDRs_1():
    """
    Basic test for the simplest version of

    """


    precomputed_idrs = {'Q8N6T3 IDR_START=123 IDR_END=406': 'WSLESSPAQNWTPPQPRTLPSMVHRVSGQPQSVTASSDKAFEDWLNDDLGSYQGAQGNRYVGFGNTPPPQKKEDDFLNNAMSSLYSGWSSFTTGASRFASAAKEGATKFGSQASQKASELGHSLNENVLKPAQEKVKEGKIFDDVSSGVSQLASKVQGVGSKGWRDVTTFFSGKAEGPLDSPSEGHSYQNSGLDHFQNSNIDQSFWETFGSAEPTKTRKSPSSDSWTCADTSTERRSSDSWEVWGSASTNRNSNSDGGEGGEGTKKAVPPAVPTDDGWDNQNW',
                        'p53 IDR_START=0 IDR_END=101': 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQK',
                        'p53 IDR_START=280 IDR_END=393': 'DRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD',
                        'sp|P0DMV8|HS71A_HUMAN Heat shock 70 kDa protein 1A OS=Homo sapiens OX=9606 GN=HSPA1A PE=1 SV=1 IDR_START=607 IDR_END=641': 'SGLYQGAGGPGPGGFGAQGPKGGSGSGPTIEEVD'}

    # remove output if there already
    
    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)

    ## check that there was no error
    # no error
    assert result.returncode == 0

    ## check nothing was printed to screen
    # no output
    assert "" in result.stdout

    ## Now we check the command actually worked. Read in the putative
    # outfile generated by the command
    # read 
    D = protfasta.read_fasta('output/test_1.fasta')

    ## assert this matches precomputed predictions
    for d in D:
        assert precomputed_idrs[d] == D[d]



def test_metapredict_predict_IDRs_2():
    """
    Basic test for the simplest version of

    """


    # check we can compute for different thresholds 
    precomputed_idrs = {'Q8N6T3 IDR_START=141 IDR_END=406': 'LPSMVHRVSGQPQSVTASSDKAFEDWLNDDLGSYQGAQGNRYVGFGNTPPPQKKEDDFLNNAMSSLYSGWSSFTTGASRFASAAKEGATKFGSQASQKASELGHSLNENVLKPAQEKVKEGKIFDDVSSGVSQLASKVQGVGSKGWRDVTTFFSGKAEGPLDSPSEGHSYQNSGLDHFQNSNIDQSFWETFGSAEPTKTRKSPSSDSWTCADTSTERRSSDSWEVWGSASTNRNSNSDGGEGGEGTKKAVPPAVPTDDGWDNQNW', 'p53 IDR_START=64 IDR_END=89': 'RMPEAAPPVAPAPAAPTPAAPAPAP', 'p53 IDR_START=295 IDR_END=318': 'HHELPPGSTKRALPNNTSSSPQP', 'p53 IDR_START=358 IDR_END=393': 'PGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD', 'sp|P0DMV8|HS71A_HUMAN Heat shock 70 kDa protein 1A OS=Homo sapiens OX=9606 GN=HSPA1A PE=1 SV=1 IDR_START=615 IDR_END=641': 'GPGPGGFGAQGPKGGSGSGPTIEEVD'}

    # remove output if there already
    
    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --threshold 0.9'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)

    ## check that there was no error
    # no error
    assert result.returncode == 0

    ## check nothing was printed to screen
    # no output
    assert "" in result.stdout

    ## Now we check the command actually worked. Read in the putative
    # outfile generated by the command
    # read 
    D = protfasta.read_fasta('output/test_1.fasta')

    ## assert this matches precomputed predictions
    for d in D:
        assert precomputed_idrs[d] == D[d]
        
def test_metapredict_predict_IDRs_legacy():
    """
    Basic test for the simplest version of

    """


    # check we can compute for different thresholds 
    precomputed_idrs = {'Q8N6T3 IDR_START=124 IDR_END=406': 'SLESSPAQNWTPPQPRTLPSMVHRVSGQPQSVTASSDKAFEDWLNDDLGSYQGAQGNRYVGFGNTPPPQKKEDDFLNNAMSSLYSGWSSFTTGASRFASAAKEGATKFGSQASQKASELGHSLNENVLKPAQEKVKEGKIFDDVSSGVSQLASKVQGVGSKGWRDVTTFFSGKAEGPLDSPSEGHSYQNSGLDHFQNSNIDQSFWETFGSAEPTKTRKSPSSDSWTCADTSTERRSSDSWEVWGSASTNRNSNSDGGEGGEGTKKAVPPAVPTDDGWDNQNW', 'p53 IDR_START=0 IDR_END=102': 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKT', 'p53 IDR_START=277 IDR_END=393': 'PGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD', 'sp|P0DMV8|HS71A_HUMAN Heat shock 70 kDa protein 1A OS=Homo sapiens OX=9606 GN=HSPA1A PE=1 SV=1 IDR_START=610 IDR_END=641': 'YQGAGGPGPGGFGAQGPKGGSGSGPTIEEVD'}

    # remove output if there already
    
    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --legacy'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)

    ## check that there was no error
    # no error
    assert result.returncode == 0

    ## check nothing was printed to screen
    # no output
    assert "" in result.stdout

    ## Now we check the command actually worked. Read in the putative
    # outfile generated by the command
    # read 
    D = protfasta.read_fasta('output/test_1.fasta')

    ## assert this matches precomputed predictions
    for d in D:
        assert precomputed_idrs[d] == D[d]


def test_metapredict_predict_IDRs_test_invalid_sequence_actions():
    #
    # Not super sophisticated, but checks that the different invalid sequence actions
    # perported to work can at least be passed without causing an issue
    #
    

    def check_results():
        precomputed_idrs = {'Q8N6T3 IDR_START=123 IDR_END=406': 'WSLESSPAQNWTPPQPRTLPSMVHRVSGQPQSVTASSDKAFEDWLNDDLGSYQGAQGNRYVGFGNTPPPQKKEDDFLNNAMSSLYSGWSSFTTGASRFASAAKEGATKFGSQASQKASELGHSLNENVLKPAQEKVKEGKIFDDVSSGVSQLASKVQGVGSKGWRDVTTFFSGKAEGPLDSPSEGHSYQNSGLDHFQNSNIDQSFWETFGSAEPTKTRKSPSSDSWTCADTSTERRSSDSWEVWGSASTNRNSNSDGGEGGEGTKKAVPPAVPTDDGWDNQNW',
                            'p53 IDR_START=0 IDR_END=101': 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQK',
                            'p53 IDR_START=280 IDR_END=393': 'DRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD',
                            'sp|P0DMV8|HS71A_HUMAN Heat shock 70 kDa protein 1A OS=Homo sapiens OX=9606 GN=HSPA1A PE=1 SV=1 IDR_START=607 IDR_END=641': 'SGLYQGAGGPGPGGFGAQGPKGGSGSGPTIEEVD'}
        D = protfasta.read_fasta('output/test_1.fasta')

        ## assert this matches precomputed predictions
        for d in D:
            assert precomputed_idrs[d] == D[d]




    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --invalid-sequence-action ignore'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)
    assert result.returncode == 0
    check_results()


    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --invalid-sequence-action fail'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)
    assert result.returncode == 0
    check_results()


    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --invalid-sequence-action remove'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)
    assert result.returncode == 0
    check_results()
    
    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --invalid-sequence-action convert-ignore'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)
    assert result.returncode == 0
    check_results()

    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --invalid-sequence-action convert-remove'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)
    assert result.returncode == 0
    check_results()


    cmd = 'metapredict-predict-idrs input/three_seqs.fasta -o output/test_1.fasta --invalid-sequence-action FAKE-ACTION'
    outfile = 'output/test_1.fasta'
    result = run_command(cmd, outfile)

    # expect this to be 1 because error is raised passing a bad action
    assert result.returncode == 1

    
