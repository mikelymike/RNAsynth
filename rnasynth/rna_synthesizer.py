#!/usr/bin/env python


from itertools import tee
from itertools import izip
import logging

from sklearn.linear_model import SGDClassifier

from eden.converter.fasta import fasta_to_sequence
from eden.converter.rna.rnashapes import rnashapes_to_eden
from eden.util import fit as optimized_estimator_fit
from eden.graph import Vectorizer
from eden.modifier.seq import seq_to_seq
from eden.modifier.seq import shuffle_modifier
from eden.converter.rna.rnafold import rnafold_to_eden

from rnasynth.constraint_extractor import ConstraintExtractor
from rnasynth.rna_designer import AntaRNAv117Designer


logger = logging.getLogger(__name__)


class RNASynthesizerInitializer(object):

    """ Main class for instantiating an instance of the RNASynth class.


     RNASynthesizerInitializer receives all the parameters which are used in initializing the following
     objects which are then used to initialize an instance of the RNASynth class:
     - SGDClassifier
     - ConstraintExtractor
     - AntaRNAv117Designer
     - PreProcessor
     - Vectorizer

     Parameters
     ----------

     SGDClassifier

     average : bool (default True)

     class_weight : str (default 'auto')

     shuffle : bool (default True)

     n_jobs : int (default -1)

     cv : int (default 3)

     n_iter_search : int (default 1)

     For parameter description, please refer to :
     https://github.com/scikit-learn/scikit-learn/blob/c957249/sklearn/linear_model/stochastic_gradient.py#L548


     ConstraintExtractor

     importance_threshold_sequence_constraint : int (default 0)
             Classification score threshold for identifying important nucleotides in a sequence.

     min_size_connected_component_sequence_constraint : int (default 1)
             Minimum number of adjacent important nucleotides which can form a sequence constraint.

     importance_threshold_structure_constraint : int (default 0)
             Classification score threshold for labeling important basepairs in a secondary structure.

     min_size_connected_component_structure_constraint : int (default 1)
             Minimum number of adjacent basepairs which can form a secondary structure constraint.

     min_size_connected_component_unpaired_structure_constraint : int (default 1)
             Minimum number of adjacent backbones which can form a secondary structure constraint.


     AntaRNAv117Designer

     Cstr : str (default "")

     Cseq : str (default "")

     tGC : list (default [])

     level : int (default 1)

     tGCmax : float (default -1.0)

     tGCvar : float (default -1.0)

     temperature : float (default 37.0)

     paramFile : str (default "")

     noGUBasePair : bool (default False)

     noLBPmanagement : bool (default True)

     pseudoknots : bool (default True)

     usedProgram : str (default "RNAfold")

     pkprogram : str (default "pKiss")

     pkparameter : bool (default False)

     HotKnots_PATH : str (default "")

     strategy : str (default "A")

     noOfColonies : int (default 1)

     output_file : str (default "STDOUT")

     py : bool (default True)

     name : str (default "antaRNA")

     verbose : bool (default False)

     output_verbose : bool (default False)

     seed : str (default "none")

     improve_procedure : (default "s")

     Resets : int (default 5)

     ants_per_selection: int (default 10)

     ConvergenceCount : int (default 130)

     antsTerConv : int (default 50)

     alpha : float (default 1.0)

     beta : float (default 1.0)

     ER : float (default 0.2)

     Cstrweight : float (default 0.5)

     Cgcweight : float (default 5.0)

     Cseqweight : float (default 1.0)

     omega : float (default 2.23)

     time : int (default 600)

     For parameter description, please refer to :
     https://github.com/RobertKleinkauf/antaRNA


     PreProcessor

     shape_type: int (default 5)

     energy_range : int (default 35)

     max_num : int (deafult 3)

     split_components : bool (default True)

     For parameter description, please refer to :
     https://github.com/fabriziocosta/EDeN/blob/master/eden/converter/rna/rnashapes.py


     RNASynth

     n_synthesized_sequences_per_seed_sequence : int (default 2)
             Option for setting the number of synthesized sequences per constraint.


     instance_score_threshold_in : int (default 0)
             Predicted score threshold for filtering synthesized sequences.

     instance_score_threshold_out :int (default 1)
            Predicted score threshold for filtering graphs.

     train_to_test_split_ratio : float (default 0.2)
             Ratio for splitting the sample dataset into train and test datasets.

     shuffle_order : int (default 2)
             Eden.modifier.seq.seq_to_seq parameter.

     negative_shuffle_ratio : int (default 2)
             Number of negative sample sequences generated for each positive sample.

     vectorizer_complexity : int (default 2)
             eden.graph.Vectorizer parameter.

     max_num_graphs_per_seq: int (default 3)
             eden.converter.rna.rnashapes.rnashapes_to_eden parameter.


     Vectorizer

     vectorizer_complexity : int (default 2)

     r : int (default None)

     d : int (default None)

     min_r : int (default 0)

     min_d : int (default 0)

     For parameter description, please refer to :
     https://github.com/fabriziocosta/EDeN/blob/master/eden/graph.py
    """

    def __init__(self,
                 # classifier params
                 average=True,
                 class_weight='auto',
                 shuffle=True,
                 # constraint_extractor params
                 importance_threshold_sequence_constraint=0,
                 min_size_connected_component_sequence_constraint=1,
                 importance_threshold_structure_constraint=0,
                 min_size_connected_component_structure_constraint=1,
                 min_size_connected_component_unpaired_structure_constraint=1,
                 # designer
                 Cstr="",
                 Cseq="",
                 tGC=[],
                 level=1,
                 tGCmax=-1.0,
                 tGCvar=-1.0,
                 temperature=37.0,
                 paramFile="",
                 noGUBasePair=False,
                 noLBPmanagement=True,
                 pseudoknots=False,
                 usedProgram="RNAfold",
                 pkprogram="pKiss",
                 pkparameter=False,
                 HotKnots_PATH="",
                 strategy="A",
                 noOfColonies=1,
                 output_file="STDOUT",
                 py=True,
                 name="antaRNA",
                 verbose=False,
                 output_verbose=False,
                 seed="none",
                 improve_procedure="s",
                 Resets=5,
                 ants_per_selection=10,
                 ConvergenceCount=130,
                 antsTerConv=50,
                 alpha=1.0,
                 beta=1.0,
                 ER=0.2,
                 Cstrweight=0.5,
                 Cgcweight=5.0,
                 Cseqweight=1.0,
                 omega=2.23,
                 time=600,
                 # pre_processor
                 shape_type=5,
                 energy_range=35,
                 max_num=3,
                 split_components=True,
                 # synthesizer
                 instance_score_threshold_in=0,
                 instance_score_threshold_out=1,
                 shuffle_order=2,
                 negative_shuffle_ratio=2,
                 vectorizer_complexity=2,
                 r=None,
                 d=None,
                 min_r=0,
                 min_d=0,
                 n_jobs=-1,
                 cv=3,
                 n_iter_search=1,
                 n_synthesized_seqs_per_seed_seq=3
                 ):

        self.constraint_extractor = ConstraintExtractor(
            importance_threshold_sequence_constraint=importance_threshold_sequence_constraint,
            min_size_connected_component_sequence_constraint=min_size_connected_component_sequence_constraint,
            importance_threshold_structure_constraint=importance_threshold_structure_constraint,
            min_size_connected_component_structure_constraint=min_size_connected_component_structure_constraint,
            min_size_connected_component_unpaired_structure_constraint=min_size_connected_component_unpaired_structure_constraint)

        self.designer = AntaRNAv117Designer(Cstr=Cstr,
                                            Cseq=Cseq,
                                            tGC=tGC,
                                            level=level,
                                            tGCmax=tGCmax,
                                            tGCvar=tGCvar,
                                            temperature=temperature,
                                            paramFile=paramFile,
                                            noGUBasePair=noGUBasePair,
                                            noLBPmanagement=noLBPmanagement,
                                            pseudoknots=pseudoknots,
                                            usedProgram=usedProgram,
                                            pkprogram=pkprogram,
                                            pkparameter=pkparameter,
                                            HotKnots_PATH=HotKnots_PATH,
                                            strategy=strategy,
                                            noOfColonies=noOfColonies,
                                            output_file=output_file,
                                            py=py,
                                            name=name,
                                            verbose=verbose,
                                            output_verbose=output_verbose,
                                            seed=seed,
                                            improve_procedure=improve_procedure,
                                            Resets=Resets,
                                            ants_per_selection=ants_per_selection,
                                            ConvergenceCount=ConvergenceCount,
                                            antsTerConv=antsTerConv,
                                            alpha=alpha,
                                            beta=beta,
                                            ER=ER,
                                            Cstrweight=Cstrweight,
                                            Cgcweight=Cgcweight,
                                            Cseqweight=Cseqweight,
                                            omega=omega,
                                            time=time)

        self.pre_processor = PreProcessor(shape_type=shape_type,
                                          energy_range=energy_range,
                                          max_num=max_num,
                                          split_components=split_components)

        self.estimator = SGDClassifier(average=average,
                                       class_weight=class_weight,
                                       shuffle=shuffle)

        self.vectorizer = Vectorizer(complexity=vectorizer_complexity,
                                     r=r,
                                     d=d,
                                     min_r=min_r,
                                     min_d=min_d)

        self.synthesizer = RNASynth(estimator=self.estimator,
                                    vectorizer=self.vectorizer,
                                    designer=self.designer,
                                    pre_processor=self.pre_processor,
                                    constraint_extractor=self.constraint_extractor,
                                    n_synthesized_seqs_per_seed_seq=n_synthesized_seqs_per_seed_seq,
                                    instance_score_threshold_in=instance_score_threshold_in,
                                    instance_score_threshold_out=instance_score_threshold_out,
                                    shuffle_order=shuffle_order,
                                    negative_shuffle_ratio=negative_shuffle_ratio,
                                    n_jobs=n_jobs,
                                    cv=cv,
                                    n_iter_search=n_iter_search)
        logger.debug('Created a RNASynthesizer object.')

    def init_synthesizer(self):
        return self.synthesizer


