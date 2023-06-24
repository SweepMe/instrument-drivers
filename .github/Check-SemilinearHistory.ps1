Param(
    [Parameter(Mandatory)]
    [string]$targetBranch,
    [Parameter(Mandatory)]
    [string]$sourceBranch
)

$ErrorActionPreference = 'Stop'

git fetch origin $targetBranch
$commitTarget = git rev-parse "origin/$targetBranch"
git fetch origin $sourceBranch
$commitSource = git rev-parse "origin/$sourceBranch"

# verify that source branch originates from the latest commit of the target branch
# (i.e. a fast-forward merge could be performed)
git merge-base --is-ancestor $commitTarget $commitSource
if ($LASTEXITCODE -ne "0")
{
   throw "Merge would create a non-semilinear history. Please rebase."
}

# the target branch should only contain simple commits and no merges
$numberOfMergeCommits = git rev-list --min-parents=2 --count "${commitTarget}..${commitSource}"
if ($numberOfMergeCommits -ne "0")
{
    Throw "Source Branch contains non-linear history. Please rebase."
}
