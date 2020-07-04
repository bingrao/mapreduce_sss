#!/bin/bash

# shellcheck disable=SC2006
RootPath=$(pwd)
export PYTHONPATH=${PYTHONPATH}:${RootPath}

BinPath=${RootPath}/bin; [ -d "$BinPath" ] || mkdir -p "$BinPath"
SrcPath=${RootPath}/src; [ -d "$SrcPath" ] || mkdir -p "$SrcPath"
LogPath=${RootPath}/logs; [ -d "$LogPath" ] || mkdir -p "$LogPath"
CfgPath=${RootPath}/config; [ -d "$CfgPath" ] || mkdir -p "$CfgPath"
CurrentDate=$(date +%F)
ConfigFile=${CfgPath}/default_config.yml
LogFile=${LogPath}/${CurrentDate}.log

set -x
python "${SrcPath}"/party.py -config "${ConfigFile}" -project_dir "${RootPath}" -project_log "${LogFile}" -nums_server 10

python "${SrcPath}"/client.py -config "${ConfigFile}" -project_dir "${RootPath}" -project_log "${LogFile}" -nums_party 5