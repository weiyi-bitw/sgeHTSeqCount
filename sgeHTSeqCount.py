import HTSeq
import numpy
import time
import itertools
import getopt
import sys
import os


# argv:
#   --jobID: Job ID
#   -g, --gtf: gtf file
#   -s, --sam: sam file
#   -b, --bam: bam file
#   -f, --folder: folder that contains SAM/BAM files
#   -o, --output: output file
#   --segID: this segment
#   --totalSegs: total segments

def clear(target):
  lst = os.listdir(target)
  for f in lst:
    os.remove(target + "/" + f)
  os.rmdir(target)

def main():
  print "====================================================="
  print "            Welcome to sgeHTSeqCount v0.02     "
  print 
  print "                                    Wei-Yi Cheng     "
  print "                                      04/24/2011     "
  print "====================================================="

  #=============================================
  # default argument settings

  gtf_file = None
  bam_file = None
  sam_file = None
  target_folder = "./"
  out_file = "exprsCount.txt"
  segment = 0
  totalSegs = 1
  jobID = int(time.time())

  usingBam = False
  batchProcess = False

  try:
    opts, args = getopt.getopt(sys.argv[1:], "g:s:b:o:f:", ["gtf=", "sam=", "bam=", "output=", "segID=", "totalSegs=", "jobID=", "folder="])
  except getopt.GetoptError, err:
    print str(err)
    # usage()
    sys.exit(2)                                
  for opt, arg in opts:
    if opt in ("-g", "--gtf"):
      gtf_file = arg
    elif opt in ("-s", "--sam"):
      sam_file = arg
    elif opt in ("-b", "--bam"):
      bam_file = arg
      usingBam = True
    elif opt in ("-f", "--folder"):
      target_folder = arg
      batchProcess = True
    elif opt in ("o", "--output"):
      out_file = arg
    elif opt == "--jobID":
      jobID = arg
    elif opt == "--segID":
      segment = int(arg)
    elif opt == "--totalSegs":
      totalSegs = int(arg)

  if(sam_file != None and usingBam):
    print "Warning: both SAM file and BAM file input exist, using BAM file."  

  if(gtf_file == None):
    print "ERROR: GTF file cannot be empty"
    # usage()
    sys.exit(2)

  if(sam_file == None and bam_file == None):
    print "**No target file is assigned, processing current directory."
    batchProcess = True

  #===========================================
  # output session information

  print
  print "{0:25s}:{1}".format("Job ID", jobID)
  print "{0:25s}:{1}".format("GTF File", gtf_file)
  if batchProcess:
    print "{0:25s}:{1}".format("Target Folder:", target_folder)
  else:  
    if usingBam: 
      print "{0:25s}:{1}".format("BAM File", bam_file)
    else:
      print "{0:25s}:{1}".format("SAM File", sam_file)
  print "{0:25s}:{1}".format("Output File", out_file)
  print "{0:25s}:{1:d}".format("This Segment", segment)
  print "{0:25s}:{1:d}".format("Total Segment", totalSegs)
  print
  print "========================================================"

  fileList = []
  
  if batchProcess :
    lst = os.listdir(target_folder)
    usingBam = True
    for f in lst:
      if f.endswith(".bam"):
        fileList.append(f)
    if len(fileList) == 0:
      usingBam = False
      for f in lst:
        if f.endswith(".sam"):
          fileList.append(f)
    if len(fileList) == 0:
      print "No .sam or .bam file in current folder. Exit."
      sys.exit(0)
  elif usingBam:
    fileList.append(bam_file)
  else:
    fileList.append(sam_file)
  numFiles = len(fileList)
  fileList.sort()
  
  

  outputDir = "output/" + str(jobID)
  try:
    os.mkdir("output")
    print "Output directory created."
  except OSError:
    None
  try:
    os.mkdir(outputDir)
    print "Job directory created."
  except OSError:
    None

    
  # Set starting time point
  t0 = time.clock()

  gtf_file = HTSeq.GFF_Reader( gtf_file )
  
  print "Creating exon arrays..."
  rowmap = {}
  exons = HTSeq.GenomicArrayOfSets( "auto", stranded=True )
  for feature in gtf_file:
    if feature.type == "exon":
      exons[ feature.iv ] += feature.name
      rowmap[feature.name] = 0
  featureList = rowmap.keys()
  featureList.sort()
  numGenes = len(featureList)

  print "{0:25s}:{1}".format("Features:", numGenes)
  print "{0:25s}:{1}".format("Files:", numFiles)

  t1 = time.clock()
  print "Done. [" + str(t1-t0) + "]"


  print "Counting alignments..."

  lclCount = {}
  
  for f in fileList:
    lclCount[f] = {}
    print "Processing " + f + "..."
    if usingBam:
      in_file = HTSeq.BAM_Reader( target_folder + f )
    else:
      in_file = HTSeq.SAM_Reader( target_folder + f )
    lineCount = 0
    for alnmt in in_file:
      if lineCount%totalSegs == segment:
        None
