graph-disorder
==============

``graph-disorder`` is a command from that takes a .fasta file as input and returns a .png for every sequence within the .fasta file. The .png files for each sequence will be saved to wherever the user specifies as the output location. Each file will be named as predicted\_disorder\_ followed by the first 10 characters of the .fasta header (which is typically the unique identifier for the protein). For example, a fasta header of >sp|Q8N6T3|ARFG1_HUMAN will return a file saved as *predicted_disorder_sp|Q8N6T3|.png*. Additionally, the title of each graph is automatically generated and will have the title Predicted Protein Disorder followed by the first 10 characters of the .fasta header. In the previous example, the graph would be titled *Predicted Protein Disorder sp|Q8N6T3|*.

Once metapredict is installed, the user can run ``graph-disorder`` from the command line:

.. code-block:: bash
	
	$ graph-disorder <Path to .fasta file> <Path where to save the output> <flags>

**Example:** 

.. code-block:: bash
	
	$ graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/


**WARNING:**
This command will generate a .png file for ***every*** sequence in the .fasta file. If you have 1,000 sequences in a .fasta file, it will generate **1,000** files. Therefore, I recommend saving the output to a dedicated folder (or at least not your Desktop...).


**Additional Usage:**

**Changing resolution of save graphs:**
``--DPI`` / ``-D`` 

By default, the output files have a DPI of 150. However, the user can change the DPI of the output (higher values have greater resolution but take up more space). To change the DPI simply add the flage -D followed by the wanted DPI value.

**Example:** 

.. code-block:: bash
	
	$ graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ -D 300

**Remove non-alphabetic characters from file name:**
``--remove_characters``

By default, the output files contain characters that are non-alphabetic (example *predicted_disorder_sp|Q8N6T3|.png*). This is not a problem on some operating systems, while others do not allow files to have names that contain certain characters. To get around this, you can add the --remove_characters flag. This will remove all non-alphabetic characters from the .fasta header when saving the file. The previous example with the header >sp|Q8N6T3|ARFG1_HUMAN would now save as *predicted_disorder_spQ8N726AR.png*.

**Example:** 

.. code-block:: bash
	
	$ graph-disorder /Users/thisUser/Desktop/interestingProteins.fasta /Users/thisUser/Desktop/DisorderGraphsFolder/ --remove_characters