class PreProcessor(object):

    def __init__(self,
                 shape_type=5,
                 energy_range=35,
                 max_num=3,
                 split_components=True
                 ):
        self.shape_type = shape_type
        self.energy_range = energy_range
        self.max_num = max_num
        self.split_components = split_components
        logger.debug('Created a PreProcessor object.')

    def transform(self, seqs=None, mfe=False):
        if mfe is False:
            graphs = rnashapes_to_eden(seqs,
                                       shape_type=self.shape_type,
                                       energy_range=self.energy_range,
                                       max_num=self.max_num,
                                       split_components=self.split_components)
        else:
            graphs = rnafold_to_eden(seqs)
        return graphs


class RNASynth(object):

    def __init__(self,
                 estimator=SGDClassifier(),
                 vectorizer=Vectorizer(),
                 pre_processor=PreProcessor(),
                 designer=AntaRNAv117Designer(),
                 constraint_extractor=ConstraintExtractor(),
                 n_synthesized_seqs_per_seed_seq=3,
                 instance_score_threshold_in=0,
                 instance_score_threshold_out=1,
                 shuffle_order=2,
                 negative_shuffle_ratio=2,
                 n_jobs=-1,
                 cv=3,
                 n_iter_search=1
                 ):

        self.estimator = estimator
        self.vectorizer = vectorizer
        self.designer = designer
        self.pre_processor = pre_processor
        self.constraint_extractor = constraint_extractor

        self._n_synthesized_seqs_per_seed_seq = n_synthesized_seqs_per_seed_seq
        self._instance_score_threshold_in = instance_score_threshold_in
        self._instance_score_threshold_out = instance_score_threshold_out
        self._shuffle_order = shuffle_order
        self._negative_shuffle_ratio = negative_shuffle_ratio
        self._n_jobs = n_jobs
        self._cv = cv
        self._n_iter_search = n_iter_search

        logger.debug('Instantiated an RNASynth object.')
        logger.debug(self.__dict__)

    def __repr__(self):
        obj_str = 'RNASynth:\n'
        obj_str += 'Dataset:\n'
        obj_str += 'shuffle_order: %d\n' % self._shuffle_order
        return obj_str

    def _binary_classification_setup(self,
                                     seqs=None,
                                     negative_shuffle_ratio=None,
                                     shuffle_order=None):
        seqs, seqs_ = tee(seqs)
        graphs = self.pre_processor.transform(seqs, mfe=False)
        seqs_neg = seq_to_seq(seqs_,
                              modifier=shuffle_modifier,
                              times=negative_shuffle_ratio,
                              order=shuffle_order)
        graphs_neg = self.pre_processor.transform(seqs_neg)
        return graphs, graphs_neg

    def fit(self, seqs):
        graphs, graphs_neg = self._binary_classification_setup(
            seqs=seqs,
            negative_shuffle_ratio=self._negative_shuffle_ratio,
            shuffle_order=self._shuffle_order)
        self.estimator = optimized_estimator_fit(graphs,
                                                 graphs_neg,
                                                 self.vectorizer,
                                                 n_jobs=self._n_jobs,
                                                 cv=self._cv,
                                                 n_iter_search=self._n_iter_search)
        return self

    def _design(self, graphs):
        graphs = self.vectorizer.annotate(graphs, estimator=self.estimator)
        iterable = self.constraint_extractor.extract_constraints(graphs)
        for (dot_bracket, seq_constraint, gc_content, fasta_id) in iterable:
            for count in range(self._n_synthesized_seqs_per_seed_seq):
                sequence = self.designer.design((dot_bracket, seq_constraint, gc_content))
                header = fasta_id + ';' + str(count) + ';' +\
                    dot_bracket.replace('A', '-') + ';' +\
                    seq_constraint.replace('N', '-')
                yield header, sequence

    def _filter_graphs(self, graphs):
        graphs, graphs_ = tee(graphs)
        predictions = self.vectorizer.predict(graphs, self.estimator)
        for prediction, graph in izip(predictions, graphs_):
            if prediction > self._instance_score_threshold_in:
                yield graph

    def _filter_seqs(self, seqs):
        seqs, seqs_ = tee(seqs)
        graphs = self.pre_processor.transform(seqs, mfe=True)
        predictions = self.vectorizer.predict(graphs, self.estimator)
        for prediction, seq in izip(predictions, seqs_):
            if prediction > self._instance_score_threshold_out:
                yield seq

    def sample(self, seqs):
        graphs = self.pre_processor.transform(seqs, mfe=False)
        graphs = self._filter_graphs(graphs)
        seqs = self._design(graphs)
        seqs = self._filter_seqs(seqs)
        return seqs

    def fit_sample(self, seqs):
        seqs, seqs_ = tee(seqs)
        seqs = self.fit(seqs).sample(seqs_)
        return seqs

    def predict(self, seqs):
        graphs = self.pre_processor.transform(seqs, mfe=True)
        predictions = self.vectorizer.predict(graphs, self.estimator)
        for prediction in predictions:
            yield prediction


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    logger.info('Call to RNASynthesizer module.')

    rfam_id = 'RF01685'
    iterable_seq = fasta_to_sequence(
        'http://rfam.xfam.org/family/%s/alignment?acc=%s&format=fastau&download=0' % (rfam_id, rfam_id))
    synthesizer = RNASynthesizerInitializer().synthesizer
    synth_seqs = synthesizer.fit_sample(iterable_seq)
    for header, seq in synth_seqs:
        print header
        print seq
