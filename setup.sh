# Setup python 3
source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh  # load analysis python environment
export PS1='(l1005322) \w> '  # convenient way to know we are in an analysis environment
export PYTHONPATH=$(cd ./reborn; pwd)  # tell python where to find reborn
export PYTHONPATH=$PYTHONPATH:/sdf/data/lcls/ds/cxi/cxily5921/scratch/denss