#        if alnmt.aligned:
#          intersection_set = None
#          alnmt.iv.chrom = alnmt.iv.chrom.replace('chr', '')
#          for iv2, step_set in exons[ alnmt.iv ].steps():
#            if intersection_set is None:
#              intersection_set = step_set.copy()
#            else:
#              intersection_set.intersection_update( step_set )
#          if len( intersection_set ) == 1:
#            try:
#              lclCount[f][list(intersection_set)[0]] += 1
#            except KeyError:
#              lclCount[f][list(intersection_set)[0]] = 1
      lineCount += 1
  t2 = time.clock()
  print "Done.[" + str(t2-t1) + "]"


  tmpDir = "tmp/" + str(jobID)
  try:
    os.mkdir("tmp")
    print "tmp directory created."
  except OSError:
    None
  try:
    os.mkdir(tmpDir)
  except OSError:
    None
  print "Output to file..."
  fOut = open(tmpDir + "/cnt-" + '%05d' % segment , 'w')
  for f in lclCount.keys():
    for ff in lclCount[f].keys(): 
      fOut.write(f + "\t" + ff + "\t" + str(lclCount[f][ff]) + "\n")
  
  fOut.close()

  try:
    os.mkdir(".finish")
  except OSError:
    None
  try:
    os.mkdir(".finish/" + str(jobID))
  except OSError:
    None

  fOut = open(".finish/" + str(jobID) + "/flag-"+ '%05d' % segment , 'w')
  fOut.close()
  t3 = time.clock()
  print "Finish flag created."


  if segment == 0 :
    
    while True:
      print "Waiting for other segments to finish..."
      numFlags = len(os.listdir(".finish/" + str(jobID)))
      if(numFlags == totalSegs):
        t4 = time.clock()
        print "Spawn finished, proceed...[" + str(t4-t3) + "]"
        break
      else:
        time.sleep(1)
    
    cnt = 0
    for f in featureList:
      rowmap[f] = cnt
      cnt += 1
    colmap = {}
    cnt = 0
    for f in fileList:
      colmap[f] = cnt
      cnt += 1
    
    print "Gathering segment files...",
    counts = numpy.zeros([numGenes, numFiles], int)      
    lst = os.listdir(tmpDir)
    numTmpFiles = len(lst)
    if numTmpFiles != totalSegs:
      print "Number of count files is different from number of segments!"
      sys.exit(2)
    for f in lst:
      fIn = open(tmpDir + "/" + f, 'r')
      for line in fIn:
        line = line.strip('\n')
        line = line.split('\t')
        counts[rowmap[line[1]]][colmap[line[0]]] += int(line[2])
      fIn.close()
    t5 = time.clock()
    print "Done. [" + str(t5 - t4) + "]"

    print "Output to file...",
    fOut = open(outputDir + "/" + out_file, 'w')
    for name in fileList:
      fOut.write("\t" + name)
    fOut.write("\n")
    for gene in featureList:
      fOut.write(gene)
      for name in fileList:
        fOut.write("\t" + str(counts[rowmap[gene]][colmap[name]]))
      fOut.write("\n")
    fOut.close()
    print "Done."

  clear(tmpDir)
  clear(".finish/" + str(jobID))

  processingTime = time.clock() - t0

  print "==================================================="
  print "Done in " + str(processingTime) + " seconds."

if __name__ == "__main__":
    sys.exit(main())
