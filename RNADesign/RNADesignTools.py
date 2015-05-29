#!/usr/bin/env python

import logging
from eden import graph
from eden.converter.rna.rnafold import rnafold_to_eden
from eden.converter.fasta import fasta_to_sequence
from itertools import tee, izip
import random
from antaRNA.antaParams import antaParams
from antaRNA import antaRNA_v109
from RNADesign import ConstraintFinder as cf


random_gen_bound = 100000


#logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def sequence_to_fasta(sequences):
	fasta_list = []
	for sequence in sequences:
		fasta_list.append(sequence[0])
		fasta_list.append(sequence[1])
	return fasta_list


def generate_antaRNA_sequence(dot_bracket_constraint_string = None, sequence_constraint_string = None,\
							gc_content = None, original_header = None, antaParams = None):
	result = ', '.join(antaRNA_v109.findSequence(dot_bracket_constraint_string,sequence_constraint_string,gc_content,**antaParams.to_dict()))
	header = original_header + '_' + str(random.randrange(random_gen_bound))
	sequence = result.split("\n")[2]
	return header,sequence


def design_RNA(param_file = None , iterable = None, vectorizer = None, estimator = None, \
			nt_importance_threshold=0, nmin_important_nt_adjaceny=1, bp_importance_threshold=0, nmin_important_bp_adjaceny=1, \
			nmin_unpaired_nt_adjacency=1, multi_sequence_size=1):
	"""
	Function for synthesizing RNA sequences.
	Takes as input an iterator over networkx graphs and outputs an iterator 
	over fasta-seq,original-fasta-id pairs.
	Uses antaRNA for sequence synthesis and EDeN for annotating networkx graphs.
	Yields as output [header,sequence].
	"""
	assert param_file is not None, 'ERROR: empty param_file'
	op = antaParams(param_file)

	iterable = vectorizer.annotate(iterable, estimator=estimator)
	iterable = cf.generate_antaRNA_constraints(iterable, nt_importance_threshold, nmin_important_nt_adjaceny, \
											bp_importance_threshold, nmin_important_bp_adjaceny, nmin_unpaired_nt_adjacency)
	for (dot_bracket,seq_constraint,gc_content,fasta_id)  in iterable:
		for count in range(multi_sequence_size):
			result = generate_antaRNA_sequence(dot_bracket, seq_constraint, gc_content, fasta_id ,op)
			yield result


def filter_sequences(iterable = None, vectorizer = None, estimator = None , threshold = 0):
	"""
	Filter. Returns a subset of the iterable with marginal prediction above filtering_threshold.
	Takes as input a list of fasta sequences. Outputs an iterator over a list of eden sequences.
	"""
	iterable_sequence, iterable_sequence_for_graphs = tee( iterable )
	graphs = rnafold_to_eden( iterable_sequence_for_graphs )
	predictions = vectorizer.predict( graphs , estimator )
	for prediction,seq in izip( predictions , iterable_sequence):
		if prediction > threshold:
			yield seq


def design_filtered_RNA(param_file = None , iterable = None, vectorizer = None, design_estimator = None, filter_estimator = None, \
			nt_importance_threshold = 0, nmin_important_nt_adjaceny = 1, bp_importance_threshold = 0, nmin_important_bp_adjaceny = 1, \
			nmin_unpaired_nt_adjacency = 1, multi_sequence_size = 1 , filtering_threshold = 0):

	"""
	Function for synthesizing RNA sequences.
	Takes as input an iterator over networkx graphs and outputs an iterator 
	over fasta-seq,original-fasta-id pairs.
	Uses antaRNA for sequence synthesis and EDeN for annotating networkx graphs.
	Returns as output a fasta list.
	"""
	iterable = design_RNA(param_file = param_file , iterable = iterable , vectorizer = vectorizer, estimator = design_estimator, \
			nt_importance_threshold = nt_importance_threshold, nmin_important_nt_adjaceny = nmin_important_nt_adjaceny, \
			bp_importance_threshold = bp_importance_threshold, nmin_important_bp_adjaceny = nmin_important_bp_adjaceny, \
			nmin_unpaired_nt_adjacency = nmin_unpaired_nt_adjacency , multi_sequence_size = multi_sequence_size)

	iterable = filter_sequences(iterable = iterable, vectorizer = vectorizer, estimator = filter_estimator , threshold = filtering_threshold)
	return iterable


if __name__ == "__main__":


	logger.info('Call to RNA Design Tools package.')
	
	opts={'antaRNA_param_file':'/home/kohvaeip/RNAsynth/lib/antaRNA/antaRNA.ini' , \
	'nt_importance_threshold':-1.1 , 'nmin_important_nt_adjaceny':1 , 'bp_importance_threshold':-0.85 , \
	'nmin_important_bp_adjaceny':3 , 'nmin_unpaired_nt_adjacency':3 , 'multi_sequence_size':3, 'filtering_threshold':0}
	
	rfam_id = 'RF00005'
	rfam_url = 'http://rfam.xfam.org/family/%s/alignment?acc=%s&format=fastau&download=0'%(family_id,family_id) 
	iterable = fasta_to_sequence(rfam_url)
	iterable = rnafold_to_eden(iterable)

	#sequences = design_filtered_RNA()