#!/bin/bash




echo "Running opitmizaton look"
## Looping through the mask being on and off
## If mask==0
for mask in {0}
 do 
  echo "$mask"
  
  if [ $mask -eq 0 ]
  then
   echo "mask is now off"
   sbatch full_optimization_loop.sh $suffix 0 False            ## Running for the one case of no mask
   sleep 10

  else
   echo "mask is now on"
   for m_style in {1,5,1_fill,5_fill}
   # for m_style in {1..1}
    do
     echo "$m_style"
     sbatch full_optimization_loop.sh $suffix $m_style True    ## Looping for the case of mask and all degree types
     sleep 15
    done 
  fi
 done
 
