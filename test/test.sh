#!/bin/bash

set -o xtrace

msg='required but missing'
interval=2

function assert_code
{
  local code="${1:-$?}"
  local tobe="${2:-0}"
  if [ "$code" != "$tobe" ]; then
    exit 1
  fi
}

function assert_lines
{
  local lines=$(
  wc -l <<EOF
${1:?$msg}
EOF
  )

  if ((lines < ${2:?$msg})); then
    exit 1
  fi
}

function assert_contain
{
  grep "${2:?$msg}" <<EOF
  ${1:?$msg}
EOF
  assert_code
}

function test_clusnode
{
  # Test help
  if ! clusnode -h; then
    return 1
  fi

  # Test list
  local result=$(clusnode list)
  assert_code
  assert_lines "$result" 5


  # Get the node name of the first data line
  local name=$(
  grep -o -E '\bevanc[^ ]*\b' <<EOF | head -n 1
$result
EOF
  )

  # Test show
  if [ -z $name ] || ! clusnode show $name > /dev/null; then
    return 1
  fi
}

function test_clusrun
{
  # Test help
  if ! clusrun -h; then
    return 1
  fi

  # Test list
  local result=$(clusrun list)
  assert_code
  assert_lines "$result" 5

  # Test new
  result=$(clusrun new 'hostname && date' --short)
  assert_code
  assert_lines "$result" 5

  # Get the job id of the first data line
  local id=$(head -n 4 <<EOF | grep -o -E '\b[0-9]+\b' | head -n 1
$result
EOF
  )

  # Test show and cancel
  if [ -z $id ] || ! clusrun show $id --short > /dev/null || ! sleep $interval && clusrun cancel $id; then
    return 1
  fi
}

function test_clusdiag
{
  # Test help
  if ! clusdiag -h; then
    return 1
  fi

  # Test list
  local result=$(clusdiag list)
  assert_code
  assert_lines "$result" 5

  # Test tests
  result=$(clusdiag tests)
  assert_code
  assert_lines "$result" 5
  assert_contain "$result" 'mpi-pingpong'

  # Test new
  result=$(clusdiag new mpi-pingpong --short)
  assert_code
  assert_lines "$result" 5

  # Get the job id of the first data line
  local id=$(head -n 4 <<EOF | grep -o -E '\b[0-9]+\b' | head -n 1
$result
EOF
  )

  # Test show and cancel
  if [ -z $id ] || ! clusdiag show $id --short > /dev/null || ! sleep $interval && clusdiag cancel $id; then
    return 1
  fi
}

test_clusnode && test_clusrun && test_clusdiag
