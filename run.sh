#!/bin/bash

function help() {
     echo "Usage:  $0 target[party|client] nums[nums_server|nums_party] configFile" >&2
     echo "Example: "
     echo "       - bash run.sh party config/c0_config.yml"
     echo "       - bash run.sh client config/client_config.yml"
}

if [ "$#" -ne 3 ] ; then
  echo "Missing Parameters ..."
  help
  exit 1
fi

target=$1
nums_party=$2
nums_server=$2
configFile=$3



# shellcheck disable=SC2006
RootPath=$(pwd)
export PYTHONPATH=${PYTHONPATH}:${RootPath}

BinPath=${RootPath}/bin; [ -d "$BinPath" ] || mkdir -p "$BinPath"
SrcPath=${RootPath}/src; [ -d "$SrcPath" ] || mkdir -p "$SrcPath"
LogPath=${RootPath}/logs; [ -d "$LogPath" ] || mkdir -p "$LogPath"
CfgPath=${RootPath}/config; [ -d "$CfgPath" ] || mkdir -p "$CfgPath"
CurrentDate=$(date +%F)
#ConfigFile=${CfgPath}/default_config.yml
LogFile=${LogPath}/${CurrentDate}.log






case ${target} in
   "party")
      set -x
      python "${SrcPath}"/party.py -config "$configFile" -project_dir "${RootPath}" -project_log "${LogFile}" -nums_server ${nums_server}
      ;;
   "client")
      set -x
      python "${SrcPath}"/client.py -config "$configFile" -project_dir "${RootPath}" -project_log "${LogFile}" -nums_party ${nums_party}
      ;;
   *)
      echo "The wrong input paramters"
      help
      ;;
esac