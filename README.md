This Python script matches corresponding student records from the Open Learning Initiative (OLI) and registrar's office records from the University of Maryland University College (UMUC).  The input datasets reflect records predominately from 2014.

Records are matched if the course subject, instructor last name, and one of student name or student e-mail address match.  Records are matched for the largest sections first, and by decreasing section size.  Multiple OLI records can be matched for a single UMUC record, in which case the records are merged into a single entry.

This program, joiner.py requires Python 2 and was written under Python 2.7 by me, Benjamin Steele, in March and April 2015, for the Carnegie Mellon spring consulting project in the Master's of Statistical Practice Program.  The program takes as input four filepaths, one containing the OLI data, one containing the corresponding UMUC data, one containing the joined output filename, and one for the non-joined UMUC output.

Example usage:
python joiner2.py fren_oli.txt UMUC_fren.txt fren_joined.txt fren_nooli.txt