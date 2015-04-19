# OLI-UMUC Project
# Benjamin Steele, 3/21/2015

## This program takes as input four filenames, one containing the 
## OLI data, one containing the corresponding UMUC data, one containing
## the joined output filename, and one for the non-joined UMUC output.
##
## Matches rows in the OLI datafile with rows in the UMUC datafile.
## Example usage:
## python joiner2.py fren_oli.txt UMUC_fren.txt fren_joined.txt fren_nooli.txt
## python joiner2.py psyc_oli.txt UMUC_psyc.txt psyc_joined.txt psyc_nooli.txt
## python joiner2.py stat_oli.txt UMUC_stat.txt stat_joined.txt stat_nooli.txt


import sys
import itertools
from collections import Counter

oli_filename = sys.argv[1]
umuc_filename = sys.argv[2]
output_filename = sys.argv[3]
unpaired_filename = sys.argv[4]

oli_file = open(oli_filename,"r")
oli = oli_file.readlines()
oli_file.close()

umuc_file = open(umuc_filename,"r")
umuc = umuc_file.readlines()
umuc_file.close()

matched_oli = []
matched_umuc = []

line_ids = []
lines_written = -1 ## -1 to account for the title row

## Part 1: Making all legal matches.
## Stores the results of all legal matches in "proposed_joins" and "line_ids".

oli_linecount = -1

for oli_line in oli:

	oli_linecount += 1
	if oli_linecount > 1:
		oli_split = oli_line.split("\t")

		#print oli_split[1]

		umuc_linecount = -1
		for umuc_line in umuc:
			umuc_linecount += 1

			#print oli_split[1],umuc_line[0:5]

			if umuc_linecount > 1:
				umuc_split = umuc_line.split("\t")

				#print oli_split[1],umuc_split[3]

				if oli_split[1] == umuc_split[3] or oli_split[0] == umuc_split[2]: ## if e-mail addresses match or full names match

					## ALSO REQUIRE: UMUC instructor last name is contained in OLI instructor names
					umuc_instructor_name = umuc_split[-1].replace('"','').replace(" ",",").split(",")[0].upper()
					##Taking only the first "chunk" of UMUC instructor name, uppercase.

					if umuc_instructor_name in oli_split[19]: #if instructor names match
						line_ids.append([oli_split[2]+" "+umuc_split[10],oli_linecount,umuc_linecount])
						## Appends the section_guid and class ID counts.




## Part 2: Selecting out specific desired matches.
## We begin by counting the occurrences of specific class ID - section_guid pairs.
## The most frequent pair is assumed to be correct.  All OLI observations involved in this pair are removed from the pair pool.
## We then repeat this process, selecting the next most frequent match, until no further legal pairs can be made.
## The (OLI line number, UMUC line number) for all pairings to be made are stored.

matches_made = []

while len(line_ids) > 0:

	oli_entries_to_delete = []
	umuc_entries_to_delete = []
	indices_to_delete = []

	most_frequent_match = Counter([x[0] for x in line_ids]).most_common(1)[0][0]

	## Finds all the OLI rows that need to be deleted (have been matched) from the list of prospective matches.
	## Also does the same for the already-matched UMUC rows.
	## This allows the same UMUC record to be matched multiple times within a section, but not multiple
	## times across sections.  We will deal with the multiple-UMUC issue in parts 3 and 4.

	for entry in line_ids:
		
		if entry[0] == most_frequent_match:
			matches_made.append([entry[1], entry[2]])
			oli_entries_to_delete.append(entry[1])
			umuc_entries_to_delete.append(entry[2])


	## Finds all the prospective matches containing an OLI row to delete or UMUC row to delete.
	entry_counter = -1
	for line in line_ids:
		entry_counter += 1

		if line[1] in oli_entries_to_delete or line[2] in umuc_entries_to_delete:
			indices_to_delete.append(entry_counter)


	## Deletes all the prospective matches containing an OLI row to delete.
	for index in sorted(indices_to_delete,reverse=True):
		del line_ids[index]
	

## Part 3: identify the cases where the same UMUC row is used multiple times

rows_merged = len(matches_made) - len(set([z[1] for z in matches_made]))
reused_umuc_rows = [x for x, y in Counter([z[1] for z in matches_made]).items() if y > 1] 


## Part 4: Returning to the original files to make the selected matches.
## Also merges rows that correspond to the same UMUC record.

matches_made.insert(0,[0,0]) ## ensures title rows are carried over by inserting the titles at the beginning

output_file = open(output_filename,"w")

need_merging = []

for match in matches_made:
	if match[1] not in reused_umuc_rows:
		output_file.write(oli[match[0]].rstrip("\n")+"\t"+umuc[match[1]])
		lines_written += 1
	else:
		need_merging.append(match)

need_merging.sort(key=lambda x: x[1]) ## Need to sort since can't guarantee will be in sorted-by-UMUC key order.


for key, group in itertools.groupby(need_merging, lambda x: x[1]):

	## The numeric stats are, in order:
	## total_logins	dashboard_views	dashboard_actions	myscores_views	myscores_actions
	## pages_accessed	total_pageviews	activities_started	learnbydoing_started
	## didigetthis_started	myresponse_started	myresponse_finished	quiz_started	quiz_finished
	## quiz_first_attempt_mean	quiz_first_attempt_stdev
	## last two are float, others integer
	##
	## Most statistics are just added.  OLI personal info taken from final line.
	## Quiz mean appropriately calculated.  Quiz s.d. taken from record with most quizzes.

	numeric_stats = [0,0,0,0,0,0,0,0,0,0,0,0,0.0,0.0]
	quizzes = []

	for record_to_merge in group:
		split_record = oli[record_to_merge[0]].split("\t")
		for i in xrange(5,17):
			numeric_stats[i-5] += int(split_record[i])
		if split_record[16] != "0": ## if there were any quizzes associated with this record
			quizzes.append([int(split_record[16]),float(split_record[17]),float(split_record[18])])

	if len(quizzes) > 0:
		quiz_num = sum([x[0] for x in quizzes])
		numeric_stats[12] = "{0:.4f}".format(sum(x[0]*x[1]/quiz_num for x in quizzes))
		numeric_stats[13] = "{0:.4f}".format(quizzes[[x[0] for x in quizzes].index(max([x[0] for x in quizzes]))][2])

	output_file.write("\t".join(split_record[0:5] + [str(z) for z in numeric_stats] + split_record[19:-1]) + "\t" + split_record[-1][:-1] + "\t" + umuc[key].strip()+"\n")
	## last entry of split_record has \n at end, so need to remove that
	lines_written += 1

output_file.close()


## Part 5: Writing the non-OLI-paired UMUC data out to the secondary output file.

unpaired_out = open(unpaired_filename,"w")

unpaired_out.write(umuc[0]) ## Prints the header line.

unpaired_count = 0

for line_index in xrange(len(umuc)):
	if line_index not in [x[1] for x in matches_made]:
		unpaired_out.write(umuc[line_index])
		unpaired_count += 1

unpaired_out.close()



## Part 6: Printing a brief summary of the operations to the command line.

print lines_written, "matches made on", len(oli)-1-rows_merged,"OLI records! ("+str(len(oli)-1)+" original,", rows_merged,"merged) Paired output written to", output_filename, "and", unpaired_count,"unpaired UMUC entries to", unpaired_filename +"."

