import argparse

# In-package imports
from compare_mt import corpus_utils
from compare_mt import bucketers
from compare_mt import arg_utils
from compare_mt import print_utils
from compare_mt import formatting

def print_word_likelihood_report(ref, lls, bucket_type='freq', bucket_cutoffs=None,
                          freq_count_file=None, freq_corpus_file=None,
                          label_corpus=None, label_set=None,
                          case_insensitive=False):
  """
  Print a report comparing the word log likelihood.

  Args:
  ref: the ref of words over which the likelihoods are computed
  lls: likelihoods corresponding to each word in ref from the systems
  bucket_type: A string specifying the way to bucket words together to calculate average likelihood
  bucket_cutoffs: The boundaries between buckets, specified as a colon-separated string.
  freq_corpus_file: When using "freq" as a bucketer, which corpus to use to calculate frequency.
  freq_count_file: An alternative to freq_corpus that uses a count file in "word\tfreq" format.
  label_corpus: When using "label" as bucket type, the corpus containing the labels
                corresponding to each word in the corpus
  label_set: the permissible set of labels when using "label" as a bucket type
  case_insensitive: A boolean specifying whether to turn on the case insensitive option
  """
  case_insensitive = True if case_insensitive == 'True' else False

  bucketer = bucketers.create_word_bucketer_from_profile(bucket_type=bucket_type,
                                                         bucket_cutoffs=bucket_cutoffs,
                                                         freq_count_file=freq_count_file,
                                                         freq_corpus_file=freq_corpus_file,
                                                         label_set=label_set,
                                                         case_insensitive=case_insensitive)

  if type(label_corpus) == str:
    label_corpus = corpus_utils.load_tokens(label_corpus)

  if label_corpus is not None:
    ref = label_corpus

  lls_out = [[l for l in bucketer.calc_bucketed_likelihoods(ref, ll)] for ll in lls]

  print(f'--- average word log likelihood by {bucketer.name()} bucket')
  for i, bucket_str in enumerate(bucketer.bucket_strs):
    print (bucket_str + "\t", end='')
    for ll_out in lls_out:
      print(f"{formatting.fmt(ll_out[i])}\t", end="")
    print()

def main():
  parser = argparse.ArgumentParser(
    description='Program to compare MT results',
  )
  parser.add_argument('--ref-file', type=str, dest='ref_file',
                    help='A path to a reference file over which the likelihoods are being computed/compared')
  parser.add_argument('--ll-files', type=str, nargs='+', dest='ll_files',
                    help='A path to file containing log likelihoods for ref-file generated by systems')
  parser.add_argument('--compare-word-likelihoods', type=str, dest='compare_word_likelihoods', nargs='*',
                    default=['bucket_type=freq'],
                    help="""
                    Compare word log likelihoods by buckets. Can specify arguments in 'arg1=val1,arg2=val2,...' format.
                    See documentation for 'print_word_likelihood_report' to see which arguments are available.
                    """)
  parser.add_argument('--decimals', type=int, default=4,
                      help="Number of decimals to print for floating point numbers")

  args = parser.parse_args()

  # Set formatting
  
  # Set formatting
  formatting.fmt.set_decimals(args.decimals)

  ref = corpus_utils.load_tokens(args.ref_file)
  lls = [corpus_utils.load_nums(x) for x in args.ll_files] 

  # Word likelihood analysis
  if args.compare_word_likelihoods:
    print_utils.print_header('Word Likelihood Analysis')
    for profile in args.compare_word_likelihoods:
      kargs = arg_utils.parse_profile(profile)
      print_word_likelihood_report(ref, lls, **kargs)
      print()


if __name__ == '__main__':
  main()
